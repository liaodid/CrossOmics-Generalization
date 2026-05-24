import sys
import os
import argparse
import numpy as np
import random
import torch

sys.path.append('/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/genetic_benchmark/GEARS-adapted')
from gears import PertData, GEARS
from gears.utils import print_sys

# init and parse args
parser = argparse.ArgumentParser(description='GEARS Experiment Runner')
parser.add_argument('--dataset', type=str, default='dixit', help='Dataset to use for training', choices=['dixit', 'norman'])
parser.add_argument('--model_name', type=str, default='PseAAC', help='Model name', choices=['No-Perturb', 'GEARS', 'UniPert', 'ESM2', 'OntoProtein', 'PseAAC'])
parser.add_argument('--seed', type=int, default=2, help='Random seed for the experiment')
parser.add_argument('--train_frac', type=float, default=0.75, help='Fraction of trainning gene set')
parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
parser.add_argument('--lr', type=float, default=1e-3, help='Learning rate')
parser.add_argument('--epochs', type=int, default=20, help='Number of epochs')
parser.add_argument('--save_dir', type=str, default='/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/genetic_benchmark/saved_models/test', help='Directory to store results')
parser.add_argument('--unipert_model_dir', type=str, default="/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/current_model/")
args = parser.parse_args()

DATASET = args.dataset
MODEL_NAME = args.model_name
SEED = args.seed
TRAIN_FRAC = args.train_frac
BATCH_SIZE = args.batch_size
LR = args.lr
EPOCHS = args.epochs
NO_PERTURB = True if MODEL_NAME == 'No-Perturb' else False

exp_trail = MODEL_NAME+'_'+str(SEED) if TRAIN_FRAC == 0.75 else MODEL_NAME+'_'+str(SEED)+'_'+str(TRAIN_FRAC)
save_path = os.path.join(args.save_dir, str(DATASET), exp_trail)
os.makedirs(save_path, exist_ok=True) 
exp_name = args.save_dir.split('/')[-1]

# set seed
random_seed = SEED
random.seed(random_seed)
np.random.seed(random_seed)
torch.manual_seed(random_seed)
torch.cuda.manual_seed(random_seed)
torch.cuda.manual_seed_all(random_seed)
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True
os.environ['PYTHONHUSHSEED'] = str(random_seed)

# set model
unipert_path = '/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert'
unipert_data_path = '/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/data'
if MODEL_NAME == 'UniPert':
    sys.path.append(unipert_path)
    from unipert import UniPert
    pert_encoder = UniPert(data_dir=unipert_data_path, 
                      model_hparams = {'save_dir': args.unipert_model_dir})
elif MODEL_NAME == 'ESM2':  
    sys.path.append(unipert_path)
    from unipert import TargetEmbedder_ESM2
    pert_encoder = TargetEmbedder_ESM2(data_dir=unipert_data_path)
elif MODEL_NAME == 'OntoProtein':  
    sys.path.append(unipert_path)
    from unipert import TargetEmbedder_OntoProtein
    pert_encoder = TargetEmbedder_OntoProtein(data_dir=unipert_data_path)
elif MODEL_NAME == 'PseAAC':  
    sys.path.append(unipert_path)
    from unipert import TargetEmbedder_PseAAC
    pert_encoder = TargetEmbedder_PseAAC(data_dir=unipert_data_path)
elif MODEL_NAME == 'GEARS' or MODEL_NAME == 'No-Perturb':  
    pert_encoder = None     # keep raw GO graph embedding
else:
    raise ValueError('Model name should be [GEARS, UniPert, ESM2, OntoProtein, PseAAC, No-Perturb].')

# print params
print_sys('-------------------NEW EXP---------------------')
print_sys(f'dataset : {DATASET}')
print_sys(f'model_name : {MODEL_NAME}')
print_sys(f'seed : {SEED}')
print_sys(f'epochs : {EPOCHS}')
print_sys(f'lr : {LR}')
print_sys(f'batch_size : {BATCH_SIZE}')
print_sys(f'train_frac : {TRAIN_FRAC}')
print_sys(f'exp_name : {exp_name}')
print_sys('-----------------------------------------------')

# prepare data
pert_data = PertData(data_path='/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/genetic_benchmark/data',
                     pert_encoder_type=MODEL_NAME,
                     pert_encoder=pert_encoder,
                     )
pert_data.load(data_name=DATASET)
pert_data.prepare_split(split='simulation', 
                        seed=SEED, 
                        train_gene_set_size=TRAIN_FRAC,
                        combo_seen2_train_frac=TRAIN_FRAC,
                        )
pert_data.get_dataloader(batch_size=BATCH_SIZE,
                         test_batch_size=128,
                        )

# prepare model
gears_model = GEARS(pert_data, 
                    device='cuda:0', 
                    weight_bias_track=True, 
                    proj_name=str(DATASET), 
                    exp_name=exp_trail+'_'+exp_name,
                    save_path=save_path,
                    )
gears_model.model_initialize(hidden_size=64, 
                             no_perturb=NO_PERTURB
                             )

# train model
gears_model.train(epochs=EPOCHS, 
                  lr=LR
                  )    

# save model
gears_model.save_model(save_path)

