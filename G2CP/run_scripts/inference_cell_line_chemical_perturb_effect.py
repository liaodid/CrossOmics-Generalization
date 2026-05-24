# nohup python inference_cell_line_chemical_perturb_effect.py > inference_ESR1_drugs.log 2>&1 &


import sys
import os
import argparse
import numpy as np
import random
import torch
import pickle
import scanpy as sc
import pandas as pd
import anndata as ad
import concurrent
from concurrent.futures import ProcessPoolExecutor

### load real effect sdata
benchmark_genes = []

for data_name in ['MCF7', 'A549', 'HT29', 'A375', 'PC3']:
    # print(f'===  {data_name}  ===')
    adata_path = os.path.join(f'/data/liyiming/Project/UniPert-G2CP_reproduce/G2CP/data/LINCS/{data_name}/{data_name}_gene_chem_ctrl_adata.h5ad')
    adata = ad.read_h5ad(adata_path, 'r')
    var = adata.var
    break

### inference effect adata
unipert_rep_dict = pickle.load(open('/data/liyiming/Project/UniPert-G2CP_reproduce/G2CP/results/ER_case_unipert_reps.pkl', 'rb'))
ER_agonist = '17-beta-estradiol|coumestrol|daidzein|diarylpropionitrile|dienestrol|diethylstilbestrol|equilin|estradiol|estradiol-benzoate|estradiol-cypionate|estradiol-valerate|estriol|estrone|estropipate|ethinyl-estradiol|mestranol|PPT'.split('|')
ER_drugs = ['Estradiol', 'Tamoxifen', 'Raloxifene', 'Elacestrant', 'Fulvestrant']
query = ER_agonist + ER_drugs


## load model
sys.path.append('/data/liyiming/Project/UniPert-G2CP_reproduce/G2CP/backbone_model/GEARS')
from gears import PertData, GEARS
from gears.utils import print_sys

datasets = ['LINCS-A549', 'LINCS-A375', 'LINCS-MCF7', 'LINCS-PC3', 'LINCS-HT29']
TRAIN_MODE = 'pretrain-finetune-ts'
SEED = 0
TRAIN_FRAC = 0.0
VAL_FRAC = 0.1
BATCH_SIZE = 32
LR = 1e-3
EPOCHS = 20
WEIGHT_DECAY = 5e-4
NO_PERTURB = False

save_path = '/data/liyiming/Project/UniPert-G2CP_reproduce/G2CP/saved_models/LINCS_ts'
exp_trail = 'new_' + TRAIN_MODE+'_'+str(SEED)+'_'+str(TRAIN_FRAC)
model_list = []
dataloader_list = []

def process_cell_line(cell_line):
    print(f"======================={cell_line}=======================")
    # prepare data
    pert_data = PertData(data_path='/data/liyiming/Project/UniPert-G2CP_reproduce/G2CP/data')
    pert_data.load(
        data_name=cell_line,
        pert_type_col_name = 'pert_type',
        perturbagen_col_name = 'condition',
        control_key = 'ctrl'
        )
    pert_data.prepare_split(
        split=TRAIN_MODE, 
        seed=SEED, 
        train_ptbg_set_frac = TRAIN_FRAC,       
        val_ptbg_set_frac = VAL_FRAC,
        )
    pert_data.get_dataloader(
        batch_size=BATCH_SIZE,
        test_batch_size=128,
        )

    # prepare model
    model_path = os.path.join(save_path, str(cell_line), exp_trail)
    exp_name = model_path.split('/')[-1]
    gears_model = GEARS(
        pert_data, 
        device='cuda:0', 
        weight_bias_track=False, 
        proj_name=str(cell_line), 
        exp_name=exp_trail+'_'+exp_name,
        save_path=model_path,
        )
    # load model
    gears_model.load_pretrained(model_path, 'finetune_model')

    # inference 
    print(f'Start inference for {cell_line}...')
    res = gears_model.new_predict(query, unipert_rep_dict)
    print(f'Finish inference for {cell_line}.')
    return cell_line, res

    
with ProcessPoolExecutor() as executor:
    futures = {executor.submit(process_cell_line, cell_line): cell_line for cell_line in datasets}
    for future in concurrent.futures.as_completed(futures):
        cell_line, res = future.result()

        adata = ad.AnnData(X=np.array(list(res.values())))  
        adata.obs['condition'] = list(res.keys())  
        adata.var = var 
        # save inerference adata
        adata.write_h5ad(f'/data/liyiming/Project/UniPert-G2CP_reproduce/G2CP/results/in_silico_chemical_perturb_effect/{cell_line}_in_silico_effect_adata.h5ad')
