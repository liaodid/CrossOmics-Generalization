from copy import deepcopy
import os
import pickle
import numpy as np
import torch
import torch.optim as optim
import torch.nn as nn
from torch.optim.lr_scheduler import StepLR

from .model import GEARS_Model
from .inference import evaluate, compute_metrics, deeper_analysis, \
                  non_dropout_analysis
from .utils import loss_fct, uncertainty_loss_fct, parse_any_pert, \
                  get_similarity_network, print_sys, GeneSimNetwork, \
                  create_cell_graph_dataset_for_prediction, get_mean_control, \
                  get_GI_genes_idx, get_GI_params

torch.manual_seed(0)

import warnings
warnings.filterwarnings("ignore")

class GEARS:
    """
    GEARS base model class
    """

    def __init__(self, 
                 pert_data, 
                 device = 'cuda',
                 weight_bias_track = False, 
                 proj_name = 'GEARS', 
                 exp_name = 'GEARS',
                 save_path = None,
                 ):
        """
        Initialize GEARS model

        Parameters
        ----------
        pert_data: PertData object
            dataloader for perturbation data
        device: str
            Device to run the model on. Default: 'cuda'
        weight_bias_track: bool
            Whether to track performance on wandb. Default: False
        proj_name: str
            Project name for wandb. Default: 'GEARS'
        exp_name: str
            Experiment name for wandb. Default: 'GEARS'

        Returns
        -------
        None

        """

        self.weight_bias_track = weight_bias_track
        
        if self.weight_bias_track:
            import wandb
            wandb.init(project=proj_name, 
                       name=exp_name, 
                       dir=save_path
            )       
            self.wandb = wandb
        else:
            self.wandb = None
        
        self.device = device
        self.config = None
        
        self.dataloader = pert_data.dataloader
        self.adata = pert_data.adata
        self.node_map = pert_data.node_map
        # self.node_map_pert = pert_data.node_map_pert
        self.data_path = pert_data.dataset_path
        self.dataset_name = pert_data.dataset_name
        self.split = pert_data.split
        self.seed = pert_data.seed
        self.train_ptbg_set_frac = pert_data.train_ptbg_set_frac
        self.pretrain_ptbg_set_frac = pert_data.pretrain_ptbg_set_frac
        self.finetune_ptbg_set_frac = pert_data.finetune_ptbg_set_frac
        self.set2conditions = pert_data.set2conditions
        # self.subgroup = pert_data.subgroup
        self.gene_list = pert_data.gene_names
        # self.pert_list = pert_data.pert_names.tolist()
        self.chem_ptbgs = pert_data.chem_ptbgs
        self.gene_ptbgs = pert_data.gene_ptbgs
        self.all_ptbgs = pert_data.all_ptbgs
        self.num_genes = len(self.gene_list)
        self.num_perts = len(self.gene_ptbgs) + len(self.chem_ptbgs)
        # self.default_pert_graph = pert_data.default_pert_graph
        self.saved_pred = {}
        self.saved_logvar_sum = {}
        
        self.ctrl_expression = torch.tensor(
            np.mean(self.adata.X[self.adata.obs.condition == 'ctrl'],
                    axis=0)).reshape(-1, ).to(self.device)
        # pert_full_id2pert = dict(self.adata.obs[['condition_name', 'condition']].values)
        # self.dict_filter = {pert_full_id2pert[i]: j for i, j in
        #                     self.adata.uns['non_zeros_gene_idx'].items() if
        #                     i in pert_full_id2pert}
        self.dict_filter = {i: np.arange(self.adata.n_vars) for i in self.all_ptbgs}
        self.ctrl_adata = self.adata[self.adata.obs['condition'] == 'ctrl']
        
        # gene_dict = {g:i for i,g in enumerate(self.gene_list)}
        # self.pert2gene = {p: gene_dict[pert] for p, pert in
        #                   enumerate(self.pert_list) if pert in self.gene_list}

    def tunable_parameters(self):
        """
        Return the tunable parameters of the model

        Returns
        -------
        dict
            Tunable parameters of the model

        """

        return {'hidden_size': 'hidden dimension, default 64',
                'num_go_gnn_layers': 'number of GNN layers for GO graph, default 1',
                'num_gene_gnn_layers': 'number of GNN layers for co-expression gene graph, default 1',
                'decoder_hidden_size': 'hidden dimension for gene-specific decoder, default 16',
                'num_similar_genes_go_graph': 'number of maximum similar K genes in the GO graph, default 20',
                'num_similar_genes_co_express_graph': 'number of maximum similar K genes in the co expression graph, default 20',
                'coexpress_threshold': 'pearson correlation threshold when constructing coexpression graph, default 0.4',
                'uncertainty': 'whether or not to turn on uncertainty mode, default False',
                'uncertainty_reg': 'regularization term to balance uncertainty loss and prediction loss, default 1',
                'direction_lambda': 'regularization term to balance direction loss and prediction loss, default 1'
               }
    
    def model_initialize(self, hidden_size = 64,
                         num_go_gnn_layers = 1, 
                         num_gene_gnn_layers = 1,
                         decoder_hidden_size = 16,
                         num_similar_genes_go_graph = 20,
                         num_similar_genes_co_express_graph = 20,                    
                         coexpress_threshold = 0.4,
                         uncertainty = False, 
                         uncertainty_reg = 1,
                         direction_lambda = 1e-1,
                        #  G_go = None,
                        #  G_go_weight = None,
                         G_coexpress = None,
                         G_coexpress_weight = None,
                         no_perturb = False, 
                        #  model_name = None,      # mod
                        ):
        """
        Initialize the model

        Parameters
        ----------
        hidden_size: int
            hidden dimension, default 64
        num_go_gnn_layers: int
            number of GNN layers for GO graph, default 1
        num_gene_gnn_layers: int
            number of GNN layers for co-expression gene graph, default 1
        decoder_hidden_size: int
            hidden dimension for gene-specific decoder, default 16
        num_similar_genes_go_graph: int
            number of maximum similar K genes in the GO graph, default 20
        num_similar_genes_co_express_graph: int
            number of maximum similar K genes in the co expression graph, default 20
        coexpress_threshold: float
            pearson correlation threshold when constructing coexpression graph, default 0.4
        uncertainty: bool
            whether or not to turn on uncertainty mode, default False
        uncertainty_reg: float
            regularization term to balance uncertainty loss and prediction loss, default 1
        direction_lambda: float
            regularization term to balance direction loss and prediction loss, default 1
        G_go: scipy.sparse.csr_matrix
            GO graph, default None
        G_go_weight: scipy.sparse.csr_matrix
            GO graph edge weights, default None
        G_coexpress: scipy.sparse.csr_matrix
            co-expression graph, default None
        G_coexpress_weight: scipy.sparse.csr_matrix
            co-expression graph edge weights, default None
        no_perturb: bool
            predict no perturbation condition, default False

        Returns
        -------
        None
        """
        
        self.config = {'hidden_size': hidden_size,
                       'num_go_gnn_layers' : num_go_gnn_layers, 
                       'num_gene_gnn_layers' : num_gene_gnn_layers,
                       'decoder_hidden_size' : decoder_hidden_size,
                       'num_similar_genes_go_graph' : num_similar_genes_go_graph,
                       'num_similar_genes_co_express_graph' : num_similar_genes_co_express_graph,
                       'coexpress_threshold': coexpress_threshold,
                       'uncertainty' : uncertainty, 
                       'uncertainty_reg' : uncertainty_reg,
                       'direction_lambda' : direction_lambda,
                    #    'G_go': G_go,
                    #    'G_go_weight': G_go_weight,
                       'G_coexpress': G_coexpress,
                       'G_coexpress_weight': G_coexpress_weight,
                       'device': self.device,
                       'num_genes': self.num_genes,
                       'num_perts': self.num_perts,
                       'no_perturb': no_perturb,
                      }
        
        if self.wandb:
            self.wandb.config.update(self.config)
        
        if self.config['G_coexpress'] is None:
            ## calculating co expression similarity graph
            edge_list = get_similarity_network(network_type='co-express',
                                               adata=self.adata,
                                               threshold=coexpress_threshold,
                                               k=num_similar_genes_co_express_graph,
                                               data_path=self.data_path,
                                               data_name=self.dataset_name,
                                            #    split=self.split.split('_')[0].split('-')[-1], 
                                               split=('-').join(self.split.split('-')[2:]),
                                               seed=self.seed,
                                               pretrain_gene_set_size=self.pretrain_ptbg_set_frac,
                                               train_gene_set_size=self.train_ptbg_set_frac,
                                               set2conditions=self.set2conditions)

            sim_network = GeneSimNetwork(edge_list, self.gene_list, node_map = self.node_map)
            self.config['G_coexpress'] = sim_network.edge_index
            self.config['G_coexpress_weight'] = sim_network.edge_weight
    

        self.model = GEARS_Model(self.config).to(self.device)
        self.best_model = deepcopy(self.model)     

    def load_pretrained(self, path, filename = 'model'):
        """
        Load pretrained model

        Parameters
        ----------
        path: str
            path to the pretrained model

        Returns
        -------
        None
        """

        with open(os.path.join(path, 'config.pkl'), 'rb') as f:
            config = pickle.load(f)
        
        if 'device' in config:
            del config['device']
        if 'num_genes' in config:
            del config['num_genes']
        if 'num_perts' in config:
            del config['num_perts']
        
        self.model_initialize(**config)
        self.config = config
        
        state_dict = torch.load(os.path.join(path, f'{filename}.pt'), map_location = torch.device('cpu'))
        if next(iter(state_dict))[:7] == 'module.':
            # the pretrained model is from data-parallel module
            from collections import OrderedDict
            new_state_dict = OrderedDict()
            for k, v in state_dict.items():
                name = k[7:] # remove `module.`
                new_state_dict[name] = v
            state_dict = new_state_dict

        # Ignore loading for self.pert_emb
        state_dict.pop('pert_emb.weight', None) 
        
        self.model.load_state_dict(state_dict)
        self.model = self.model.to(self.device)
        self.best_model = self.model
    
    def save_model(self, path, filename = 'model'):
        """
        Save the model

        Parameters
        ----------
        path: str
            path to save the model

        Returns
        -------
        None

        """
        if not os.path.exists(path):
            os.mkdir(path)
        
        if self.config is None:
            raise ValueError('No model is initialized...')
        
        with open(os.path.join(path, 'config.pkl'), 'wb') as f:
            pickle.dump(self.config, f)
       
        torch.save(self.best_model.state_dict(), os.path.join(path, f'{filename}.pt'))
    
    def new_predict(self, pert_list, unipert_rep_dict):
        """
        Predict the transcriptome given a list of genes/gene combinations being
        perturbed

        Parameters
        ----------
        pert_list: list
            list of single perturbagen to be perturbed
        unipert_rep_dict: dict
            dictionary of perturbagen representation

        Returns
        -------
        results_pred: dict
            dictionary of predicted transcriptome
        results_logvar: dict
            dictionary of uncertainty score

        """
        ## given a list of single/combo genes, return the transcriptome
        ## if uncertainty mode is on, also return uncertainty score.
        
        self.ctrl_adata = self.adata[self.adata.obs['condition'] == 'ctrl']

        if self.config['uncertainty']:
            results_logvar = {}
            
        self.best_model = self.best_model.to(self.device)
        self.best_model.eval()
        results_pred = {}
        results_logvar_sum = {}
        
        from torch_geometric.data import DataLoader
        from tqdm import tqdm
        for pert in tqdm(pert_list):
            if pert not in unipert_rep_dict.keys():
                print(f"No unipert representation of [{pert}] in given dict.")
                continue
            else:
                pert_emb = unipert_rep_dict[pert]
                pert_emb = pert_emb / np.linalg.norm(pert_emb) if np.linalg.norm(pert_emb) != 0 else pert_emb

            from torch_geometric.data import Data
            Xs = self.ctrl_adata[np.random.randint(0, len(self.ctrl_adata), 300), :].X.toarray()
            # Create cell graphs
            cg = [Data(x=torch.Tensor(X).T, y=None, de_idx=[1], pert=pert, unipert_rep=[pert_emb]).to(self.device) for X in Xs]
            loader = DataLoader(cg, 300, shuffle = False)
            batch = next(iter(loader))
            batch.to(self.device)

            with torch.no_grad():
                p = self.best_model(batch)
            results_pred[pert] = np.mean(p.detach().cpu().numpy(), axis = 0)
                
        self.saved_pred.update(results_pred)
        return results_pred
        
    def GI_predict(self, combo, GI_genes_file='./genes_with_hi_mean.npy'):
        """
        Predict the GI scores following perturbation of a given gene combination

        Parameters
        ----------
        combo: list
            list of genes to be perturbed
        GI_genes_file: str
            path to the file containing genes with high mean expression

        Returns
        -------
        GI scores for the given combinatorial perturbation based on GEARS
        predictions

        """

        ## if uncertainty mode is on, also return uncertainty score.
        try:
            # If prediction is already saved, then skip inference
            pred = {}
            pred[combo[0]] = self.saved_pred[combo[0]]
            pred[combo[1]] = self.saved_pred[combo[1]]
            pred['_'.join(combo)] = self.saved_pred['_'.join(combo)]
        except:
            if self.config['uncertainty']:
                pred = self.predict([[combo[0]], [combo[1]], combo])[0]
            else:
                pred = self.predict([[combo[0]], [combo[1]], combo])

        mean_control = get_mean_control(self.adata).values  
        pred = {p:pred[p]-mean_control for p in pred} 

        if GI_genes_file is not None:
            # If focussing on a specific subset of genes for calculating metrics
            GI_genes_idx = get_GI_genes_idx(self.adata, GI_genes_file)       
        else:
            GI_genes_idx = np.arange(len(self.adata.var.gene_name.values))
            
        pred = {p:pred[p][GI_genes_idx] for p in pred}
        return get_GI_params(pred, combo)
    
    def plot_perturbation(self, query, save_file = None):
        """
        Plot the perturbation graph

        Parameters
        ----------
        query: str
            condition to be queried
        save_file: str
            path to save the plot

        Returns
        -------
        None

        """

        import seaborn as sns
        import matplotlib.pyplot as plt
        
        sns.set_theme(style="ticks", rc={"axes.facecolor": (0, 0, 0, 0)}, font_scale=1.5)

        adata = self.adata
        gene2idx = self.node_map
        cond2name = dict(adata.obs[['condition', 'condition_name']].values)
        gene_raw2id = dict(zip(adata.var.index.values, adata.var.gene_name.values))

        de_idx = [gene2idx[gene_raw2id[i]] for i in
                  adata.uns['top_non_dropout_de_20'][cond2name[query]]]
        genes = [gene_raw2id[i] for i in
                 adata.uns['top_non_dropout_de_20'][cond2name[query]]]
        truth = adata[adata.obs.condition == query].X.toarray()[:, de_idx]
        
        query_ = [q for q in query.split('+') if q != 'ctrl']
        pred = self.predict([query_])['_'.join(query_)][de_idx]
        ctrl_means = adata[adata.obs['condition'] == 'ctrl'].to_df().mean()[
            de_idx].values

        pred = pred - ctrl_means
        truth = truth - ctrl_means
        
        plt.figure(figsize=[16.5,4.5])
        plt.title(query)
        plt.boxplot(truth, showfliers=False,
                    medianprops = dict(linewidth=0))    

        for i in range(pred.shape[0]):
            _ = plt.scatter(i+1, pred[i], color='red')

        plt.axhline(0, linestyle="dashed", color = 'green')

        ax = plt.gca()
        ax.xaxis.set_ticklabels(genes, rotation = 90)

        plt.ylabel("Change in Gene Expression over Control",labelpad=10)
        plt.tick_params(axis='x', which='major', pad=5)
        plt.tick_params(axis='y', which='major', pad=5)
        sns.despine()
        
        if save_file:
            plt.savefig(save_file, bbox_inches='tight')
        plt.show()
    
    def new_train(self, 
              epochs = 20, 
              lr = 1e-3,
              weight_decay = 5e-4,
              train_loader = None,
              val_loader = None,
              test_loader = None,
              GT = False,
             ):
        """
        Train the model

        Parameters
        ----------
        epochs: int
            number of epochs to train
        lr: float
            learning rate
        weight_decay: float
            weight decay

        Returns
        -------
        None

        """
        self.model = self.model.to(self.device)
        best_model = deepcopy(self.model)

        optimizer = optim.Adam(self.model.parameters(), lr=lr, weight_decay = weight_decay)
        scheduler = StepLR(optimizer, step_size=1, gamma=0.5)
        min_val = np.inf
        print_sys('Start Training...')
        for epoch in range(epochs):
            self.model.train()
            for step, batch in enumerate(train_loader):
                batch.to(self.device)
                optimizer.zero_grad()
                y = batch.y
                pred = self.model(batch)
                loss = loss_fct(pred, y, batch.pert,
                            ctrl = self.ctrl_expression, 
                            dict_filter = self.dict_filter,
                            direction_lambda = self.config['direction_lambda'])
                loss.backward()
                nn.utils.clip_grad_value_(self.model.parameters(), clip_value=1.0)
                optimizer.step()

                if self.wandb: 
                    self.wandb.log({'training_loss': loss.item()}, commit=True)

                if step % 10 == 0:
                    log = "Epoch {} Step {} Loss: {:.4f}" 
                    print_sys(log.format(epoch + 1, step + 1, loss.item()))

            scheduler.step()
            # Evaluate model performance on train and val set
            train_res = evaluate(train_loader, self.model, self.config['uncertainty'], self.device)
            val_res = evaluate(val_loader, self.model, self.config['uncertainty'], self.device)

            train_metrics, _ = compute_metrics(train_res, ground_truth=GT)
            val_metrics, _ = compute_metrics(val_res, ground_truth=GT)

            # Print epoch performance
            print_sys("Epoch {}: ".format(epoch + 1))
            log = "Train Overall MSE: {:.4f}\n" \
                "Validation Overall MSE: {:.4f}. "
            print_sys(log.format(train_metrics['mse'], 
                                val_metrics['mse']
                                ))
            
            if self.wandb:
                metrics = ['mse', 'pearson']
                for m in metrics:
                    self.wandb.log({'pretrain_train_' + m: train_metrics[m],
                                    'pretrain_val_'+m: val_metrics[m],
                                    }, commit=True)
    
            # Select best model
            if val_metrics['mse'] < min_val:
                min_val = val_metrics['mse']
                best_model = deepcopy(self.model)
                
        self.best_model = best_model   

        if test_loader is None:
            print_sys('Done! No test dataloader detected.')
            return
            
        # Model testing
        test_loader = self.dataloader['test_loader']
        print_sys("Start Testing...")
        test_res = evaluate(test_loader, self.best_model, self.config['uncertainty'], self.device)
        test_metrics, _ = compute_metrics(test_res, ground_truth=GT)    
        log = "Best performing model: Test MSE: {:.4f}"
        print_sys(log.format(test_metrics['mse']))
        
        if self.wandb:
            metrics = ['mse', 'pearson']
            for m in metrics:
                self.wandb.log({'test_' + m: test_metrics[m]}, commit=True)
        
        print_sys('Done!')