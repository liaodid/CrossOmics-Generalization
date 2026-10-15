import argparse
import sys
sys.path.append('../UniPert')
from unipert import UniPert


### set hyperparameters
parser = argparse.ArgumentParser(description='Train UniPert model with specified hyperparameters.')
# model hyperparameters
parser.add_argument('--version', type=str, default='v0')
parser.add_argument('--exp_name', type=str, default='unipert_test')
parser.add_argument('--gnn_type', type=str, default='GCN')
parser.add_argument('--layer_num', type=int, default=2, choices=[1, 2, 3])
parser.add_argument('--out_dim', type=int, default=256, choices=[64, 128, 256])
parser.add_argument('--target_embedder', type=str, default='ESM2', choices=['PseAAC', 'ESM2', 'OntoProtein'])
parser.add_argument('--compound_embedder', type=str, default='ECFP4', choices=['ECFP4', 'UniMol', 'KPGT'])
# training hyperparameters
parser.add_argument('--seed', type=int, default=2024)             
parser.add_argument('--epochs1', type=int, default=1)         
parser.add_argument('--epochs2', type=int, default=1)          
parser.add_argument('--bs', type=int, default=512)                
parser.add_argument('--lr1', type=float, default=5e-3)            
parser.add_argument('--lr2', type=float, default=5e-3, choices=[1e-3, 5e-3, 1e-2])            
parser.add_argument('--wd', type=float, default=1e-5)             
parser.add_argument('--mm', type=float, default=0.99)             
parser.add_argument('--accumulation_steps', type=int, default=1)     
parser.add_argument('--drop_edge_p_1', type=float, default=0.1)   
parser.add_argument('--drop_feat_p_1', type=float, default=0.3)   
parser.add_argument('--drop_edge_p_2', type=float, default=0.3)   
parser.add_argument('--drop_feat_p_2', type=float, default=0.1)   

args = parser.parse_args()
if 'test' in args.exp_name: 
    argp
    args.epochs1 = 10
    args.epochs2 = 3
    
model_hparams = {
    'version': args.version,
    'out_dim': args.out_dim,
    'gnn_type': args.gnn_type,
    'layer_num': args.layer_num,
    'target_embedder': args.target_embedder,
    'compound_embedder': args.compound_embedder,
}

train_hparams = {
    'exp_name': args.exp_name,
    'seed': args.seed,
    'epochs1': args.epochs1,
    'epochs2': args.epochs2,
    'bs': args.bs,
    'lr1': args.lr1,
    'lr2': args.lr2,
    'wd': args.wd,
    'mm': args.mm,
    # 'ctc_weight': args.ctc_weight, 
    'accumulation_steps': args.accumulation_steps,
    'drop_edge_p_1': args.drop_edge_p_1,
    'drop_feat_p_1': args.drop_feat_p_1,
    'drop_edge_p_2': args.drop_edge_p_2,
    'drop_feat_p_2': args.drop_feat_p_2,
}


### train model
unipert = UniPert(data_dir='../UniPert/data', model_hparams=model_hparams)
if not unipert.loaded:
    unipert.train(train_hparams=train_hparams)
    print(f"Experiment training completed successfully!")
# unipert.encode_ref_perturbagens()

