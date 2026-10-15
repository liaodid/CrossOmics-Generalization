import copy
import pickle
import re
import numpy as np
import pandas as pd
from tqdm import tqdm 
from lamin_utils import logger, colors

import torch
import torch.nn as nn
from torch_geometric.nn import BatchNorm, GCNConv, GATConv, SGConv, LayerNorm, Sequential
from torch_geometric.utils.dropout import dropout_adj
from torch_geometric.transforms import Compose

from rdkit.Chem import AllChem
from getSequence import getseq

from .utils import *
from . import DATA_DIR

import warnings
warnings.filterwarnings("ignore")


class BGRL(nn.Module):
    r"""BGRL architecture for Graph representation learning."""
    def __init__(self, encoder, predictor):
        super().__init__()
        # online network
        self.online_encoder = encoder
        self.predictor = predictor
        # target network
        self.target_encoder = copy.deepcopy(encoder)
        # reinitialize weights
        self.target_encoder.reset_parameters()
        # stop gradient
        for param in self.target_encoder.parameters():
            param.requires_grad = False

    def trainable_parameters(self):
        r"""Returns the parameters that will be updated via an optimizer."""
        return list(self.online_encoder.parameters()) + list(self.predictor.parameters())

    @torch.no_grad()
    def update_target_network(self, mm):
        r"""Performs a momentum update of the target network's weights."""
        assert 0.0 <= mm <= 1.0, "Momentum needs to be between 0.0 and 1.0, got %.5f" % mm
        for param_q, param_k in zip(self.online_encoder.parameters(), self.target_encoder.parameters()):
            param_k.data.mul_(mm).add_(param_q.data, alpha=1. - mm)

    def forward(self, online_x, target_x):
        # forward online network
        online_y = self.online_encoder(online_x)
        # prediction
        online_q = self.predictor(online_y)
        # forward target network
        with torch.no_grad():
            target_y = self.target_encoder(target_x).detach()
        return online_q, target_y
    

class GNN_Encoder(nn.Module):
    """
    GNN encoder for graph node (target) representation learning.
    """
    def __init__(self, layer_sizes, gnn_type='GCN', batchnorm=False, batchnorm_mm=0.99, layernorm=False, weight_standardization=False):
        super().__init__()

        assert batchnorm != layernorm
        assert len(layer_sizes) >= 2
        self.input_size, self.representation_size = layer_sizes[0], layer_sizes[-1]
        self.weight_standardization = weight_standardization

        self.gnn_type = gnn_type
        if gnn_type == 'GCN':
            gnn = GCNConv
        else:
            raise ValueError(f'Invalid GNN type "{gnn_type}".')

        # construct gnn layers
        layers = []
        for in_dim, out_dim in zip(layer_sizes[:-1], layer_sizes[1:]):
            layers.append((gnn(in_dim, out_dim), 'x, edge_index, edge_weight -> x'),)
            if batchnorm:
                layers.append(BatchNorm(out_dim, momentum=batchnorm_mm))
            else:
                layers.append(LayerNorm(out_dim))
            layers.append(nn.PReLU())
        self.model = Sequential('x, edge_index, edge_weight', layers)   ### add edge_weight

    def forward(self, data):
        if self.weight_standardization:
            self.standardize_weights()
        return self.model(data.x, data.edge_index, data.edge_attr)

    def reset_parameters(self):
        self.model.reset_parameters()

    def standardize_weights(self):
        skipped_first_conv = False
        for m in self.model.modules():
            if isinstance(m, GCNConv, GATConv, SGConv):
                if not skipped_first_conv:
                    skipped_first_conv = True
                    continue
                weight = m.lin.weight.data
                var, mean = torch.var_mean(weight, dim=1, keepdim=True)
                weight = (weight - mean) / (torch.sqrt(var + 1e-5))
                m.lin.weight.data = weight
                

