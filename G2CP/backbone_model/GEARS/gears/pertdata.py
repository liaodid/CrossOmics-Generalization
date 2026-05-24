from torch_geometric.data import Data
import torch
import numpy as np
import pickle
from torch_geometric.data import DataLoader
import os
import scanpy as sc
from tqdm import tqdm

import warnings
warnings.filterwarnings("ignore")
sc.settings.verbosity = 0

from .data_utils import get_DE_genes, get_dropout_non_zero_genes, DataSplitter
from .utils import print_sys, zip_data_download_wrapper, dataverse_download,\
                  filter_pert_in_go, get_genes_from_perts, tar_data_download_wrapper,\
                  molecule_split_deepchem

class PertData:
    """
    Class for loading and processing perturbation data

    Attributes
    ----------
    data_path: str
        Path to save/load data
    gene_set_path: str
        Path to gene set to use for perturbation graph
    default_pert_graph: bool
        Whether to use default perturbation graph or not
    dataset_name: str
        Name of dataset
    dataset_path: str
        Path to dataset
    adata: AnnData
        AnnData object containing dataset
    dataset_processed: bool
        Whether dataset has been processed or not
    ctrl_adata: AnnData
        AnnData object containing control samples
    gene_names: list
        List of gene names
    node_map: dict
        Dictionary mapping gene names to indices
    split: str
        Split type
    seed: int
        Seed for splitting
    subgroup: str
        Subgroup for splitting
    train_gene_set_size: int
        Number of genes to use for training

    """
    
    def __init__(self, 
                 data_path, 
                 gene_set_path=None, 
                #  default_pert_graph=True,
                 ):
        """
        Parameters
        ----------

        data_path: str
            Path to save/load data
        gene_set_path: str
            Path to gene set to use for perturbation graph
        default_pert_graph: bool
            Whether to use default perturbation graph or not

        """

        
        # Dataset/Dataloader attributes
        self.data_path = data_path
        # self.default_pert_graph = default_pert_graph
        self.gene_set_path = gene_set_path
        self.dataset_name = None
        self.dataset_path = None
        self.adata = None
        self.dataset_processed = None
        self.ctrl_adata = None
        self.gene_names = []
        self.node_map = {}

        # Split attributes
        self.split = None
        self.seed = None
        self.subgroup = None
        self.train_gene_set_size = None

        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)

        # server_path = 'https://dataverse.harvard.edu/api/access/datafile/6153417'
        # dataverse_download(server_path,
        #                    os.path.join(self.data_path, 'gene2go_all.pkl'))
        # with open(os.path.join(self.data_path, 'gene2go_all.pkl'), 'rb') as f:
        #     self.gene2go = pickle.load(f)
   
    def load(self, 
             data_name = None, 
             data_path = None,
             pert_type_col_name = 'pert_type',
             perturbagen_col_name = 'condition',
             control_key = 'ctrl'
             ):
        """
        Load existing dataloader
        Use data_name for loading 'norman', 'adamson', 'dixit' datasets
        For other datasets use data_path

        Parameters
        ----------
        data_name: str
            Name of dataset
        data_path: str
            Path to dataset

        Returns
        -------
        None

        """
        self.pert_type_col_name = pert_type_col_name
        self.perturbagen_col_name = perturbagen_col_name
        self.control_key = control_key
        self.num_samples = 1
    
        if data_name in ['LINCS-A549', 'LINCS-A375', 'LINCS-MCF7', 'LINCS-PC3', 'LINCS-HT29', 'LINCS-pool']:
            cell_line = data_name.split('-')[1]
            data_path = os.path.join(self.data_path, 'LINCS', cell_line)
            self.dataset_path = data_path
            self.dataset_name = data_name
            adata_path = os.path.join(data_path, f'{cell_line}_gene_chem_ctrl_adata.h5ad')
            self.adata = sc.read_h5ad(adata_path)
            self.gene_ptbgs = list(self.adata.obs[(self.adata.obs[self.pert_type_col_name] == 'trt_xpr')][self.perturbagen_col_name].unique())
            self.chem_ptbgs = list(self.adata.obs[(self.adata.obs[self.pert_type_col_name] == 'trt_cp')][self.perturbagen_col_name].unique())
            self.all_ptbgs = list(set(self.chem_ptbgs) | set(self.gene_ptbgs))
            self.gene_names = list(self.adata.var.index)
            print_sys(f'genetic ptbgs: {len(self.gene_ptbgs)}')
            print_sys(f'chemical ptbgs: {len(self.chem_ptbgs)}')
            if data_name in ['LINCS-pool']:
                self.batch_key = 'cell_line'    
            else:
                self.batch_key = None
        elif data_name in ["CPJUMP1-A549", "CPJUMP1-U2OS"]:
            cell_line = data_name.split('-')[1]
            data_path = os.path.join(self.data_path, 'CPJUMP1', cell_line)
            self.dataset_path = data_path
            self.dataset_name = data_name
            adata_path = os.path.join(data_path, f'{cell_line}_gene_chem_ctrl_adata.h5ad')
            self.adata = sc.read_h5ad(adata_path)
            self.gene_ptbgs = list(self.adata.obs[(self.adata.obs[self.pert_type_col_name] == 'trt_xpr')][self.perturbagen_col_name].unique())
            self.chem_ptbgs = list(self.adata.obs[(self.adata.obs[self.pert_type_col_name] == 'trt_cp')][self.perturbagen_col_name].unique())
            self.all_ptbgs = list(set(self.chem_ptbgs) | set(self.gene_ptbgs))
            self.gene_names = list(self.adata.var.index)
            print_sys(f'genetic ptbgs: {len(self.gene_ptbgs)}')
            print_sys(f'chemical ptbgs: {len(self.chem_ptbgs)}')
            self.batch_key = 'Plate'
            self.num_samples = 3
        elif os.path.exists(data_path):
            adata_path = os.path.join(data_path, 'perturb_processed.h5ad')
            self.adata = sc.read_h5ad(adata_path)
            self.dataset_name = data_path.split('/')[-1]
            self.dataset_path = data_path
        else:
            raise ValueError("data attribute is either ['LINCS-A549', 'LINCS-A375', 'LINCS-MCF7', 'LINCS-PC3', 'LINCS-HT29', 'CPJUMP1_A549', 'CPJUMP1_U2OS'] "
                             "or a path to an h5ad file")
        
        ### check unipert representation
        if 'UniPert_reps' in self.adata.uns.keys():
            self.unipert_reps = self.adata.uns['UniPert_reps']
        else:
            print_sys('No UniPert_reps found in adata.uns. Please get UniPert_reps first!')
            return
        
        ### pyg dataset
        pyg_path = os.path.join(data_path, 'data_pyg')
        if not os.path.exists(pyg_path): os.mkdir(pyg_path)
        dataset_fname = os.path.join(pyg_path, 'cell_graphs.pkl')         
        
        if os.path.isfile(dataset_fname):
            print_sys("Local copy of pyg dataset is detected. Loading...")
            self.dataset_processed = pickle.load(open(dataset_fname, "rb"))        
            print_sys("Done!")
        else:
            self.ctrl_adata = self.adata[self.adata.obs[self.perturbagen_col_name] == self.control_key]
            
            print_sys("Creating pyg object for each cell in the data...")
            self.create_dataset_file()
            print_sys("Saving new dataset pyg object at " + dataset_fname) 
            pickle.dump(self.dataset_processed, open(dataset_fname, "wb"))    
            print_sys("Done!")

    def prepare_split(self, 
                    split = 'pretrain',   
                    seed = 0, 
                    seed1 = 0, 
                    seed2 = 0, 
                    train_ptbg_set_frac = 0.8,
                    pretrain_ptbg_set_frac = 0.8,
                    finetune_ptbg_set_frac = 0.8,
                    val_ptbg_set_frac = 0.1,
                    test_ptbgs = None,
                    split_dict_path=None
                    ):

        """
        Prepare splits for training, validation and testing

        Parameters
        ----------
        split: str
            Type of split to use. 
        seed: int
            Random seed
        train_ptbg_set_frac: float
            Fraction of genes to use for training
        test_ptbgs: list
            List of perturbations to use for testing
        split_dict_path: str
            Path to dictionary used for custom split. Sample format:
                {'train': [X, Y], 'val': [P, Q], 'test': [Z]}

        Returns
        -------
        None

        """
        self.split = split
        self.seed = seed
        self.seed1 = seed1
        self.seed2 = seed2
        self.train_ptbg_set_frac = train_ptbg_set_frac
        self.pretrain_ptbg_set_frac = pretrain_ptbg_set_frac
        self.finetune_ptbg_set_frac = finetune_ptbg_set_frac
        
        if 'custom' in split:
            try:
                with open(split_dict_path, 'rb') as f:
                    self.set2conditions = pickle.load(f)
            except:
                    raise ValueError('Please set split_dict_path for custom split')
            return
            
        split_folder = os.path.join(self.dataset_path, 'splits')
        if not os.path.exists(split_folder): os.mkdir(split_folder)

        if 'cpf' in split:
            # cross-pretrain-finetune exps
            split_file = self.dataset_name + '_' + str(seed) + '_' + str(self.pretrain_ptbg_set_frac) + '_' + str(self.finetune_ptbg_set_frac) + '_cpf' + '.pkl'
        elif 'pool' in split:
            # cellular context-integrated exps
            split_file = self.dataset_name + '_' + str(seed) + '_1.0_pool' + '.pkl'
        elif ('essp' in split) or ('simf' in split):
            # gene essentiality / compound similsrity -based cpf exps
            split_name = ('-').join(split.split('-')[-2:])
            split_file = self.dataset_name + '_' + str(seed) + '_' + str(self.pretrain_ptbg_set_frac) + '_' + str(self.finetune_ptbg_set_frac) + '_' + split_name + '.pkl'
        else:
            # touchstone as finetune set (ts exps)
            split_file = self.dataset_name + '_' + str(seed) + '_' +  str(self.train_ptbg_set_frac) + '.pkl'

        split_path = os.path.join(split_folder, split_file)
        
        # load data split file
        if os.path.exists(split_path):
            print('here1')
            print_sys("Local copy of split is detected. Loading...")
            set2conditions = pickle.load(open(split_path, "rb"))
            print_sys(f"train ptbgs: {len(set2conditions['train'])}")
            print_sys(f"val ptbgs: {len(set2conditions['val'])}")
            print_sys(f"test ptbgs: {len(set2conditions['test'])}")
            if 'pretrain_train' in set2conditions.keys():
                print_sys(f"pretrain_train ptbgs: {len(set2conditions['pretrain_train'])}")
            if 'pretrain_val' in set2conditions.keys():
                print_sys(f"pretrain_val ptbgs: {len(set2conditions['pretrain_val'])}")
        else:
            print_sys("Creating new splits....")
            map_dict = {}
            set2conditions = {}
            if ('pretrain-finetune' in split) or ('ground-truth' in split) or ('no-pretrain' in split) or ('no-perturb' in split):
                if 'cpf' in split:
                    # cross pretrain & fine-tune with diverse proportion
                    # finetune
                    rng_test = np.random.default_rng(seed=self.seed)
                    test_ptbgs = rng_test.choice(self.chem_ptbgs, int(len(self.chem_ptbgs) * (1-self.finetune_ptbg_set_frac)), replace=False)
                    train_val_ptbgs = np.setdiff1d(self.chem_ptbgs, test_ptbgs)
                    val_ptbgs = rng_test.choice(train_val_ptbgs, int(len(train_val_ptbgs) * val_ptbg_set_frac), replace=False)
                    train_ptbgs = np.setdiff1d(train_val_ptbgs, val_ptbgs)

                    # pretrain
                    rng_pretrain = np.random.default_rng(seed=self.seed)
                    pretrain_ptbgs = rng_pretrain.choice(self.gene_ptbgs, int(len(self.gene_ptbgs) * self.pretrain_ptbg_set_frac), replace=False)
                    pretrain_val_ptbgs = rng_pretrain.choice(pretrain_ptbgs, int(len(pretrain_ptbgs) * val_ptbg_set_frac), replace=False)
                    pretrain_train_ptbgs = np.setdiff1d(pretrain_ptbgs, pretrain_val_ptbgs)  
                elif 'pool' in split:
                    # pooled genetic pretrain
                    rng_pretrain = np.random.default_rng(seed=self.seed)
                    pretrain_val_ptbgs = rng_pretrain.choice(self.gene_ptbgs, int(len(self.gene_ptbgs) * val_ptbg_set_frac), replace=False)
                    pretrain_train_ptbgs = np.setdiff1d(self.gene_ptbgs, pretrain_val_ptbgs)    
                    # specific chemical finetune (unused)
                    rng_test = np.random.default_rng(seed=self.seed)
                    test_ptbgs = rng_test.choice(self.chem_ptbgs, int(len(self.chem_ptbgs) * (1-self.train_ptbg_set_frac)), replace=False)
                    train_val_ptbgs = np.setdiff1d(self.chem_ptbgs, test_ptbgs)
                    val_ptbgs = rng_test.choice(train_val_ptbgs, int(len(train_val_ptbgs) * val_ptbg_set_frac), replace=False)
                    train_ptbgs = np.setdiff1d(train_val_ptbgs, val_ptbgs)
                elif 'essp' in split:
                    # pretrain & fine-tune with diverse proportion with different gene splitting based on gene essentiality
                    # finetune
                    rng_test = np.random.default_rng(seed=self.seed)
                    test_ptbgs = rng_test.choice(self.chem_ptbgs, int(len(self.chem_ptbgs) * (1-self.finetune_ptbg_set_frac)), replace=False)
                    train_val_ptbgs = np.setdiff1d(self.chem_ptbgs, test_ptbgs)
                    val_ptbgs = rng_test.choice(train_val_ptbgs, int(len(train_val_ptbgs) * val_ptbg_set_frac), replace=False)
                    train_ptbgs = np.setdiff1d(train_val_ptbgs, val_ptbgs)
                    # pretrain
                    if 'dep' in split:
                        file_dir = os.path.join(self.data_path, 'processed_DepMap_ranked_gene_essentiality.pkl')
                    if 'udep' in split:
                        file_dir = os.path.join(self.data_path, 'processed_DepMap_reversed_ranked_gene_essentiality.pkl')
                    else:
                        raise ValueError('Please set split_dict_path for custom split')

                    with open(file_dir, "rb") as f:
                        gene_ess_dict = pickle.load(f)
                        raked_genes = gene_ess_dict[self.dataset_name.split('-')[-1]]
                    
                    rng_pretrain = np.random.default_rng(seed=self.seed)
                    pretrain_ptbg_num = int(len(self.gene_ptbgs) * self.pretrain_ptbg_set_frac)
                    pretrain_ptbgs = raked_genes[:pretrain_ptbg_num]
                    pretrain_val_ptbgs = rng_pretrain.choice(pretrain_ptbgs, int(len(pretrain_ptbgs) * val_ptbg_set_frac), replace=False)
                    pretrain_train_ptbgs = np.setdiff1d(pretrain_ptbgs, pretrain_val_ptbgs)     
                elif 'simf' in split:
                    import pandas as pd
                    # pretrain & fine-tune with diverse proportion with different chem splitting
                    # pretrain
                    rng_pretrain = np.random.default_rng(seed=self.seed)
                    pretrain_ptbgs = rng_pretrain.choice(self.gene_ptbgs, int(len(self.gene_ptbgs) * self.pretrain_ptbg_set_frac), replace=False)
                    pretrain_val_ptbgs = rng_pretrain.choice(pretrain_ptbgs, int(len(pretrain_ptbgs) * val_ptbg_set_frac), replace=False)
                    pretrain_train_ptbgs = np.setdiff1d(pretrain_ptbgs, pretrain_val_ptbgs)  
                    # finetune
                    rng_finetune = np.random.default_rng(seed=self.seed)
                    cmap_cp_df = os.path.join(self.data_path, 'processed_CMAP_compound_info.csv')
                    id2smiles = (
                        cmap_cp_df
                        .dropna(subset=["pert_id", "canonical_smiles"])  
                        .drop_duplicates(subset=["pert_id"])              
                        .set_index("pert_id")["canonical_smiles"]
                        .to_dict()
                    )
                    method = split.split('-')[-1]
                    test_frac = 1-self.finetune_ptbg_set_frac
                    val_frac = self.finetune_ptbg_set_frac * val_ptbg_set_frac
                    train_frac = 1-test_frac-val_frac
                    train_ptbgs, val_ptbgs, test_ptbgs = molecule_split_deepchem(
                        data=self.chem_ptbgs,
                        id2smiles=id2smiles,
                        sizes=(train_frac, val_frac, test_frac),
                        method=method,
                        seed=self.seed,
                    )
                elif 'ts' in split:
                    # all genetic for pertrain, touchstone for finetune, discover for test
                    import pandas as pd
                    train_val_ptbgs = pd.read_csv(os.path.join(self.data_path, 'new_Touchstone.csv'))['Query ID'].unique().tolist()
                    val_ptbgs = np.random.choice(train_val_ptbgs, int(len(train_val_ptbgs) * val_ptbg_set_frac), replace=False)
                    train_ptbgs = np.setdiff1d(train_val_ptbgs, val_ptbgs)
                    test_ptbgs = np.setdiff1d(self.chem_ptbgs, train_val_ptbgs)

                    pretrain_val_ptbgs = np.random.choice(self.gene_ptbgs, int(len(self.gene_ptbgs) * val_ptbg_set_frac), replace=False)
                    pretrain_train_ptbgs = np.setdiff1d(self.gene_ptbgs, pretrain_val_ptbgs)
                                   
                else:
                    # pretrain on all genetic ptbgs, finetune on {1-test_frac} chemical ptbgs, test on the rest chemical ptbgs
                    test_frac = 1-self.train_ptbg_set_frac
                    test_ptbgs = np.random.choice(self.chem_ptbgs, int(len(self.chem_ptbgs) * test_frac), replace=False)
                    train_val_ptbgs = np.setdiff1d(self.chem_ptbgs, test_ptbgs)
                    val_ptbgs = np.random.choice(train_val_ptbgs, int(len(train_val_ptbgs) * val_ptbg_set_frac), replace=False)
                    train_ptbgs = np.setdiff1d(train_val_ptbgs, val_ptbgs)

                    pretrain_val_ptbgs = np.random.choice(self.gene_ptbgs, int(len(self.gene_ptbgs) * val_ptbg_set_frac), replace=False)
                    pretrain_train_ptbgs = np.setdiff1d(self.gene_ptbgs, pretrain_val_ptbgs)

                print_sys('Pretrain split composition:')
                print_sys('pretrain_train: ' + str(len(pretrain_train_ptbgs)))
                print_sys('pretrain_val: ' + str(len(pretrain_val_ptbgs)))
                print_sys('train: ' + str(len(train_ptbgs)))
                print_sys('val: ' + str(len(val_ptbgs)))
                print_sys('test: ' + str(len(test_ptbgs)))

                map_dict.update({x: 'train' for x in list(train_ptbgs)})
                map_dict.update({x: 'val' for x in list(val_ptbgs)})
                map_dict.update({x: 'test' for x in list(test_ptbgs)})
                set2conditions = {'train': list(train_ptbgs), 'val': list(val_ptbgs), 'test': list(test_ptbgs)}

                # if len(list(pretrain_train_ptbgs)) > 0:
                map_dict.update({x: 'pretrain_train' for x in list(pretrain_train_ptbgs)})
                map_dict.update({x: 'pretrain_val' for x in list(pretrain_val_ptbgs)})
                set2conditions.update({'pretrain_train': list(pretrain_train_ptbgs), 'pretrain_val': list(pretrain_val_ptbgs)})      

                self.adata.obs['split'] = self.adata.obs[self.perturbagen_col_name].map(map_dict)              
            
            else:
                raise ValueError(f'We do not support split: {split}.')
                 
            pickle.dump(set2conditions, open(split_path, "wb"))
            print_sys("Saving new splits at " + split_path)
            
        self.set2conditions = set2conditions
        # print_sys(f"self.set2conditions: {self.set2conditions}")
        print_sys("Done!")

    def get_dataloader(self, batch_size, test_batch_size = None):
        """
        Get dataloaders for training and testing

        Parameters
        ----------
        batch_size: int
            Batch size for training
        test_batch_size: int
            Batch size for testing

        Returns
        -------
        dict
            Dictionary of dataloaders

        """
        if test_batch_size is None:
            test_batch_size = batch_size
            
        self.node_map = {x: it for it, x in enumerate(self.gene_names)}
        # print_sys(f"node map: {self.node_map}")
       
        # Create cell graphs
        cell_graphs = {}
        # splits = ['train','val','test']
        splits = list(self.set2conditions.keys())
        for i in splits:
            cell_graphs[i] = []
            for p in self.set2conditions[i]:
                cell_graphs[i].extend(self.dataset_processed[p])

        print_sys("Creating dataloaders....")
        # Set up dataloaders
        self.dataloader = {}
        # chemical finetune
        if ('train' in splits) and (len(self.set2conditions['train'])>0):
            train_loader = DataLoader(cell_graphs['train'], batch_size=batch_size, shuffle=True, drop_last = True)
            self.dataloader.update({'train_loader': train_loader})
        if 'val' in splits and (len(self.set2conditions['val'])>0):
            val_loader = DataLoader(cell_graphs['val'], batch_size=batch_size, shuffle=True)
            self.dataloader.update({'val_loader': val_loader})
        if 'test' in splits and (len(self.set2conditions['test'])>0):
            test_loader = DataLoader(cell_graphs['test'], batch_size=batch_size, shuffle=False)
            self.dataloader.update({'test_loader': test_loader})
        # genetic pretrain
        if ('pretrain_train' in splits) and (len(self.set2conditions['pretrain_train'])>0):
            pretrain_train_loader = DataLoader(cell_graphs['pretrain_train'], batch_size=batch_size, shuffle=True, drop_last = True)
            self.dataloader.update({'pretrain_train_loader': pretrain_train_loader})
        if 'pretrain_val' in splits  and (len(self.set2conditions['pretrain_val'])>0):
            pretrain_val_loader = DataLoader(cell_graphs['pretrain_val'], batch_size=batch_size, shuffle=True)
            self.dataloader.update({'pretrain_val_loader': pretrain_val_loader})
        print_sys("Done!")

    def create_cell_graph(self, X, y, de_idx, pert, unipert_rep=None):
        """
        Create a cell graph from a given cell

        Parameters
        ----------
        X: np.ndarray
            Gene expression matrix
        y: np.ndarray
            Label vector
        de_idx: np.ndarray
            DE gene indices
        pert: str
            Perturbation category
        unipert_rep: np.ndarray
            UniPert representation

        Returns
        -------
        torch_geometric.data.Data
            Cell graph to be used in dataloader

        """

        feature_mat = torch.Tensor(X).reshape(-1, 1)
         # if pert_idx is None: pert_idx = [-1]
        return Data(x=feature_mat,            # sampled control
                    y=torch.Tensor(y).reshape(1,-1),        # perturbed
                    de_idx=de_idx, 
                    pert=pert,                # pert category
                    unipert_rep=unipert_rep,  # pert representation
                    )

    def create_cell_graph_dataset(self, 
                                  split_adata, 
                                  pert_category,
                                  unipert_rep,
                                  num_samples=1,
                                #   pert_type=None,
                                  ):
        """
        Combine cell graphs to create a dataset of cell graphs

        Parameters
        ----------
        split_adata: anndata.AnnData
            Annotated data matrix
        pert_category: str
            Perturbation category
        unipert_rep: str
            Pertbagen representation encoded by UniPert
        num_samples: int
            Number of samples to create per perturbed cell (i.e. number of
            control cells to map to each perturbed cell)

        Returns
        -------
        list
            List of cell graphs

        """

        num_de_genes = 20        
        adata_ = split_adata[split_adata.obs[self.perturbagen_col_name] == pert_category]
        if 'rank_genes_groups_cov_all' in adata_.uns:
            de_genes = adata_.uns['rank_genes_groups_cov_all']
            de = True
        else:
            de = False
            num_de_genes = 1
        Xs = []
        ys = []

        # When considering a non-control perturbation
        if pert_category != self.control_key:
            de_idx = [-1] * num_de_genes
            for i, cell_z in enumerate(adata_.X):
                if self.batch_key:
                    batch = adata_.obs[self.batch_key][i]
                    ctrl_data = self.ctrl_adata[self.ctrl_adata.obs[self.batch_key] == batch]
                    ctrl_samples = ctrl_data[np.random.randint(0, len(ctrl_data), num_samples), :]
                else:
                    ctrl_samples = self.ctrl_adata[np.random.randint(0, len(self.ctrl_adata), num_samples), :]

                for c in ctrl_samples.X:
                    Xs.append(c)
                    ys.append(cell_z)

        # When considering a control perturbation
        else:
            # pert_idx = None
            de_idx = [-1] * num_de_genes
            for cell_z in adata_.X:
                Xs.append(cell_z)
                ys.append(cell_z)

        # Create cell graphs
        cell_graphs = []
        for X, y in zip(Xs, ys):
            cell_graph = self.create_cell_graph(  
                                    X=X.toarray(),
                                    y=y.toarray(), 
                                    de_idx=de_idx, 
                                    pert=pert_category, 
                                    # pert_idx,
                                    unipert_rep=unipert_rep,
                                    )
            # print_sys(f"cell graph: {cell_graph}")
            cell_graphs.append(cell_graph)

        return cell_graphs

    def create_dataset_file(self):
        """
        Create dataset file for each perturbation condition
        """
        print_sys("Creating dataset file...")
        self.dataset_processed = {}
        for p in tqdm(self.adata.obs[self.perturbagen_col_name].unique()):
            if p != self.control_key:
                if '+' in p:
                    unipert_rep = [self.unipert_reps[i] for i in p.split('+') if i != self.control_key]
                else:
                    unipert_rep = [self.unipert_reps[p]]
                    # print_sys(f"unipert_rep: {unipert_rep}")
            else:
                unipert_rep = [None]

            self.dataset_processed[p] = self.create_cell_graph_dataset(self.adata, p, unipert_rep, num_samples=self.num_samples)
        print_sys("Done!")