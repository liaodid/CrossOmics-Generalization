import sys
import os
import argparse
import numpy as np
import random
import torch

sys.path.append('/data/liyiming/Project/UniPert-G2CP_reproduce/G2CP/backbone_model/GEARS')
from gears import PertData, GEARS
from gears.utils import print_sys

os.environ["WANDB_MODE"] = "offline"

# init and parse args
parser = argparse.ArgumentParser(description='GEARS Experiment Runner')
parser.add_argument('--dataset', type=str, default='LINCS-A549', 
                    choices=['LINCS-A549', 'LINCS-A375', 'LINCS-MCF7', 'LINCS-PC3', 'LINCS-HT29'])
parser.add_argument('--train_mode', type=str, default='pretrain-finetune-ts',       # pretrain on Touchstone set  
                    choices=['ground-truth', 'pretrain-finetune-ts'])   
parser.add_argument('--seed', type=int, default=0, help='Random seed for the experiment') 
parser.add_argument('--train_frac', type=float, default=0.0, help='Fraction of trainning gene set')
parser.add_argument('--val_frac', type=float, default=0.1, help='Fraction of validation set')
parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
parser.add_argument('--lr', type=float, default=1e-3, help='Learning rate')
parser.add_argument('--epochs', type=int, default=20, help='Number of epochs')
parser.add_argument('--weight_decay', type=float, default=5e-4, help='Weight decay')    
parser.add_argument('--save_dir', type=str, default='/data/liyiming/Project/UniPert-G2CP_reproduce/G2CP/saved_models/test', help='Directory to store results')
parser.add_argument('--unipert_model_dir', type=str, default="/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/current_model")
args = parser.parse_args()

DATASET = args.dataset
TRAIN_MODE = args.train_mode
SEED = args.seed
FINETUNE_FRAC = TRAIN_FRAC = args.train_frac
VAL_FRAC = args.val_frac
BATCH_SIZE = args.batch_size
LR = args.lr
EPOCHS = 4 if 'test' in args.save_dir else args.epochs
WEIGHT_DECAY = args.weight_decay
NO_PERTURB = True if 'no-perturb' in TRAIN_MODE else False


exp_trail = 'new_' + TRAIN_MODE+'_'+str(SEED)+'_'+str(TRAIN_FRAC)
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


# print params
print_sys('-------------------NEW EXP---------------------')
print_sys(f'dataset : {DATASET}')
print_sys(f'train_mode : {TRAIN_MODE}')
print_sys(f'seed : {SEED}')
print_sys(f'epochs : {EPOCHS}')
print_sys(f'lr : {LR}')
print_sys(f'batch_size : {BATCH_SIZE}')
print_sys(f'train_frac : {TRAIN_FRAC}')
print_sys(f'finetune_frac : {FINETUNE_FRAC}')
print_sys(f'exp_name : {exp_name}')
print_sys('-----------------------------------------------')

# prepare data
pert_data = PertData(data_path='/data/liyiming/Project/UniPert-G2CP_reproduce/G2CP/data')
pert_data.load(data_name=DATASET,
               pert_type_col_name = 'pert_type',
               perturbagen_col_name = 'condition',
               control_key = 'ctrl'
               )
pert_data.prepare_split(split=TRAIN_MODE, 
                        seed=SEED, 
                        train_ptbg_set_frac = TRAIN_FRAC,       
                        val_ptbg_set_frac = VAL_FRAC,
                        )
pert_data.get_dataloader(batch_size=BATCH_SIZE,
                         test_batch_size=128,
                        )
dataloader = pert_data.dataloader

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


if 'pretrain-finetune' in TRAIN_MODE:
    # pre-train model
    gears_model.new_train(
        epochs=EPOCHS, 
        lr=LR,
        weight_decay=WEIGHT_DECAY,
        train_loader= dataloader['pretrain_train_loader'],
        val_loader=dataloader['pretrain_val_loader'],
        test_loader= None,
        )

    # save final model
    gears_model.save_model(save_path, 'pretrain_model')
    print_sys('Pre-train Done!')

    # fine-tune model
    gears_model.new_train(
        epochs=EPOCHS//2, 
        lr=LR/10,
        weight_decay=WEIGHT_DECAY*10,    
        train_loader= dataloader['train_loader'],
        val_loader=dataloader['val_loader'],
        test_loader=dataloader['test_loader'],
        )  

    # save final model
    gears_model.save_model(save_path, 'finetune_model')
    print_sys('Fine-tune Done!')

elif 'ground-truth' in TRAIN_MODE:
    gears_model.new_train(
        epochs=EPOCHS, 
        lr=LR,
        weight_decay=WEIGHT_DECAY,    
        train_loader= dataloader['train_loader'],
        val_loader=dataloader['val_loader'],
        test_loader=dataloader['test_loader'],
        GT=True,
        )  
    
else:
    gears_model.new_train(
        epochs=EPOCHS, 
        lr=LR,
        weight_decay=WEIGHT_DECAY,    
        train_loader= dataloader['train_loader'],
        val_loader=dataloader['val_loader'],
        test_loader=dataloader['test_loader'],
        )  
    # save final model
    gears_model.save_model(save_path, 'model')

print_sys('-------------------END---------------------')
