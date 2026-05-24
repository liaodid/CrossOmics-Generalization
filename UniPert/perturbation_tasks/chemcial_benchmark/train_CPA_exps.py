# pip install cpa-tools==0.8.7
# nohup python train_CPA_exps.py > train_CPA_exps.log 2>&1 &

import sys

sys.path.append('/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/chemical_benchmark/CPA')
from CPA.cpa_adapted import CPA

import numpy as np
import os
import pickle
import scanpy as sc
import argparse


parser = argparse.ArgumentParser(description='Train CPA-based model with a given split key and dataset.')
parser.add_argument('--model', type=str, default='chemCPA', help='The model type.', choices=['CPA', 'chemCPA', 'UniPert', 'UniMol', 'KPGT'])
parser.add_argument('--dataset', type=str, default='sciplex3_HDAC', help='The dataset for the CPA model.', choices=['sciplex3_HDAC', 'sciplex3_all'])  
parser.add_argument('--split_id', type=str, default='1', help='The split id for the CPA model.')
parser.add_argument('--batch_size', type=int, default='512', help='The batch size for the CPA model.')
parser.add_argument('--save_dir', type=str, default='/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/chemical_benchmark/saved_models/test', help='Directory to store results')

args = parser.parse_args()

MODEL = args.model
DATA_NAME = args.dataset
SPLIT_ID = args.split_id   
SPLIT_KEY = 'loo_split'+SPLIT_ID if DATA_NAME == 'sciplex3_HDAC' else 'ood_split'+SPLIT_ID 
output_dir = os.path.join(args.save_dir, str(DATA_NAME), str(MODEL), str(SPLIT_KEY))
os.makedirs(output_dir, exist_ok=True) 


## Set drug embeddings
if MODEL == 'CPA':
    use_rdkit_embeddings = False
    emb_dict = None
elif MODEL == 'chemCPA':        # ECPF4
    use_rdkit_embeddings = True
    emb_dict = None
elif MODEL == 'UniPert':
    use_rdkit_embeddings = True
    with open("/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/current_model/unipert_reps.pkl", 'rb') as f:
        emb_dict = pickle.load(f)
elif MODEL == 'UniMol':
    use_rdkit_embeddings = True
    with open("/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/ref_unimol_embs.pkl", 'rb') as f:
        emb_dict = pickle.load(f)
elif MODEL == 'KPGT':
    use_rdkit_embeddings = True
    with open("/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/ref_kpgt_embs.pkl", 'rb') as f:
        emb_dict = pickle.load(f)
else:
    raise ValueError('Model not supported.')

## Data Loading
if  DATA_NAME == 'sciplex3_HDAC':
    data_path = '/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/chemcial_benchmark/data/processed_sciPlex3_HDAC.h5ad'
    adata = sc.read(data_path)
elif DATA_NAME == 'sciplex3_all':
    data_path = '/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/chemcial_benchmark/data/processed_sciPlex3_all.h5ad'
    adata = sc.read(data_path)
else:
    raise ValueError('Dataset not supported.')


## print params
print('-------------------NEW EXP---------------------')
print(f'dataset : {DATA_NAME}')
print(f'model_name : {MODEL}')
print(f'split : {SPLIT_KEY}')
print('-----------------------------------------------')


## Data setup
CPA.setup_anndata(adata, 
                    perturbation_key='condition',
                    dosage_key='dose_val',
                    control_group='control',
                    batch_key=None,
                    smiles_key='SMILES' if use_rdkit_embeddings else None,  
                    is_count_data=False,
                    categorical_covariate_keys=['cell_type'],
                    deg_uns_key='rank_genes_groups_cov',
                    deg_uns_cat_key='cov_drug_dose_name',
                    max_comb_len=1,
                    )

## Training CPA
# hparam settings followed from https://cpa-tools.readthedocs.io/en/stable/tutorials/
ae_hparams = {'n_latent': 64,
    'recon_loss': 'nb',
    'doser_type': 'linear',
    'n_hidden_encoder': 256,
    'n_layers_encoder': 3,
    'n_hidden_decoder': 512,
    'n_layers_decoder': 2,
    'use_batch_norm_encoder': True,
    'use_layer_norm_encoder': False,
    'use_batch_norm_decoder': True,
    'use_layer_norm_decoder': False,
    'dropout_rate_encoder': 0.25,
    'dropout_rate_decoder': 0.25,
    'variational': False,
    'seed': 6478
    }

trainer_params = {'n_epochs_kl_warmup': None,
    'n_epochs_pretrain_ae': 50,
    'n_epochs_adv_warmup': 100,
    'n_epochs_mixup_warmup': 10,
    'mixup_alpha': 0.1,
    'adv_steps': None,
    'n_hidden_adv': 128,
    'n_layers_adv': 3,
    'use_batch_norm_adv': False,
    'use_layer_norm_adv': False,
    'dropout_rate_adv': 0.2,
    'reg_adv': 10.0,
    'pen_adv': 0.1,
    'lr': 0.0003,
    'wd': 4e-07,
    'adv_lr': 0.0003,
    'adv_wd': 4e-07,
    'adv_loss': 'cce',
    'doser_lr': 0.0003,
    'doser_wd': 4e-07,
    'do_clip_grad': False,
    'gradient_clip_value': 1.0,
    'step_size_lr': 10
    }

## Model instantiation
if ('loo' in args.split_key) or ('ood' in args.split_key)or ('MEC' in args.split_key):
    test_split = 'ood'
else:
    test_split = 'test'

model = CPA(adata=adata, 
            split_key=SPLIT_KEY,
            train_split='train',
            valid_split='valid',
            test_split=test_split,
            use_rdkit_embeddings=use_rdkit_embeddings,      # modified
            drug_emb_dict=emb_dict,                         # modified
            **ae_hparams,
            )

## Training CPA
model.train(max_epochs=2000,     
            use_gpu=True, 
            batch_size=args.batch_size,    
            plan_kwargs=trainer_params,
            early_stopping_patience=10,
            check_val_every_n_epoch=5,
            save_path=output_dir,
           )

print('Train Done!')