class MLP_Predictor(nn.Module):
    """ 
    MLP predictor .
    """
    def __init__(self, input_size, output_size, hidden_size=512):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size, bias=True),
            nn.PReLU(1),
            nn.Linear(hidden_size, output_size, bias=True)
        )
        self.reset_parameters()

    def forward(self, x):
        return self.net(x)

    def reset_parameters(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                m.reset_parameters()


class DropFeatures:
    r"""Drops node features with probability p."""
    def __init__(self, p=None, precomputed_weights=True):
        assert 0. < p < 1., 'Dropout probability has to be between 0 and 1, but got %.2f' % p
        self.p = p

    def __call__(self, data):
        drop_mask = torch.empty((data.x.size(1),), dtype=torch.float32, device=data.x.device).uniform_(0, 1) < self.p
        data.x[:, drop_mask] = 0
        return data

    def __repr__(self):
        return '{}(p={})'.format(self.__class__.__name__, self.p)


class DropEdges:
    r"""Drops edges with probability p."""
    def __init__(self, p, force_undirected=False):
        assert 0. < p < 1., 'Dropout probability has to be between 0 and 1, but got %.2f' % p
        self.p = p
        self.force_undirected = force_undirected

    def __call__(self, data):
        edge_index = data.edge_index
        edge_attr = data.edge_attr if 'edge_attr' in data else None
        edge_index, edge_attr = dropout_adj(edge_index, edge_attr, p=self.p, force_undirected=self.force_undirected)
        data.edge_index = edge_index
        if edge_attr is not None:
            data.edge_attr = edge_attr
        return data

    def __repr__(self):
        return '{}(p={}, force_undirected={})'.format(self.__class__.__name__, self.p, self.force_undirected)


def get_graph_drop_transform(drop_edge_p, drop_feat_p):
    transforms = list()
    # make copy of graph
    transforms.append(copy.deepcopy)
    # drop edges
    if drop_edge_p > 0.:
        transforms.append(DropEdges(drop_edge_p))
    # drop features
    if drop_feat_p > 0.:
        transforms.append(DropFeatures(drop_feat_p))
    return Compose(transforms)


### ================= Compound Encoder ================= ###


class CompoundEncoder(nn.Module):
    """
    Compound encoder
    """
    def __init__(self, embedder, output_dim=128):
        super().__init__()
        self.embedder = embedder
        self.emb_dict = embedder.saved_embs
        emb_dim = self.embedder.emb_dim
        self.linear_layer = nn.Linear(emb_dim, output_dim)

    def trainable_parameters(self):
        return list(self.linear_layer.parameters())

    def forward(self, smiles_list, device):
        if isinstance(smiles_list, str):
            smiles_list = [smiles_list]
        embs = []
        for smiles in smiles_list:
            assert smiles in list(self.emb_dict.keys()), \
                f'{smiles} emb not found! Please get the emb with CompoundEmbedder first!'
            embs.append(self.emb_dict[smiles].reshape(-1))
            # print(emb_dict[smiles].shape)
        embs = torch.tensor(np.array(embs), dtype=torch.float32).to(device)
        # print(embs)
        embs = self.linear_layer(embs)    # [num_sm, output_dim]
        return embs 
    

class CompoundEmbedder_KPGT:
    """
    Compound SMILES representation using KPGT.
    """
    def __init__(self, data_dir):
        super().__init__()
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.saved_embs = {}
        self.emb_dim = 2304
        self.ref_emb_file = os.path.join(data_dir, 'ref_kpgt_embs.pkl')
        # self.load_model()
        self.init_embs_from_saved_pkl()
        
    def init_embs_from_saved_pkl(self):
        if os.path.exists(self.ref_emb_file):
            reps = pd.read_pickle(self.ref_emb_file)
            self.saved_embs.update(reps)
            logger.download(f'Reference KPGT embedding file loaded.')
        else:
            print(f'Reference KPGT embedding file [{self.ref_emb_file}] not found.')
            print(f'A new reference KPGT embedding file will be created.')
            # 创建pkl文件
            with open(self.ref_emb_file, 'wb') as f:
                pickle.dump(self.saved_embs, f)

    def update_saved_pkl(self, new_embs):
        self.saved_embs.update(new_embs)
        with open(self.ref_emb_file, 'wb') as f:
            pickle.dump(self.saved_embs, f)
            logger.success(f'Reference KPGT embedding updated!')

    def dict_to_namespace(self, dict_):
        namespace = argparse.Namespace()
        for key, value in dict_.items():
            setattr(namespace, key, value)
        return namespace

    def load_model(self):
        try:
            from extract_features import extract_features
        except:
            import sys
            sys.path.append('/data/liyiming/Project/UniPert_G2CP/UniPert/data/KPGT/scripts/')
            from preprocess_downstream_dataset import preprocess_dataset
            from extract_features import extract_features
        self.args = self.dict_to_namespace({
            "config": 'base',
            "model_path": "/data/liyiming/Project/UniPert_G2CP/UniPert/data/KPGT/base.pth",
            "data_path": "/data/liyiming/Project/UniPert_G2CP/UniPert/data/KPGT/datasets",
            "dataset": "custom",
            "device": "gpu"  # Add this line to force CPU usage
        })
        logger.success('KPGT embedder loaded.')

    def get_emb_from_smiles(self, smiles):
        # if self.model is None: self.load_model()
        if check_smiles(smiles):
            c_smiles = Chem.CanonSmiles(smiles)
            if smiles in list(self.saved_embs.keys()):
                return {smiles: self.saved_embs[smiles]}
            elif c_smiles in list(self.saved_embs.keys()):
                self.saved_embs.update({smiles: self.saved_embs[c_smiles]})
                return {smiles: self.saved_embs[c_smiles]}
            else:
                # unimol_emb = self.model.get_repr(smiles, return_atomic_reprs=True)['cls_repr']
                # unimol_emb = np.array(unimol_emb).reshape(-1)
                # self.saved_embs.update({c_smiles: unimol_emb, smiles: unimol_emb})
                # return {smiles: unimol_emb}
                logger.warning(f'KPGT embedding for {smiles} not found!')
        else:
            return None
            
    def get_emb_from_smiles_list(self, smiles_list, save=False):
        out_embs = {}
        for smiles in tqdm(smiles_list):
            emb = self.get_emb_from_smiles(smiles)
            if emb is not None:
                out_embs.update(emb)
        if save:self.update_saved_pkl(out_embs)
        return out_embs


class CompoundEmbedder_UniMol:
    """
    Compound SMILES representation using Uni-Mol.
    """
    def __init__(self, data_dir):
        super().__init__()
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.saved_embs = {}
        self.emb_dim = 512
        self.ref_emb_file = os.path.join(data_dir, 'ref_unimol_embs.pkl')
        # self.load_model()
        self.init_embs_from_saved_pkl()
        
    def init_embs_from_saved_pkl(self):
        if os.path.exists(self.ref_emb_file):
            reps = pd.read_pickle(self.ref_emb_file)
            self.saved_embs.update(reps)
            logger.download(f'Reference UniMol embedding file loaded.')
        else:
            print(f'Reference UniMol embedding file [{self.ref_emb_file}] not found.')
            print(f'A new reference UniMol embedding file will be created.')
            # 创建pkl文件
            with open(self.ref_emb_file, 'wb') as f:
                pickle.dump(self.saved_embs, f)

    def update_saved_pkl(self, new_embs):
        self.saved_embs.update(new_embs)
        with open(self.ref_emb_file, 'wb') as f:
            pickle.dump(self.saved_embs, f)
            logger.success(f'Reference UniMol embedding updated!')

    def load_model(self):
        try:
            from unimol_tools import UniMolRepr
        except:
            import sys
            sys.path.append('/data/liyiming/Project/UniPert_G2CP/UniPert/data/Uni-Mol/unimol_tools')
            from unimol_tools import UniMolRepr
        self.model = UniMolRepr(data_type='molecule', remove_hs=False)
        logger.success('UniMol embedder loaded.')

    def get_emb_from_smiles(self, smiles):
        # if self.model is None: self.load_model()
        if check_smiles(smiles):
            c_smiles = Chem.CanonSmiles(smiles)
            if smiles in list(self.saved_embs.keys()):
                return {smiles: self.saved_embs[smiles]}
            elif c_smiles in list(self.saved_embs.keys()):
                self.saved_embs.update({smiles: self.saved_embs[c_smiles]})
                return {smiles: self.saved_embs[c_smiles]}
            else:
                unimol_emb = self.model.get_repr(smiles, return_atomic_reprs=True)['cls_repr']
                unimol_emb = np.array(unimol_emb).reshape(-1)
                self.saved_embs.update({c_smiles: unimol_emb, smiles: unimol_emb})
                return {smiles: unimol_emb}
        else:
            return None
            
    def get_emb_from_smiles_list(self, smiles_list, save=False):
        out_embs = {}
        for smiles in tqdm(smiles_list):
            emb = self.get_emb_from_smiles(smiles)
            if emb is not None:
                out_embs.update(emb)
        if save:self.update_saved_pkl(out_embs)
        return out_embs
    

class CompoundEmbedder_ECFP4:
    """
    Compound SMILES representation using ECFP4.
    """
    def __init__(self, data_dir):
        super().__init__()
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.saved_embs = {}
        self.emb_dim = 2048
        self.ref_emb_file = os.path.join(data_dir, 'ref_ecfp4_embs.pkl')
        self.init_embs_from_saved_pkl()
        logger.success('ECFP4 embedder loaded.')

    def init_embs_from_saved_pkl(self):
        if os.path.exists(self.ref_emb_file):
            reps = pd.read_pickle(self.ref_emb_file)
            self.saved_embs.update(reps)
        else:
            print(f'Reference ECFP4 embedding file [{self.ref_emb_file}] not found.')
            print(f'A new reference ECFP4 embedding file will be created.')
            # 创建pkl文件
            with open(self.ref_emb_file, 'wb') as f:
                pickle.dump(self.saved_embs, f)

    def update_saved_pkl(self, new_embs):
        self.saved_embs.update(new_embs)
        with open(self.ref_emb_file, 'wb') as f:
            pickle.dump(self.saved_embs, f)
            logger.success(f'Reference ECFP4 embedding updated!')

    def get_emb_from_smiles(self, smiles):
        if check_smiles(smiles):
            c_smiles = Chem.CanonSmiles(smiles)
            if smiles in list(self.saved_embs.keys()):
                return {smiles: self.saved_embs[smiles]}
            elif c_smiles in list(self.saved_embs.keys()):
                self.saved_embs.update({smiles: self.saved_embs[c_smiles]})
                return {smiles: self.saved_embs[c_smiles]}
            else:
                mol = Chem.MolFromSmiles(smiles)
                ecfp4_emb = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
                ecfp4_emb = np.array(ecfp4_emb, dtype=float)  
                self.saved_embs.update({c_smiles: ecfp4_emb, smiles: ecfp4_emb})
                return {smiles: ecfp4_emb}
        else:
            return None
            
    def get_emb_from_smiles_list(self, smiles_list, save=False):
        out_embs = {}
        for smiles in tqdm(smiles_list):
            emb = self.get_emb_from_smiles(smiles)
            if emb is not None:
                out_embs.update(emb)
        if save: self.update_saved_pkl(out_embs)
        return out_embs
    
    def get_bulk_emb_from_smiles_list(self, smiles_list, save=False):
        from concurrent.futures import ProcessPoolExecutor, as_completed
        out_embs = {}
        total_tasks = len(smiles_list)
        cpu_cores = os.cpu_count() or 1
        if total_tasks>0:
            logger.info(f'Using {cpu_cores} cores to generate ECFP4 embeddings.')
            with ProcessPoolExecutor(max_workers=cpu_cores) as executor:
                with tqdm(total=total_tasks, desc="Processing") as pbar:
                    futures = {executor.submit(compound_worker, self, smiles): smiles for smiles in smiles_list}
                    for future in as_completed(futures):
                        smiles = futures[future]
                        try:
                            partial_out_embs, key = future.result()
                            if key is not None:
                                out_embs.update(partial_out_embs)
                            pbar.update(1)  
                        except Exception as exc:
                            logger.error(f'{smiles} generated an exception: {exc}')
                            pbar.update(1) 
            logger.success(f'ECFP4 embeddings with {len(out_embs)} queries generated.')
            if save:self.update_saved_pkl(out_embs)
        return out_embs

### ================= Target Encoder ================= ###

class TargetEncoder(nn.Module):
    """
    Target encoder
    """
    def __init__(self, embedder, output_dim=128):
        super().__init__()
        self.embedder = embedder
        self.emb_dict = embedder.saved_embs
        emb_dim = embedder.emb_dim
        self.linear_layer = nn.Linear(emb_dim, output_dim)

    def trainable_parameters(self):
        return list(self.linear_layer.parameters())

    def forward(self, tgt_list, device):
        if isinstance(tgt_list, str):
            tgt_list = [tgt_list]
        embs = []
        for tgt in tgt_list:
            assert tgt in list(self.emb_dict.keys()), \
                f'{tgt} emb not found! Please get the emb with TargetEmbedder first!'
            embs.append(self.emb_dict[tgt].reshape(-1))
        embs = torch.tensor(np.array(embs), dtype=torch.float32).to(device)
        embs = self.linear_layer(embs)    
        return embs   


class TargetEmbedder_PseAAC:
    """
    Protein sequence representation using PseAAC.
    """
    def __init__(self, data_dir=DATA_DIR, lamda=24):
        super().__init__()
        self.data_dir = data_dir
        self.saved_embs = {}
        self.lamda = lamda
        self.emb_dim = 20+2*self.lamda
        self.ref_emb_file = os.path.join(data_dir, 'ref_pseaac_embs.pkl')
        self.ref_fasta_file = os.path.join(data_dir, 'ref_target_seq.fasta')
        self.model = None
        self.load_model()
        self.init_embs_from_saved_pkl()
        logger.success('PseAAC embedder loaded.')
    
    def load_model(self):
        from propy.PseudoAAC import GetAPseudoAAC
        self.model = GetAPseudoAAC
        logger.success('PseAAC model loaded.')

    def update_saved_pkl(self, new_embs):
        self.saved_embs.update(new_embs)
        with open(self.ref_emb_file, 'wb') as f:
            pickle.dump(self.saved_embs, f)
            logger.success(f'Reference PseAAC embeddings updated.')

    def init_embs_from_saved_pkl(self):
        # load saved pkl, or create new one from ref fasta
        if os.path.exists(self.ref_emb_file):
            ref_embs = pd.read_pickle(self.ref_emb_file)
            self.saved_embs.update(ref_embs)
            logger.download(f'Reference PseAAC embedding file loaded.')
        else:
            logger.warning(f'Reference PseAAC embedding file [{self.ref_emb_file}] not found.') 
            logger.info(f'A new reference PseAAC embedding file will be created.')
            ref_embs = self.get_bulk_embs_from_fasta(self.ref_fasta_file)
            self.update_saved_pkl(ref_embs)

    def update_genome_wide_embs(self, save=False):
        out_embs = {}
        tgt_ptbg_info_file = os.path.join(self.data_dir, 'target_info_HGNC_id_19321_with_labels.csv')
        df = pd.read_csv(tgt_ptbg_info_file).dropna(subset=['Approved symbol', 'UniProt accession']).loc[:, ['Approved symbol', 'UniProt accession']].drop_duplicates()
        mapping_dict = dict(zip(df['Approved symbol'], df['UniProt accession']))
        for gene_symbol, uniprot_id in mapping_dict.items():
                if uniprot_id in list(self.saved_embs.keys()):
                    out_embs.update({gene_symbol: self.saved_embs[uniprot_id]})
        if save: self.update_saved_pkl(out_embs)
        return out_embs
    
    def get_emb_from_seq(self, seq):
        seq = ''.join([aa for aa in seq if aa in "ARNDCQEGHILKMFPSTWYV"])
        if len(seq) < self.lamda:
            logger.warning(f'Sequence should over {self.lamda} for PseAAC generating.')
            return None
        else:
            try:
                apaac = np.array(list(self.model(seq, self.lamda).values()), dtype=float)
                return apaac
            except:
                return None
        
    def get_emb_from_gene_symbol(self, gene):
        # gene = gene.upper()
        if gene in list(self.saved_embs.keys()):
            return {gene: self.saved_embs[gene]}      
        elif gene.upper() in list(self.saved_embs.keys()):
            return {gene: self.saved_embs[gene.upper()]}   
        else:
            logger.print(f'Retrieving sequence for {gene} ...')
            try:
                pro_seq = getseq('9606+'+gene, just_sequence=True)
            except:
                logger.warning(f'No sequence found for {gene}.')
                return None
            emb = self.get_emb_from_seq(pro_seq)
            if emb is None:
                logger.warning(f'Cannot get embedding for [{gene}].')
                return None
            # self.saved_embs.update({gene: emb})
            return {gene: emb}

    def get_emb_from_gene_symbol_list(self, gene_list, save=False):
        gene_list = list(set(gene_list))
        out_embs = {}
        for gene in gene_list:
            emb = self.get_emb_from_gene_symbol(gene)
            if emb is not None:
                out_embs.update(emb)
        logger.success(f'PseAAC embeddings with {len(out_embs)} querys generated.')
        if save: self.update_saved_pkl(out_embs)
        return out_embs
    
    def get_emb_from_uniprot_id(self, uniprot_id):
        uniprot_id = uniprot_id.upper()
        if uniprot_id not in list(self.saved_embs.keys()):
            logger.print(f'Retrieving sequence for {uniprot_id} ...')
            try:
                pro_seq = getseq(uniprot_id, uniprot_id=True, just_sequence=True)
            except:
                logger.warning(f'No sequence found for {uniprot_id}')
                return None
            emb = self.get_emb_from_seq(pro_seq)
            if emb is None:
                logger.warning(f'Cannot get PseAAC embedding for [{uniprot_id}].')
                return None
            # self.saved_embs.update({uniprot_id: emb})
            return {uniprot_id: emb}
        else:
            return {uniprot_id: self.saved_embs[uniprot_id]}
    
    def get_emb_from_uniprot_id_list(self, uid_list, save=False):
        uid_list = list(set(uid_list))
        out_embs = {}
        for uid in uid_list:
            emb = self.get_emb_from_uniprot_id(uid)
            if emb is not None:
                out_embs.update(emb)
        logger.success(f'PseAAC embeddings with {len(out_embs)} querys generated.')
        if save: self.update_saved_pkl(out_embs)
        return out_embs

    def get_embs_from_fasta(self, fasta_file, save=False):
        dataset = FastaBatchedDataset.from_file(fasta_file)
        out_embs = {}
        
        for header, seq in tqdm(dataset):  
            if 'PN=' in header:      # pert name as key
                pn = header.split('PN=')[1].split(' ')[0]
                emb = self.get_emb_from_seq(seq)
                out_embs.update({pn: emb})  
            elif '|' in header:      
                uniprot_id = header.split('|')[1].split(' ')[0]  
                if uniprot_id in list(self.saved_embs.keys()): 
                    out_embs.update({uniprot_id: self.saved_embs[uniprot_id]}) 
                else:
                    emb = self.get_emb_from_seq(seq) 
                    out_embs.update({uniprot_id: emb})
            else:
                emb = self.get_emb_from_seq(seq)
                out_embs.update({header: emb}) 
        logger.success(f'PseAAC embeddings with {len(out_embs)} querys generated.')
        if save: self.update_saved_pkl(out_embs)
        return out_embs
   
    def get_bulk_embs_from_fasta(self, fasta_file, save=False):
        from concurrent.futures import ProcessPoolExecutor, as_completed
        dataset = FastaBatchedDataset.from_file(fasta_file)
        out_embs = {}
        total_tasks = len(list(dataset))

        cpu_cores = os.cpu_count() or 1
        logger.info(f'Using {cpu_cores} cores to generate PseAAC embeddings.')
        with ProcessPoolExecutor(max_workers=cpu_cores) as executor:
            with tqdm(total=total_tasks, desc="Processing") as pbar:
                futures = {executor.submit(target_worker, self, header, seq): header for header, seq in dataset}
                for future in as_completed(futures):
                    header = futures[future]
                    try:
                        partial_out_embs, key = future.result()
                        if key is not None:
                            out_embs.update(partial_out_embs)
                        pbar.update(1)  
                    except Exception as exc:
                        logger.error(f'{header} generated an exception: {exc}')
                        pbar.update(1) 

        logger.success(f'PseAAC embeddings with {len(out_embs)} queries generated.')
        if save:self.update_saved_pkl(out_embs)
        return out_embs


class TargetEmbedder_ESM2:
    """
    Protein sequence representation using ESM2.
    """
    def __init__(self, data_dir=DATA_DIR):
        super().__init__()
        self.data_dir = data_dir
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.model, self.alphabet = None, None
        self.saved_embs = {}
        self.emb_dim = 1280
        self.ref_emb_file = os.path.join(data_dir, 'ref_esm2_embs.pkl')
        self.ref_fasta_file = os.path.join(data_dir, 'ref_target_seq.fasta')
        self.model = None
        self.load_model()
        self.init_embs_from_saved_pkl()
        logger.success('ESM2 embedder created.')

    def load_model(self):
        from esm import pretrained
        self.model, self.alphabet = pretrained.load_model_and_alphabet('esm2_t33_650M_UR50D')
        self.model.full() if self.device=='cpu' else self.model.half()
        self.model = self.model.to(self.device)
        logger.success('ESM2 model loaded.')

    def update_saved_pkl(self, new_embs):
        self.saved_embs.update(new_embs)
        with open(self.ref_emb_file, 'wb') as f:
            pickle.dump(self.saved_embs, f)
            logger.success(f'ref_esm2_embs.pkl updated.')
            return

    def init_embs_from_saved_pkl(self):
        # load saved pkl, or create new one from ref fasta
        if os.path.exists(self.ref_emb_file):
            ref_reps = pd.read_pickle(self.ref_emb_file)
            self.saved_embs.update(ref_reps)
            logger.download(f'Reference ESM2 embedding file loaded.')
        else:
            logger.warning(f'Reference ESM2 embedding file [{self.ref_emb_file}] not found.') 
            logger.info(f'A new reference ESM2 embedding file will be created.')
            ref_reps = self.get_embs_from_fasta(self.ref_fasta_file)
            self.update_saved_pkl(ref_reps)

    def update_genome_wide_embs(self, save=False):
        out_embs = {}
        tgt_ptbg_info_file = os.path.join(self.data_dir, 'target_info_HGNC_id_19321_with_labels.csv')
        df = pd.read_csv(tgt_ptbg_info_file).dropna(subset=['Approved symbol', 'UniProt accession']).loc[:, ['Approved symbol', 'UniProt accession']].drop_duplicates()
        mapping_dict = dict(zip(df['Approved symbol'], df['UniProt accession']))
        for gene_symbol, uniprot_id in mapping_dict.items():
                if uniprot_id in list(self.saved_embs.keys()):
                    out_embs.update({gene_symbol: self.saved_embs[uniprot_id]})
        if save: self.update_saved_pkl(out_embs)
        return out_embs

    def get_emb_from_seq(self, seq):
        seq = seq[:5000]   # max length of esm input sequence set to 5000
        with torch.no_grad():   
            toks = torch.tensor([self.alphabet.get_idx(i) for i in seq]).reshape(1, -1)
            toks = toks.to(self.device, non_blocking=True)
            out = self.model(toks, repr_layers=[33], return_contacts=False)
            token_reps = out["representations"][33].mean(1).reshape(-1).detach().cpu().numpy()
        return token_reps
 
    def get_emb_from_gene_symbol(self, gene):
        # gene = gene.upper()
        if gene in list(self.saved_embs.keys()):
            return {gene: self.saved_embs[gene]}    
        elif gene.upper() in list(self.saved_embs.keys()):
            return {gene: self.saved_embs[gene.upper()]}     
        else:
            logger.print(f'Retrieving sequence for {gene} ...')
            try:
                pro_seq = getseq(gene, just_sequence=True)
            except:
                logger.warning(f'No sequence found for {gene}.')
                return None
            out_rep = self.get_emb_from_seq(pro_seq)
            # self.saved_embs.update({gene: out_rep})
            return {gene: out_rep}

    def get_emb_from_gene_symbol_list(self, gene_list, save=False):
        gene_list = list(set(gene_list))
        out_embs = {}
        for gene in gene_list:
            emb = self.get_emb_from_gene_symbol(gene)
            if emb is not None:
                out_embs.update(emb)
        logger.success(f'ESM2 embeddings with {len(out_embs)} querys generated.')
        if save: self.update_saved_pkl(out_embs)
        return out_embs
    
    def get_emb_from_uniprot_id(self, uniprot_id):
        uniprot_id = uniprot_id.upper()
        if uniprot_id not in list(self.saved_embs.keys()):
            logger.print(f'Retrieving sequence for {uniprot_id} ...')
            try:
                pro_seq = getseq(uniprot_id, uniprot_id=True, just_sequence=True)
            except:
                logger.warning(f'No sequence found for {uniprot_id}.')
                return None
            out_rep = self.get_emb_from_seq(pro_seq)
            # self.saved_embs.update({uniprot_id: out_rep})
            return {uniprot_id: out_rep}
        else:
            return {uniprot_id: self.saved_embs[uniprot_id]}
    
    def get_emb_from_uniprot_id_list(self, uid_list, save=False):
        uid_list = list(set(uid_list))
        out_embs = {}
        for uid in uid_list:
            emb = self.get_emb_from_uniprot_id(uid)
            if emb is not None:
                out_embs.update(emb)
        logger.success(f'ESM2 embeddings with {len(out_embs)} querys generated.')
        if save: self.update_saved_pkl(out_embs)
        return out_embs

    def get_embs_from_fasta(self, fasta_file, save=False):
        dataset = FastaBatchedDataset.from_file(fasta_file)
        out_embs = {}
        for header, seq in tqdm(dataset):  
            emb = self.get_emb_from_seq(seq)
            if 'PN=' in header:      # pert name as key
                pn = header.split('PN=')[1]
                out_embs.update({pn: emb})  
            if '|' in header:      
                uniprot_id = header.split('|')[1].split(' ')[0]  
                if uniprot_id in list(self.saved_embs.keys()): 
                    out_embs.update({uniprot_id: emb}) 
                else:
                    emb = self.get_emb_from_seq(seq) 
                    out_embs.update({uniprot_id: emb})
            if ('PN=' not in header) and ('|' not in header):
                out_embs.update({header: emb}) 

            # if 'PN=' in header:      # pert name as key
            #     pn = header.split('PN=')[1].split(' ')[0]
            #     emb = self.get_emb_from_seq(seq)
            #     out_embs.update({pn: emb})  
            # elif '|' in header:      
            #     uniprot_id = header.split('|')[1].split(' ')[0]  
            #     if uniprot_id in list(self.saved_embs.keys()): 
            #         out_embs.update({uniprot_id: self.saved_embs[uniprot_id]}) 
            #     else:
            #         emb = self.get_emb_from_seq(seq) 
            #         out_embs.update({uniprot_id: emb})
            # else:
            #     emb = self.get_emb_from_seq(seq)
            #     out_embs.update({header: emb})
             
        logger.success(f'ESM2 embeddings with {len(out_embs)} querys generated.')
        if save: self.update_saved_pkl(out_embs)
        return out_embs


class TargetEmbedder_OntoProtein:
    """
    Protein sequence representation using OntoProtein.
    """
    def __init__(self, data_dir=DATA_DIR, model_dir="/data/liyiming/Project/UniPert_G2CP/UniPert/data/OntoProtein_model"):
        super().__init__()
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.model, self.tokenizer = None, None
        self.saved_embs = {}
        self.emb_dim = 1024
        self.ref_emb_file = os.path.join(data_dir, 'ref_ontoprotein_embs.pkl')
        self.ref_fasta_file = os.path.join(data_dir, 'ref_target_seq.fasta')
        self.model = None
        self.load_model()
        self.init_embs_from_saved_pkl()
        logger.success('OntoProtein embedder loaded.')

    def load_model(self):
        from transformers import AutoTokenizer, AutoModelForMaskedLM
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("zjunlp/OntoProtein")
            self.model = AutoModelForMaskedLM.from_pretrained("zjunlp/OntoProtein").to(self.device)    
        except:
            logger.warning('Failed to load OntoProtein model. Try to download the model from local.')
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
                self.model = AutoModelForMaskedLM.from_pretrained(self.model_dir).to(self.device)
            except:
                logger.error('Failed to load OntoProtein model from local. Try to download from remote.')

        self.model.eval()
        self.model.full() if self.device=='cpu' else self.model.half()
        logger.success(f'OntoProtein model loaded.')

    def update_saved_pkl(self, new_embs):
        self.saved_embs.update(new_embs)
        with open(self.ref_emb_file, 'wb') as f:
            pickle.dump(self.saved_embs, f)
            logger.success(f'Reference OntoProtein embedding updated!')
            return

    def init_embs_from_saved_pkl(self):
        # load saved pkl, or create new one from ref fasta
        if os.path.exists(self.ref_emb_file):
            ref_reps = pd.read_pickle(self.ref_emb_file)
            self.saved_embs.update(ref_reps)
            logger.download(f'Reference OntoProtein embedding file loaded.')
        else:
            logger.warning(f'Reference OntoProtein embedding file [{self.ref_emb_file}] not found.') 
            logger.info(f'A new reference OntoProtein embedding file will be created.')
            # create new one
            ref_embs = self.get_embs_from_fasta(self.ref_fasta_file)
            self.update_saved_pkl(ref_embs)

    def update_genome_wide_embs(self, save=False):
        out_embs = {}
        tgt_ptbg_info_file = os.path.join(self.data_dir, 'target_info_HGNC_id_19321_with_labels.csv')
        df = pd.read_csv(tgt_ptbg_info_file).dropna(subset=['Approved symbol', 'UniProt accession']).loc[:, ['Approved symbol', 'UniProt accession']].drop_duplicates()
        mapping_dict = dict(zip(df['Approved symbol'], df['UniProt accession']))
        for gene_symbol, uniprot_id in mapping_dict.items():
                if uniprot_id in list(self.saved_embs.keys()):
                    out_embs.update({gene_symbol: self.saved_embs[uniprot_id]})
        if save: self.update_saved_pkl(out_embs)
        return out_embs

    def get_emb_from_seq(self, seq):
        if self.model is None:
            print('Loading OntoProtein model...')
            self.load_model()
            print('OntoProtein model loaded!')
        seq = seq[:6000]   # max length of input sequence is 6000
        seq = " ".join(list(re.sub(r"[UZOB]", "X", seq)))
        ids = self.tokenizer.batch_encode_plus([seq], add_special_tokens=True, padding="longest")
        input_ids = torch.tensor(ids['input_ids']).to(self.device)
        attention_mask = torch.tensor(ids['attention_mask']).to(self.device)
        with torch.no_grad():   
            emb = self.model(input_ids=input_ids, attention_mask=attention_mask, output_hidden_states=True)
            emb = emb.hidden_states[-1][0].mean(dim=0).detach().cpu().numpy()
        return emb
 
    def get_emb_from_gene_symbol(self, gene):
        # gene = gene.upper()
        if gene in list(self.saved_embs.keys()):
            return {gene: self.saved_embs[gene]}      
        elif gene.upper() in list(self.saved_embs.keys()):
            return {gene: self.saved_embs[gene.upper()]}   
        else:
            logger.print(f'Retrieving sequence for {gene} ...')
            try:
                pro_seq = getseq(gene, just_sequence=True)
            except:
                logger.warning(f'No sequence found for {gene}.')
                return None
            out_rep = self.get_emb_from_seq(pro_seq)
            # self.saved_embs.update({gene: out_rep})
            return {gene: out_rep}

    def get_emb_from_gene_symbol_list(self, gene_list, save=False):
        gene_list = list(set(gene_list))
        out_embs = {}
        for gene in gene_list:
            emb = self.get_emb_from_gene_symbol(gene)
            if emb is not None:
                out_embs.update(emb)
        logger.success(f'OntoProtein embeddings with {len(out_embs)} querys generated.')
        if save: self.update_saved_pkl(out_embs)
        return out_embs
    
    def get_emb_from_uniprot_id(self, uniprot_id):
        uniprot_id = uniprot_id.upper()
        if uniprot_id not in list(self.saved_embs.keys()):
            print(f'Retrieving sequence for {uniprot_id} ...')
            try:
                pro_seq = getseq(uniprot_id, uniprot_id=True, just_sequence=True)
            except:
                logger.warning(f'No sequence found for {uniprot_id}.')
                return None
            out_rep = self.get_embs_from_seq(pro_seq)
            # self.saved_embs.update({uniprot_id: out_rep})
            return {uniprot_id: out_rep}
        else:
            return {uniprot_id: self.saved_embs[uniprot_id]}
    
    def get_emb_from_uniprot_id_list(self, uid_list, save=False):
        uid_list = list(set(uid_list))
        out_embs = {}
        for uid in uid_list:
            emb = self.get_emb_from_uniprot_id(uid)
            if emb is not None:
                out_embs.update(emb)
        logger.success(f'OntoProtein embeddings with {len(out_embs)} querys generated.')
        if save: self.update_saved_pkl(out_embs)
        return out_embs

    def get_embs_from_fasta(self, fasta_file, save=False):
        dataset = FastaBatchedDataset.from_file(fasta_file)
        out_embs = {}
        for header, seq in tqdm(dataset):  
            if 'PN=' in header:      # pert name as key
                pn = header.split('PN=')[1]
                emb = self.get_emb_from_seq(seq)
                out_embs.update({pn: emb})  
            if '|' in header:      
                uniprot_id = header.split('|')[1].split(' ')[0]  
                if uniprot_id in list(self.saved_embs.keys()): 
                    out_embs.update({uniprot_id: emb}) 
                else:
                    emb = self.get_emb_from_seq(seq) 
                    out_embs.update({uniprot_id: emb})
            if ('PN=' not in header) and ('|' in header):
                out_embs.update({header: emb}) 

            # if 'PN=' in header:      # pert name as key
            #     pn = header.split('PN=')[1].split(' ')[0]
            #     emb = self.get_emb_from_seq(seq)
            #     out_embs.update({pn: emb})  
            # elif '|' in header:      
            #     uniprot_id = header.split('|')[1].split(' ')[0]  
            #     if uniprot_id in list(self.saved_embs.keys()): 
            #         out_embs.update({uniprot_id: self.saved_embs[uniprot_id]}) 
            #     else:
            #         emb = self.get_emb_from_seq(seq) 
            #         out_embs.update({uniprot_id: emb})
            # else:
            #     emb = self.get_emb_from_seq(seq)
            #     out_embs.update({header: emb}) 
                
        logger.success(f'OntoProtein embeddings with {len(out_embs)} querys generated.')
        if save: self.update_saved_pkl(out_embs)
        return out_embs
    

def compound_worker(cls_instance, smiles):
    emb = cls_instance.get_emb_from_smiles(smiles)
    if emb is not None:
        return {smiles: emb}, smiles
    else:
        return {}, None 


def target_worker(cls_instance, header, seq):
    emb = cls_instance.get_emb_from_seq(seq)
    if emb is not None:
        # 根据header类型更新结果字典
        if 'PN=' in header:
            key = header.split('PN=')[1]
        elif '|' in header:
            key = header.split('|')[1].split(' ')[0]
        else:
            key = header
        return {key: emb}, key 
    else:
        return {}, None 