import time
import pickle
import subprocess
import anndata
import pandas as pd
from tqdm import tqdm
from typing import List, Optional
from collections import defaultdict
from lamin_utils import logger, colors

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from torch_geometric.data import Data 
from torch_geometric.utils import add_self_loops, to_undirected
import itertools

from .ctcloss import CTCLoss
from .dataset import CTPairDataset
from .modules import *
from .utils import *
from . import DATA_DIR, SAVE_DIR, MODEL_DIR, MMSEQS_CACHE_DIR



class UniPert:
    def __init__(self, data_dir=DATA_DIR, model_hparams = {'save_dir': MODEL_DIR}, device=None):
        ### data
        self.data_dir = data_dir
        self.mmseqs_cache_dir = str(MMSEQS_CACHE_DIR)
        if device == 'cpu':
            self.device = torch.device('cpu')
        elif device is not None and isinstance(device, str) and device[:4] == 'cuda' and torch.cuda.is_available():
            self.device = torch.device(device)
        else:
            self.device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
            
        ### mmseqs tool
        self.client = None

        ### compound search service
        self.cp_server = None

        # ref target graph info
        self.ref_target_seq_file = os.path.join(data_dir, 'ref_target_seq.fasta')
        self.ref_target_sim_file = os.path.join(data_dir, 'ref_target_seq_similarity.csv')
        self.ref_target = None
        self.ref_target_sim = None
        self.ref_target_graph = None
        # custom target graph info
        self.custom_target_seq_file = os.path.join(data_dir, 'custom_target_seq.fasta')
        self.custom_target_sim_file = os.path.join(data_dir, 'custom_target_seq_similarity.csv')
        self.custom_target = None
        self.custom_target_sim = None
        self.custom_target_graph = None
        self.custom_target_ui2pn = defaultdict(list)     # {UniProt_id: [perturbagen_names]}
        # ref-custom target graph node id mapping 
        self.node_name2id = None
        # custom compound info
        self.custom_compound_smiles_file = os.path.join(data_dir, 'custom_compound_smiles.txt')

        ### check if model already trained at given path, construct model
        self.loaded = False
        if model_hparams is None: model_hparams = {} 
        if ('save_dir' in model_hparams.keys()) and (os.path.exists(model_hparams['save_dir'])):
            logger.info(colors.yellow(f"Model have already trained at {model_hparams['save_dir']}. "))
            self.load_models(save_dir=model_hparams['save_dir'], device=self.device)
            self.loaded = True
        else:
            self.set_model_hyperparams(model_hparams)
            self.unipert_models = self.construct_model()

        ### prepare ref graph  
        self.prepare_ref_target_graph(graph_type=self.graph_type) 
        
        ### saved unipert representations
        self.unipert_reps = {}    


    def set_model_hyperparams(self, params=None):
        # model hyperparameters
        self.save_dir = SAVE_DIR
        self.model_hparams = {
            'version': 'v1',
            'out_dim': 256,
            'gnn_type': 'GCN',
            'layer_num': 2,
            'graph_type': 'weighted_directed',
            'target_embedder': 'ESM2',
            'compound_embedder': 'ECFP4',
        }
        if params:self.model_hparams.update(params)
        logger.info(colors.yellow(f"UniPert model hyperparameters settings:"))
        for key, value in self.model_hparams.items():
            setattr(self, key, value)
        #     logger.print(f"    {key}: {value}")
        self.model_path = os.path.join(self.save_dir, 'unipert_model.pt')


    def set_train_hyperparams(self, params=None):
        self.training_data = os.path.join(self.data_dir, 'processed_pubchem_CPI_24Jan_cid8533_ua4250_i53963.csv')
        # training hyperparameters
        self.train_hparams = {
            'exp_name': 'UniPert_standard',
            'seed': 2024,
            'bs': 512,
            'epochs1': 1000,  
            'epochs2': 1000,  
            'lr1': 5e-3,   
            'lr2': 5e-3,   
            'wd': 1e-5,
            'mm': 0.99,     
            'drop_edge_p_1': 0.1,
            'drop_feat_p_1': 0.3,
            'drop_edge_p_2': 0.3,
            'drop_feat_p_2': 0.1,
            'accumulation_steps': 1,
            }
        if params:self.train_hparams.update(params)
        exp_time = time.time()
        exp_time = time.strftime("%Y%m%d-%H%M%S", time.localtime(exp_time))
        self.train_hparams['exp_time'] = exp_time
        if 'save_dir' in self.train_hparams.keys():
            self.train_hparams['save_dir'] = self.train_hparams['save_dir'].replace('/fionafyang/lynnymli/', '/data/liyiming/Project/UniPert_G2CP/')
            self.train_hparams['save_dir'] = os.path.join(self.train_hparams['save_dir'], self.train_hparams['exp_name'])
        else:
            self.train_hparams['save_dir'] = os.path.join(self.save_dir, self.train_hparams['exp_name'])
        logger.info(colors.yellow(f"UniPert model training hyperparameters settings:"))
        logger.print(f"    device: {self.device}")
        for key, value in self.train_hparams.items():
            setattr(self, key, value)
            logger.print(f"    {key}: {value}")
        self.model_path = os.path.join(self.save_dir, 'unipert_model.pt')
        

    def construct_model(self):
        logger.info(colors.yellow(f"Constructing UniPert model..."))
        ### prepare embedders
        # target
        if self.model_hparams['target_embedder'] == 'ESM2':
            self.tgt_embedder = TargetEmbedder_ESM2(self.data_dir)
        elif self.model_hparams['target_embedder'] == 'OntoProtein':
            self.tgt_embedder = TargetEmbedder_OntoProtein(self.data_dir)
        elif self.model_hparams['target_embedder'] == 'PseAAC':
            self.tgt_embedder = TargetEmbedder_PseAAC(self.data_dir)
        else:
            logger.error(f"model_hparams['target_embedder'] value error, should be one of ['ESM2',  'OntoProtein', 'PseAAC'].")
            raise ValueError(f"Unsupport value of {self.model_hparams['target_embedder']} for model_hparams['target_embedder'].")
        # compound
        if self.model_hparams['compound_embedder'] == 'UniMol':
            self.cp_embedder = CompoundEmbedder_UniMol(data_dir=self.data_dir)
        elif self.model_hparams['compound_embedder'] == 'ECFP4':
            self.cp_embedder = CompoundEmbedder_ECFP4(data_dir=self.data_dir)
        elif self.model_hparams['compound_embedder'] == 'KPGT':
            self.cp_embedder = CompoundEmbedder_KPGT(data_dir=self.data_dir)
        else:
            logger.error(f"model_hparams['compound_embedder'] value error, should be one of ['UniMol', 'ECFP4', 'KPGT'].")
            raise ValueError(f"Unsupport value of {self.model_hparams['compound_embedder']} for model_hparams['compound_embedder'].")
        self.tgt_embs = None
        self.cp_embs = None

        ### prepare unipert model
        self.cp_model = CompoundEncoder(embedder=self.cp_embedder, output_dim=self.out_dim)
        # target model
        self.tgt_encoder = GNN_Encoder(layer_sizes=[self.tgt_embedder.emb_dim]+[self.out_dim]*self.layer_num, gnn_type=self.gnn_type, batchnorm=True)
        self.tgt_predictor = MLP_Predictor(self.out_dim, self.out_dim, hidden_size=self.out_dim*4)
        self.tgt_model = BGRL(self.tgt_encoder, self.tgt_predictor)
        # alignment model
        self.align_model = CTCLoss()
        
        unipert_models = nn.ModuleList([])
        unipert_models.append(self.cp_model)
        unipert_models.append(self.tgt_model)
        unipert_models.append(self.align_model)

        logger.success(colors.green(f"UniPert model constructed."))
        return unipert_models


    def prepare_mmseqs(self, storage_directory):
        """
        Prepare the MMseqs client and create a reference database.
        """
        logger.info(colors.yellow(f'Preparing MMseqs and creating reference database in {storage_directory}...'))

        # import mmseqs, os, shutil
        # if storage_directory is None:
        #     storage_directory = str(MMSEQS_CACHE_DIR)
        # if os.path.exists(storage_directory):
        #     shutil.rmtree(storage_directory)
        # os.makedirs(storage_directory)
        # self.client = mmseqs.MMSeqs(storage_directory=storage_directory)
        # self.client.databases.create('ref', 'ref genome-wide protein database', self.ref_target_seq_file)
        # logger.success(f'MMseqs reference database created in {storage_directory}.')

        import shutil
        # Reset MMseqs cache directory
        if os.path.exists(self.mmseqs_cache_dir):
            shutil.rmtree(self.mmseqs_cache_dir)
        os.makedirs(self.mmseqs_cache_dir, exist_ok=True)  
        # Create MMseqs reference database
        ref_db_path = os.path.join(self.mmseqs_cache_dir, 'ref')
        subprocess.run(["mmseqs", "createdb", self.ref_target_seq_file, ref_db_path], check=True)
        logger.success('MMseqs reference database created.')


    def prepare_cp_server(self):
        if check_pubchempy():
            import pubchempy as pcp
            self.cp_server = pcp
            self.cp_server_name = 'pubchem'  
            logger.success(f"pubchempy server connected succcess.")
        elif check_chemspipy():
            from chemspipy import ChemSpider
            self.cp_server = ChemSpider(os.environ['CHEMSPIDER_APIKEY'])
            self.cp_server_name = 'chemspider'
            logger.success(f"chemspider server connected succcess.")
        else:
            logger.warning(f"pubchempy or chemspipy service cannot be use! Please check your network connection.")
            self.cp_server = None


    def cal_similarity_from_fasta(self, custom_seq_fasta=None, save_sim_file=True):
        # prepare mmseqs
        if self.client is None:
            self.prepare_mmseqs(storage_directory=self.mmseqs_cache_dir)

        if custom_seq_fasta is not None:
            self.custom_target_seq_file = custom_seq_fasta
            self.custom_target_sim_file = self.custom_target_seq_file.replace('.fasta', '_similarity.csv')

        self.custom_target = list(set([seq_record.id.split('|')[1] if '|' in seq_record.id else seq_record.id for seq_record in SeqIO.parse(self.custom_target_seq_file, "fasta")]))

        logger.info(colors.yellow(f'Calculating similarity between {self.custom_target_seq_file} and reference fasta file...'))

        # print(f'Calculating similarity between {self.custom_target_seq_file} and reference data...')
        # results = self.client.databases[0].search_file(
        #         self.custom_target_seq_file, 
        #         search_type="protein",
        #         headers=["query_sequence_id", "target_sequence_id", "sequence_identity"]
        #         )
        # self.custom_target_sim = results.dataframe
        
        # Prepare MMseqs2 reference database
        ref_db_path = os.path.join(self.mmseqs_cache_dir, 'ref')
        if not os.path.exists(ref_db_path): 
            self._prepare_mmseqs_database()

        # Set custom target sequence FASTA file
        if custom_seq_fasta is not None:
            self.custom_target_seq_file = custom_seq_fasta
            # self.custom_target_sim_file = self.custom_target_seq_file.replace('.fasta', '_similarity.csv')
        # Extract unique IDs of custom target sequences
        self.custom_target = list(set([seq_record.id.split('|')[1] if '|' in seq_record.id else seq_record.id for seq_record in SeqIO.parse(self.custom_target_seq_file, "fasta")]))

        logger.info(f'Computing similarities between {self.custom_target_seq_file} and reference sequences...')

        # Run MMseqs2 with search commond
        # Define MMseqs2 working paths
        query_db_path = os.path.join(self.mmseqs_cache_dir, 'query')
        result_db_path = os.path.join(self.mmseqs_cache_dir, 'result')
        tmp_dir = os.path.join(self.mmseqs_cache_dir, 'tmp')
        aln_result = os.path.join(self.mmseqs_cache_dir, 'alnResult.m8')

        # Clean previous MMseqs2 outputs to avoid FileExistsError
        import glob
        import shutil
        for f in glob.glob(f"{query_db_path}*") + glob.glob(f"{result_db_path}*"):
            try:
                os.remove(f)
            except OSError:
                pass
        if os.path.exists(tmp_dir): shutil.rmtree(tmp_dir)
        
        # Run MMseqs2
        subprocess.run(["mmseqs", "createdb", self.custom_target_seq_file, query_db_path], check=True)
        subprocess.run(["mmseqs", "search", query_db_path, ref_db_path, result_db_path, tmp_dir, "-a"], check=True)
        subprocess.run(["mmseqs", "convertalis", query_db_path, ref_db_path, result_db_path, aln_result, "--format-output", "query,target,nident,alnlen,fident", "--format-mode", "4"], check=True)
        
        result_df = pd.read_csv(aln_result, sep='\t')
        result_df["fident_exact"] = (result_df["nident"]/result_df["alnlen"])
        sim_df = result_df.loc[:, ["query", "target", "fident_exact"]]
        sim_df.to_csv(self.custom_target_sim_file, header=None, index=False)
        self.custom_target_sim = sim_df

        # print(f'Resulting in {len(self.custom_target_sim)} records.')

        if save_sim_file:
            self.custom_target_sim.to_csv(self.custom_target_sim_file, index=False, header=False)
            logger.save(colors.green(f"MMseqs2 results saved to {self.custom_target_sim_file}"))


    def prepare_ref_target_graph(self, graph_type='weighted_directed'):
        if not self.graph_type:
            self.graph_type = 'weighted_directed'
        if self.ref_target_graph is not None:
            logger.download(colors.bold(f"Reference target graph prepared."))
            # print(f'Reference target graph with {len(self.ref_target)} nodes and {self.ref_target_graph.edge_weight.shape[0]} edges.')
            return

        if not os.path.exists(self.ref_target_seq_file):
            logger.error(f"{self.ref_target_seq_file} does not found. Please download it first.")
            raise ValueError(f'{self.ref_target_seq_file} not found.')

        # get graph node names (uniprot id)
        self.ref_target = list(set([seq_record.id.split('|')[1] for seq_record in SeqIO.parse(self.ref_target_seq_file, "fasta")]))

        # generate graph node embeddings
        if self.tgt_embedder.saved_embs == {}:
            self.tgt_embedder.get_embs_from_fasta(self.ref_target_seq_file)
        self.tgt_embs = self.tgt_embedder.saved_embs
        node_feature_df = pd.DataFrame(self.tgt_embs).T

        # generate node name & id mapping dict & node features
        node_names = self.ref_target
        num_nodes = len(node_names)
        self.node_name2id = {name: i for i, name in enumerate(node_names)}
        x = torch.tensor(node_feature_df.loc[node_names, :].values, dtype=torch.float)
        
        # prepared graph edges
        if self.ref_target_sim is None:
            if not os.path.exists(self.ref_target_sim_file):
                self.cal_similarity_from_fasta(self.ref_target_seq_file)
        self.ref_target_sim = pd.read_csv(self.ref_target_sim_file, header=None).drop_duplicates()
        edge_info_df = self.ref_target_sim.copy()
        
        # generate graph data
        logger.info(colors.yellow(f"Building a {graph_type} graph..."))
        valid_graph_types = ['weighted_directed', 'weighted_undirected', '50%_weighted_directed']
        if graph_type not in valid_graph_types:
            raise ValueError(f"Invalid graph_type: '{graph_type}'. Must be one of {valid_graph_types}")

        # initialize edge_index and edge_weight
        edge_index = None
        edge_weight = None

        # generate edge_index and edge_weight
        if not os.path.exists(self.ref_target_sim_file):
            self.cal_similarity_from_fasta(custom_seq_fasta=self.ref_target_seq_file)
        edge_info_df = pd.read_csv(self.ref_target_sim_file, header=None).drop_duplicates()
        edge_info_df.iloc[:, 0] = edge_info_df.iloc[:, 0].map(self.node_name2id)
        edge_info_df.iloc[:, 1] = edge_info_df.iloc[:, 1].map(self.node_name2id)
        edge_info_df.dropna(inplace=True)

        # weighted & directed
        edge_index = torch.tensor(edge_info_df.iloc[:, [1, 0]].astype(int).values.T, dtype=torch.long)
        edge_weight = torch.tensor(edge_info_df.iloc[:, 2].values, dtype=torch.float)
        # weighted & undirected
        if self.graph_type == 'weighted_undirected':
            edge_index, edge_weight = to_undirected(edge_index, edge_weight, reduce='mean')   # undirect'
        # unweighted & undirected
        elif self.graph_type == 'unweighted_undirected':
            # edge_index, _ = to_undirected(edge_index)  
            edge_index, edge_weight = to_undirected(edge_index, edge_weight, reduce='mean')   # undirect        
            edge_weight = torch.ones_like(edge_weight)
        # 50% weighted & directed
        elif self.graph_type == '50%_weighted_directed':
            mask = torch.rand(edge_index.size(1)) > 0.5
            edge_index = edge_index[:, mask]
            edge_weight = edge_weight[mask]

        edge_index, edge_weight = add_self_loops(edge_index, edge_weight, num_nodes=num_nodes)

        self.ref_target_graph = Data(x=x, edge_index=edge_index, edge_attr=edge_weight).to(self.device)
        self.ref_target_graph.node_names = node_names    # uniprot accession
    
        logger.success(f"Reference target graph prepared.")
        # print(f'Reference target graph with {len(self.ref_target)} nodes and {edge_weight.shape[0]} edges.')


    def construct_custom_target_graph(self, custom_seq_fasta=None):
        logger.info(colors.yellow(f'Constructing reference-custom target graph from {custom_seq_fasta}...'))
        # prepared graph edges
        self.cal_similarity_from_fasta(custom_seq_fasta)
        edge_info_df = self.custom_target_sim.copy()

        # prepared graph node embeddings
        custom_embs = self.tgt_embedder.get_embs_from_fasta(self.custom_target_seq_file)
        self.tgt_embs.update(custom_embs)
        node_feature_df = pd.DataFrame(self.tgt_embs).T

        # generate node name&id mapping dict
        new_nodes = list(set(self.custom_target) - set(self.ref_target))
        self.node_name2id.update({name: i+len(self.ref_target) for i, name in enumerate(new_nodes)})
        edge_info_df.iloc[:, 0] = edge_info_df.iloc[:, 0].map(self.node_name2id)
        edge_info_df.iloc[:, 1] = edge_info_df.iloc[:, 1].map(self.node_name2id)

        # generate graph data
        x = torch.tensor(node_feature_df.loc[self.ref_target+new_nodes, :].values, dtype=torch.float)
        edge_index = torch.tensor(edge_info_df.iloc[:, [1, 0]].values.T.astype(np.int64), dtype=torch.long).to(self.device)  # target, query for massage passing
        edge_index = torch.concat((self.ref_target_graph.edge_index, edge_index), dim=1)
        edge_weight = torch.tensor(edge_info_df.iloc[:, 2].values, dtype=torch.float).to(self.device)
        edge_weight = torch.concat((self.ref_target_graph.edge_attr, edge_weight), dim=0)
        edge_index, edge_weight = add_self_loops(edge_index, edge_weight, num_nodes=len(self.ref_target+new_nodes))

        self.custom_target_graph = Data(x=x, edge_index=edge_index, edge_attr=edge_weight).to(self.device)
        self.custom_target_graph.node_names = self.ref_target+new_nodes    # uniprot accession

        logger.success(f"Reference-custom target graph created with {len(self.custom_target_graph.node_names)} nodes and {edge_weight.shape[0]} edges.")


    ### train ###
    def prepare_training_data(self):
        tgt_graph_data = self.ref_target_graph.to(self.device)
        pair_dataset = CTPairDataset(self.training_data)
        logger.success(colors.green(f"Training data prepared."))
        return tgt_graph_data, pair_dataset


    def train(self, train_hparams=None):
        logger.print(colors.yellow(f"========================= New Train ========================="))
        from .scheduler import CosineDecayScheduler

        ### set train hyperparams ###
        self.set_train_hyperparams(train_hparams)

        ### setup tensorboard ###
        os.makedirs(self.save_dir, exist_ok=True)
        logger.info(f'Model weights and tensorboard logs will be saved to save_dir.')
        writer = SummaryWriter(self.save_dir)
        hparams = {}
        hparams.update(self.model_hparams)
        hparams.update(self.train_hparams)
        writer.add_text('hyperparams', str(hparams), 0)

        ### set global seed ###
        setup_seed(self.seed)

        ### prepare model structure ###
        unipert_models = self.unipert_models
        unipert_models = unipert_models.to(self.device)

        ### prepare data ###
        tgt_data, pair_dataset = self.prepare_training_data()

        ### prepare target graph transforms for bgrl ###
        transform_1 = get_graph_drop_transform(drop_edge_p=self.drop_edge_p_1, drop_feat_p=self.drop_feat_p_1)
        transform_2 = get_graph_drop_transform(drop_edge_p=self.drop_edge_p_2, drop_feat_p=self.drop_feat_p_2)

        ### setup optimizer ###
        optimizer = AdamW([
                    {'params': self.tgt_model.trainable_parameters()},     
                    {'params': self.cp_model.trainable_parameters()},       
                    {'params': self.align_model.parameters()}               
                    ], weight_decay=self.wd)

        ### train ###
        logger.info(colors.yellow("Start training UniPert..."))
        tgt_loss, ctc_loss = .0, .0

        # stage1 epochs for target graph self-supervised repsentation learning
        tgt_lr_scheduler = CosineDecayScheduler(self.lr1, self.epochs1//2, self.epochs1)
        mm_scheduler = CosineDecayScheduler(1-self.mm, 0, self.epochs1)
        logger.info(colors.bold(f'Stage 1: Target graph self-supervised learning...'))
        self.tgt_model.train()
        self.cp_model.eval()
        self.align_model.eval()   
        lr2 = .0
        optimizer.param_groups[1]['lr'] = lr2
        optimizer.param_groups[2]['lr'] = lr2
        pbar = tqdm(range(1, self.epochs1+1), desc='epochs ')
        for step in pbar:
            # update learning rate and momentum
            lr1 = tgt_lr_scheduler.get(step)
            optimizer.param_groups[0]['lr'] = lr1
            # print(lr1, lr2, mm)  

            # target encoder self-supervise loss
            tgt_x1, tgt_x2 = transform_1(tgt_data), transform_2(tgt_data)
            tgt_q1, tgt_y2 = self.tgt_model(tgt_x1, tgt_x2)
            tgt_q2, tgt_y1 = self.tgt_model(tgt_x2, tgt_x1)
            tgt_loss = 2 - F.cosine_similarity(tgt_q1, tgt_y2.detach(), dim=-1).mean() - F.cosine_similarity(tgt_q2, tgt_y1.detach(), dim=-1).mean()
            total_loss = tgt_loss + ctc_loss
            
            # update weights
            optimizer.zero_grad()
            total_loss.backward(retain_graph=False)
            optimizer.step()
            
            # update target network with the momentum
            mm = 1 - mm_scheduler.get(step)   
            self.tgt_model.update_target_network(mm)

            # log progress
            pbar.set_postfix(tgt_loss=f'{tgt_loss.item():.3f}')

            # log scalars
            if step==1 or step%10==0:
                writer.add_scalar('params/lr1', lr1, step)
                writer.add_scalar('params/lr2', lr2, step)
                writer.add_scalar('params/mm', mm, step)
                writer.add_scalar('train/tgt_loss', tgt_loss, step)
                writer.add_scalar('train/ctc_loss', ctc_loss, step)
                writer.add_scalar('train/total_loss', total_loss, step)
            
            torch.cuda.empty_cache()


        # stage2 epochs for both target graph self-sup & cp-tgt align learning
        steps_per_epoch = len(pair_dataset)//self.bs + 1
        tgt_lr_scheduler = CosineDecayScheduler(self.lr1, self.epochs2//2, self.epochs2)
        ctc_lr_scheduler = CosineDecayScheduler(self.lr2, steps_per_epoch//2, steps_per_epoch)
        mm_scheduler = CosineDecayScheduler(1-self.mm, 0, self.epochs2)
        logger.info(colors.bold(f'Stage 2: Target graph self-supervised learning and compound-target align learning...'))
        # set model status
        self.tgt_model.train()
        self.cp_model.train()
        self.align_model.train()
        avg_tgt_loss, avg_ctc_loss, avg_total_loss = 0, 0, 0
        pbar = tqdm(range(1, self.epochs2+1), desc='epochs ')
        for epoch in pbar:
            # shuffle per epoch
            torch.manual_seed(epoch)
            pair_loader = DataLoader(pair_dataset, batch_size=self.bs, shuffle=True, pin_memory=True)

            lr1 = tgt_lr_scheduler.get(epoch)
            optimizer.param_groups[0]['lr'] = lr1
            mm = 1 - mm_scheduler.get(epoch)

            for step, data_iter in enumerate(pair_loader):
                lr2 = ctc_lr_scheduler.get(step)
                optimizer.param_groups[1]['lr'] = lr2
                optimizer.param_groups[2]['lr'] = lr2
                # print(step, lr2)
                
                cp_sms, tgt_uas = data_iter
                cp_features = self.cp_model(cp_sms, self.device).to(self.device) 
                # target encoder self-supervise loss
                tgt_x1, tgt_x2 = transform_1(tgt_data), transform_2(tgt_data)
                tgt_q1, tgt_y2 = self.tgt_model(tgt_x1, tgt_x2)
                tgt_q2, tgt_y1 = self.tgt_model(tgt_x2, tgt_x1)
                tgt_loss = 2 - F.cosine_similarity(tgt_q1, tgt_y2.detach(), dim=-1).mean() - F.cosine_similarity(tgt_q2, tgt_y1.detach(), dim=-1).mean()

                # cp-tgt contrastive loss
                tgt_ids = torch.tensor([tgt_data.node_names.index(tgt_ua) for tgt_ua in tgt_uas], dtype=torch.long)
                with torch.no_grad():
                    tgt_features = self.tgt_model.online_encoder(tgt_data)[tgt_ids].to(self.device)  
    

                ctc_loss = self.align_model(cp_features, tgt_features, cp_sms, tgt_uas)
                total_loss = tgt_loss + ctc_loss

                avg_tgt_loss += tgt_loss.item()
                avg_ctc_loss += ctc_loss.item()
                avg_total_loss += total_loss.item()

                # update weights
                optimizer.zero_grad()
                total_loss.backward(retain_graph=True)
                optimizer.step()
                
                # update target network with the momentum
                self.tgt_model.update_target_network(mm)

            avg_tgt_loss /= steps_per_epoch
            avg_ctc_loss /= steps_per_epoch
            avg_total_loss /= steps_per_epoch

            # log progress
            pbar.set_postfix(tgt_loss=f'{avg_tgt_loss:.3f}', ctc_loss=f'{avg_ctc_loss:.3f}', total_loss=f'{avg_total_loss:.3f}')

            # log scalars
            if (self.epochs1+epoch)%1==0:
                writer.add_scalar('params/lr1', lr1, self.epochs1+epoch)
                writer.add_scalar('params/lr2', self.lr2, epoch)
                writer.add_scalar('params/mm', mm, self.epochs1+epoch)
                writer.add_scalar('train/tgt_loss', avg_tgt_loss, self.epochs1+epoch)
                writer.add_scalar('train/ctc_loss', avg_ctc_loss, epoch)
                writer.add_scalar('train/total_loss', avg_total_loss, self.epochs1+epoch)


            # save checkpoint
            checkpoint_path = os.path.join(self.save_dir, f'checkpoint_{epoch}.pt')
            if epoch % 100 == 0:
                torch.save({'cp_encoder': self.cp_model.state_dict(),
                            'tgt_encoder': self.tgt_model.online_encoder.state_dict(),
                            'model_hparams': self.model_hparams,
                            'train_hparams': self.train_hparams,
                            }, checkpoint_path)
                logger.info(f"\nModel checkpoint saved to {checkpoint_path}.")

            torch.cuda.empty_cache()

        # save encoder weights
        torch.save({'cp_encoder': self.cp_model.state_dict(),
                    'tgt_encoder': self.tgt_model.online_encoder.state_dict(),
                    'model_hparams': self.model_hparams,
                    'train_hparams': self.train_hparams,
                    }, self.model_path)
        logger.save(colors.green(f"Model training done."))
        logger.info(f"Model saved to {self.model_path}.")
       
        writer.add_hparams(hparams, {
            'hparam/tgt_loss': avg_tgt_loss,
            'hparam/ctc_loss': avg_ctc_loss,
            'hparam/total_loss': avg_total_loss
        })
        writer.close()


    ### application ###
    def load_models(self, save_dir=None, device=None):
        if not save_dir:
            model_path = os.path.join(self.save_dir, 'unipert_model.pt')
        else:
            self.save_dir = save_dir
            model_path = os.path.join(save_dir, 'unipert_model.pt')

        # construct and load model
        try:
            # model weights
            model_weights = torch.load(model_path, map_location=device)
            # model hyperparameters
            if 'model_hparams' in model_weights.keys():
                self.set_model_hyperparams(model_weights.pop('model_hparams'))
                self.save_dir = save_dir if save_dir else self.save_dir
                # self.save_dir = self.save_dir.replace('/fionafyang/lynnymli/', '/data/liyiming/Project/UniPert_G2CP/')
            elif 'hparams' in model_weights.keys():
                self.set_model_hyperparams(model_weights.pop('hparams'))
                self.save_dir = save_dir if save_dir else self.save_dir
                # self.save_dir = self.save_dir.replace('/fionafyang/lynnymli/', '/data/liyiming/Project/UniPert_G2CP/')
            else:
                self.set_model_hyperparams(params={'save_dir': self.save_dir})

            # device
            if not device:
                self.device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
            else:
                self.device = device

            # model structure
            print(f"Loading model from {self.save_dir}...")
            unipert_models = self.construct_model()
            unipert_models = unipert_models.to(self.device)
            logger.download(colors.green(f"Pretrained model file loaded."))
            try:
                self.cp_model.load_state_dict(model_weights['cp_encoder'])
                try:
                    self.tgt_encoder.load_state_dict(model_weights['tgt_encoder'])
                except:
                    model_weights['tgt_encoder']['model.module_0.bias'] = model_weights['tgt_encoder']['model.module_0.lin.bias']
                    model_weights['tgt_encoder']['model.module_3.bias'] = model_weights['tgt_encoder']['model.module_3.lin.bias']
                    model_weights['tgt_encoder'].pop('model.module_0.lin.bias')
                    model_weights['tgt_encoder'].pop('model.module_3.lin.bias')
                    self.tgt_encoder.load_state_dict(model_weights['tgt_encoder'])
            except:
                logger.error(f"Failed to load model from {self.model_path}.")
        except FileExistsError:
            # print("No saved model found. Please download or train the model.")
            logger.error("No saved model found. Please download or train the model.")
            

    def cp_pertId2smiles_mapping(self, csv_file, key_column_name='pert_id', value_column_name='canonical_smiles'):
        # key_column_name, value_column_name = 'pert_id', 'canonical_smiles'
        df = pd.read_csv(csv_file).dropna(subset=['pubchem_cid']).loc[:, [key_column_name, value_column_name]].drop_duplicates()
        df = df[df[value_column_name]!='restricted']
        return dict(zip(df[key_column_name], df[value_column_name]))


    def tgt_symbol2uniprot_mapping(self, csv_file, key_column_name='Approved symbol', value_column_name='UniProt accession'):
        df = pd.read_csv(csv_file).dropna(subset=[key_column_name, value_column_name]).loc[:, [key_column_name, value_column_name]].drop_duplicates()
        return dict(zip(df[key_column_name], df[value_column_name]))


    def load_unipert_reps(self):
        reps_path = os.path.join(self.save_dir, 'unipert_reps.pkl')
        if os.path.exists(reps_path):
            unipert_reps = pd.read_pickle(reps_path)
            self.unipert_reps.update(unipert_reps)       
            logger.success(f"Referece representations loaded.")
        else:
            logger.warning(f"{reps_path} not found.")
        

    def encode_ref_perturbagens(self, save=False):
        cp_ptbg_info_file = os.path.join(self.data_dir, 'processed_cmap_compound_info_pid34418_cid33913_sm33975.csv')
        tgt_ptbg_info_file = os.path.join(self.data_dir, 'processed_target_info_hgnc19321.csv')
        self.cp_model.eval()
        self.tgt_encoder.eval()
        self.load_unipert_reps()

        # cmap ptbgs
        cp_pertId2smiles_dict = self.cp_pertId2smiles_mapping(cp_ptbg_info_file)  # 'pert_id' -> 'canonical_smiles'
        tgt_symbol2uniprot_dict = self.tgt_symbol2uniprot_mapping(tgt_ptbg_info_file)  # 'cmap_name' -> 'uniprot accession'

        # encode cp ptbgs
        cp_unipert_reps = {}
        sms = list(cp_pertId2smiles_dict.values())

        ### encode for unseen smiles
        unembedded_sms = [s for s in sms if s not in self.cp_model.embedder.saved_embs.keys()]
        new_embs = self.cp_model.embedder.get_bulk_emb_from_smiles_list(unembedded_sms, save=False)
        self.cp_model.embedder.saved_embs.update(new_embs)
        self.cp_model.emb_dict = self.cp_model.embedder.saved_embs

        cp_reps = self.cp_model(sms, self.device).detach().cpu().numpy()    
        assert len(cp_pertId2smiles_dict) == cp_reps.shape[0]
        for i, pert_id in enumerate(cp_pertId2smiles_dict.keys()):
            cp_unipert_reps[pert_id] = cp_reps[i]

        # encode tgt ptbgs
        tgt_unipert_reps = {}
        # Get target names (uniprot accession)
        tgt_names = self.ref_target_graph.node_names   # uniprot accession
        tgt_reps = self.tgt_encoder(self.ref_target_graph.to(self.device)).detach().cpu().numpy() 

        assert len(tgt_names) == tgt_reps.shape[0]
        for gene_symbol, uniprot_id in tgt_symbol2uniprot_dict.items():
            self.tgt_embedder.saved_embs[gene_symbol] = self.tgt_embedder.saved_embs[uniprot_id]
            tgt_unipert_reps[gene_symbol] = tgt_reps[tgt_names.index(uniprot_id)]
        for uniprot_id in tgt_names:
            tgt_unipert_reps[uniprot_id] = tgt_reps[tgt_names.index(uniprot_id)]
        
        self.unipert_reps.update(tgt_unipert_reps)    
        self.unipert_reps.update(cp_unipert_reps)   
        logger.success(f"{len(cp_pertId2smiles_dict)} ref compounds and {len(tgt_names)} ref targets encoded.")  
            
        if save:
            reps_path = os.path.join(self.save_dir, 'unipert_reps.pkl')
            with open(reps_path, 'wb') as f:
                pickle.dump(self.unipert_reps, f)
            logger.save(f'Unipert representations saved to {reps_path}.')

        # return self.unipert_reps


    def encode_genetic_perturbagens_from_fasta(
        self, 
        custom_seq_fasta=None, 
        save=False
        ):
        """Encode genetic perturbagens from fasta file.
        """

        assert custom_seq_fasta is not None, "Please provide a fasta file."
        self.tgt_encoder.eval()
        self.load_unipert_reps()

        # prepared data
        self.construct_custom_target_graph(custom_seq_fasta)
        self.custom_target_graph = self.custom_target_graph.to(self.device)
        tgt_names = self.custom_target_graph.node_names    # uniprot accession

        # encode tgt ptbgs
        custom_target_reps = {}
        tgt_reps = self.tgt_encoder(self.custom_target_graph).detach().cpu().numpy() 

        assert len(tgt_names) == tgt_reps.shape[0]          # uniprot accession->pert name
        for tgt_uid in self.custom_target:
            if tgt_uid in self.custom_target_ui2pn.keys():
                pns = self.custom_target_ui2pn[tgt_uid]
                for pn in pns:
                    custom_target_reps[pn] = tgt_reps[tgt_names.index(tgt_uid)]
            else:
                custom_target_reps[tgt_uid] = tgt_reps[tgt_names.index(tgt_uid)]
        self.unipert_reps.update(custom_target_reps)
        # save
        if save:
            save_dir = os.path.join(self.save_dir, f'unipert_reps.pkl')
            with open(save_dir, 'wb') as f:
                pickle.dump(self.unipert_reps, f)
            logger.save(colors.green(f'Custom perturbagen representations saved at {save_dir}.'))
        return custom_target_reps


    def encode_genetic_perturbagens_from_gene_names(
            self, 
            gene_names: list, 
            save=False
        ):
        """Encode genetic perturbagens from gene names.
        """
        if not gene_names:
            logger.warning("gene_names is empty, skipping operation.")
            return

        self.load_unipert_reps()
        self.encode_ref_perturbagens()
        gene_names = list(set(gene_names))
        out_reps = {}
        invalid_inputs = []
        records = []
        logger.info(colors.yellow(f"Encoding {len(gene_names)} genetic perturbagens with UniPert..."))
        for gene in tqdm(gene_names):
            if gene in list(self.unipert_reps.keys()):
                out_reps[gene] = self.unipert_reps[gene]
                continue
            if gene.upper() in list(self.unipert_reps.keys()):
                out_reps[gene] = self.unipert_reps[gene.upper()]
                continue
            proid_seq = get_tgt_seq_from_gene_name(gene)   # [uniprot_id, head, seq]
            if proid_seq:
                self.custom_target_ui2pn[proid_seq[0]].append(gene)
                rec = SeqRecord(Seq(proid_seq[2]), 
                                id=proid_seq[1], 
                                description=f'PN={gene}'    # pert name
                                )
                records.append(rec) 
            else:
                invalid_inputs.append(gene)
        # write to fasta file
        if records != []:
            SeqIO.write(records, self.custom_target_seq_file, "fasta")
            reps = self.encode_genetic_perturbagens_from_fasta(
                self.custom_target_seq_file,
                save=False
                )
            out_reps.update(reps)
        # save
        if save:
            reps_path = os.path.join(self.save_dir, f'unipert_reps.pkl')
            self.unipert_reps.update(out_reps)
            with open(reps_path, 'wb') as f:
                pickle.dump(self.unipert_reps, f)
            logger.save(f'Custom perturbagen representations saved at {reps_path}.')
        return out_reps, invalid_inputs
    
    
    def encode_genetic_perturbagens_from_uniprot_accessions(
            self, 
            uniprot_accessions: list, 
            save=False
        ):
        """Encode genetic perturbagens from gene names.
        """
        if not uniprot_accessions:
            logger.warning("uniprot_accessions is empty, skipping operation.")
            return

        self.load_unipert_reps()
        self.encode_ref_perturbagens()
        uniprot_accessions = list(set(uniprot_accessions))
        out_reps = {}
        invalid_inputs = []
        records = []
        logger.info(colors.yellow(f"Encoding {len(uniprot_accessions)} genetic perturbagens with UniPert..."))
        for query_ua in tqdm(uniprot_accessions):
            if query_ua in list(self.unipert_reps.keys()):
                out_reps[query_ua] = self.unipert_reps[query_ua]
                continue
            if query_ua.upper() in list(self.unipert_reps.keys()):
                out_reps[query_ua] = self.unipert_reps[query_ua.upper()]
                continue
            proid_seq = get_tgt_seq_from_uniprot_accession(query_ua)   # [uniprot_id, head, seq]
            if proid_seq:
                self.custom_target_ui2pn[proid_seq[0]].append(query_ua)
                rec = SeqRecord(Seq(proid_seq[2]), 
                                id=proid_seq[1], 
                                description=f'PN={query_ua}'    # pert name
                                )
                records.append(rec) 
            else:
                invalid_inputs.append(query_ua)
        # write to fasta file
        if records != []:
            SeqIO.write(records, self.custom_target_seq_file, "fasta")
            reps = self.encode_genetic_perturbagens_from_fasta(
                self.custom_target_seq_file,
                save=False
                )
            out_reps.update(reps)
        # save
        if save:
            reps_path = os.path.join(self.save_dir, f'unipert_reps.pkl')
            self.unipert_reps.update(out_reps)
            with open(reps_path, 'wb') as f:
                pickle.dump(self.unipert_reps, f)
            logger.save(f'Custom perturbagen representations saved at {reps_path}.')
        return out_reps, invalid_inputs
        

    def encode_chemical_perturbagens_from_smiles(
            self,
            smiles_list, 
            save=False
        ):
        """Encode chemical perturbagens from smiles list.
        """
        # get smiles embedder
        self.cp_model.eval().to(self.device)
        self.load_unipert_reps()
        unembedded_sms = [s for s in smiles_list if s not in self.cp_model.embedder.saved_embs.keys()]
        new_embs = self.cp_model.embedder.get_emb_from_smiles_list(unembedded_sms)
        self.cp_model.embedder.saved_embs.update(new_embs)
        self.cp_model.emb_dict = self.cp_model.embedder.saved_embs
        # encode ptbgs
        custom_compound_reps = {}
        cp_reps = self.cp_model(smiles_list, self.device).detach().cpu().numpy()   
        assert len(smiles_list) == cp_reps.shape[0]
        for i, (sm, reps) in enumerate(zip(smiles_list, cp_reps)):
            custom_compound_reps[sm] = cp_reps[i]
        self.unipert_reps.update(custom_compound_reps)
        # save
        if save:
            save_dir = os.path.join(self.save_dir, f'unipert_reps.pkl')
            with open(save_dir, 'wb') as f:
                pickle.dump(self.unipert_reps, f)
            logger.save(f'Custom perturbagen representations saved at {save_dir}.')

        return custom_compound_reps


    def encode_chemical_perturbagens_from_cp_sms_csv(
            self, 
            custom_cp_sms_csv, 
            cp_col_name='Compound', 
            sms_col_name='SMILES', 
            save=False
        ):
        """Encode chemical perturbagens from csv file.
        """
        self.cp_model.eval().to(self.device)
        self.load_unipert_reps()
        # get compound and smiles
        cp_sms_df = pd.read_csv(custom_cp_sms_csv).loc[:, [cp_col_name, sms_col_name]]
        cp_sms_df = cp_sms_df.dropna(subset=[sms_col_name])
        cp_sms_df = cp_sms_df.drop_duplicates()
        # cp_sms_dict = cp_sms_df.set_index(cp_col_name)[sms_col_name].to_dict()
        assert len(cp_sms_df) > 0, "No custom compounds found in the provided csv file."
        cp_sms_df['is_valid'] = cp_sms_df[sms_col_name].apply(lambda sms: check_smiles(sms))
        cp_sms_df = cp_sms_df[cp_sms_df['is_valid']==True]
        compound_lists = cp_sms_df[cp_col_name].tolist()
        smiles_list = cp_sms_df[sms_col_name].tolist()
        # get smiles embedder
        _ = self.cp_model.embedder.get_emb_from_smiles_list(smiles_list)
        self.cp_model.emb_dict = self.cp_model.embedder.saved_embs
        # encode ptbgs
        custom_compound_reps = {}
        cp_reps = self.cp_model(smiles_list, self.device).detach().cpu().numpy()   
        assert len(smiles_list) == cp_reps.shape[0] == len(compound_lists)
        for i, (cp, _) in enumerate(zip(compound_lists, smiles_list)):
            custom_compound_reps[cp] = cp_reps[i]
        
        self.unipert_reps.update(custom_compound_reps)
        # save embs
        if save:
            save_dir = os.path.join(self.save_dir, f'unipert_reps.pkl')
            with open(save_dir, 'wb') as f:
                pickle.dump(self.unipert_reps, f)
            print(f'Custom perturbagen representations saved at {save_dir}.')

        return custom_compound_reps
    

    def generate_unipert_embs_for_pert_adata(
            self,
            adata: anndata.AnnData,  
            ptbg_cols: List[str] = ['perturbation'],  
            ptbg_types: Optional[List[str]] = None, 
            control_key: str = 'control',
            return_results: bool = False
        ):
        """
        Generate embeddings for perturbagens based on the given perturbation AnnData object.

        Parameters:
        adata : anndata.AnnData
            A required perturbation AnnData object.
        ptbg_cols : list of str
            Required list of adata.obs.column names, indicating perturbagen info .
        ptbg_types : list of str, optional
            An optional list of strings indicating the type of each ptbg_key.
            Valid types include 'genetic' and 'chemical'.
            If provided, must be a list of strings with the same length as ptbg_cols.
        control_key: str, default 'control'
        return_emb : bool, default True
        """
        self.load_unipert_reps()
        # adata = adata.copy()
        valid_types = ['genetic', 'chemical']
        if not isinstance(ptbg_cols, list) or not isinstance(ptbg_types, list):
            raise ValueError("ptbg_keys and ptbg_types must be list")
        elif len(ptbg_cols) != len(ptbg_types):
            raise ValueError("ptbg_keys and ptbg_types must have the same length")
        elif any(t not in valid_types for t in ptbg_types):
            raise ValueError("ptbg_types must be 'genetic' or 'chemical'")
        else:
            genetic_ptbgs = []
            chemical_ptbgs = []
            invalid_ptbgs = []

            for key, typ in zip(ptbg_cols, ptbg_types):
                if key not in adata.obs.columns:
                    raise ValueError(f"{key} not found in adata.obs.columns")
                else:
                    ptbgs = list(adata.obs.dropna(subset=[key])[key].unique())
                    if control_key in ptbgs: ptbgs.remove(control_key)
                    if typ == 'genetic':
                        genetic_ptbgs.extend(ptbgs)
                    elif typ == 'chemical':
                        chemical_ptbgs.extend(ptbgs)    

            unipert_embs = {}
            # encode genetic ptbgs
            if genetic_ptbgs != []:
                genetic_ptbgs = list(set(genetic_ptbgs))
                records = []
                logger.info(colors.yellow(f"Retrieving sequence for genetic perturbagens..."))
                for gene in tqdm(genetic_ptbgs):
                    if gene in self.unipert_reps.keys():
                        unipert_embs[gene] = self.unipert_reps[gene]
                        continue
                    proid_seq = get_tgt_seq_from_gene_name(gene)   # [uniprot_id, head, seq]
                    if proid_seq:
                        self.custom_target_ui2pn[proid_seq[0]].append(gene)
                        rec = SeqRecord(Seq(proid_seq[2]), 
                                        id=proid_seq[1], 
                                        description=f'PN={gene}'    # pert name
                                        )
                        records.append(rec) 
                    else:
                        invalid_ptbgs.append(gene)
                        
                if len(records) > 0:
                # write to fasta file
                    # records = list(set(records))
                    SeqIO.write(records, self.custom_target_seq_file, "fasta")
                    genetic_ptbg_embs = self.encode_genetic_perturbagens_from_fasta(
                        self.custom_target_seq_file,
                        save=False
                        )
                    unipert_embs.update(genetic_ptbg_embs)

            # encode chemical ptbgs
            chemical_ptbg_embs = None
            if chemical_ptbgs != []:
                if not self.cp_server: self.prepare_cp_server()
                chemical_ptbgs = list(set(chemical_ptbgs))
                cp_sms = {}
                logger.info(colors.yellow("Retrievaling SMILES for chemical perturbagens..."))
                for compound in tqdm(chemical_ptbgs):
                    if compound in self.unipert_reps.keys():
                        unipert_embs[compound] = self.unipert_reps[compound]
                        continue
                    sms = get_cp_sms_from_compound_name(compound, server=self.cp_server)
                    if sms:
                        cp_sms[compound] = sms
                    else:
                        invalid_ptbgs.append(compound)
                
                if len(cp_sms) > 0:
                    # transfer chemical_smiles(dict) to df and write to csv file
                    chemical_ptbg_df = pd.DataFrame(list(cp_sms.items()), columns=['Compound', 'SMILES'])
                    chemical_ptbg_df.to_csv(self.custom_compound_smiles_file, index=False)
                    chemical_ptbg_embs = self.encode_chemical_perturbagens_from_cp_sms_csv(
                        self.custom_compound_smiles_file, 
                        cp_col_name='Compound', 
                        sms_col_name='SMILES',
                        save=False
                        )
                    unipert_embs.update(chemical_ptbg_embs)

            # save unipert_embs to adata.uns['unipert_emb']
            adata.uns['UniPert_reps'] = unipert_embs
            adata.uns['invalid_ptbgs'] = invalid_ptbgs
            logger.success(colors.green(f'UniPert representations generated!'))
            logger.info(f"{len(unipert_embs)} perturbagens' UniPert representations saved to adata.uns['UniPert_reps']")
            if len(invalid_ptbgs)>0:
                logger.warning(f"{len(invalid_ptbgs)} perturbagens can not be repersentated and saved to adata.uns['invalid_ptbgs']: \n{invalid_ptbgs}")

            if return_results:
                return {'UniPert_reps': unipert_embs, 'invalid_ptbgs': invalid_ptbgs}
