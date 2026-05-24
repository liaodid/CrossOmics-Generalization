# source activate py310
# python evaluate_models.py


import numpy as np
import pandas as pd
import scanpy as sc
from scipy.stats import pearsonr
from sklearn.metrics import r2_score, mean_squared_error
from collections import defaultdict
import sys, os
import copy
import argparse

sys.path.append('/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/chemcial_benchmark/CPA')
from CPA.cpa_adapted import CPA


def find_folders_with_model_pt(saved_dir):
    folders_with_model_pt = []
    for root, dirs, files in os.walk(saved_dir):
        if 'model.pt' in files:
            folders_with_model_pt.append(root)
    return folders_with_model_pt


def ccc(x, y):
    """Concordance Correlation Coefficient
    
    Parameters:
    x : ndarray
        A NumPy array of values for the first variable.
    y : ndarray
        A NumPy array of values for the second variable.

    Returns:
    float
        The concordance correlation coefficient between x and y.
    """
    sxy = np.sum((x - x.mean())*(y - y.mean()))/x.shape[0]
    rhoc = 2*sxy / (np.var(x) + np.var(y) + (x.mean() - y.mean())**2)
    return rhoc


def evaluate_expression_metrics(x_true, x_pred, gene_indices):
    """
    Calculate and store statistical metrics for gene expression data.
    
    Parameters:
    x_true : ndarray
        Gene expression matrix for the treated group.
    x_pred : ndarray
        Gene expression matrix predicted by the model /for the control group.
    gene_indices : ndarray
        Indices of genes of interest.
    
    Returns:
    dict
        A dictionary containing the calculated statistical metrics.
    """
    # Select genes of interest
    x_true_deg = x_true[:, gene_indices]
    x_pred_deg = x_pred[:, gene_indices]

    # Calculate metrics
    r2_mean_deg = r2_score(np.mean(x_true_deg, axis=0), np.mean(x_pred_deg, axis=0))
    mse_mean_deg = mean_squared_error(np.mean(x_true_deg, axis=0), np.mean(x_pred_deg, axis=0))
    pcc_mean_deg, _ = pearsonr(np.mean(x_true_deg, axis=0), np.mean(x_pred_deg, axis=0))
    ccc_mean_deg = ccc(np.mean(x_true_deg, axis=0), np.mean(x_pred_deg, axis=0))
    
    return r2_mean_deg, mse_mean_deg, pcc_mean_deg, ccc_mean_deg


def evaluate_model(
    model, 
    ctrl_adata, 
    test_adata, 
    is_count_data,
    model_name, 
    data_name, 
    split_key, 
    model_dir,
    deg_uns_cat_key, 
    control_group,
    n_random_ctrl=100
):
    """
    Evaluate the performance of a given model on test data.

    Parameters:
    model : object
        The model to be evaluated.
    ctrl_adata : AnnData
        The control group single-cell data.
    test_adata : AnnData
        The test single-cell data.
    is_count_data : bool, optional
        Whether to perform log transformation on count data.
    model_name : str
        The name of the model.
    data_name : str
        The name of the dataset.
    split_key : str
        The key for data splitting.
    model_dir : str
        The directory path of the model.
    deg_uns_cat_key : str, optional
        The key for the unsupervised category of differentially expressed genes.
    control_group : str, optional
        The name of the control group.
    n_random_ctrl : int, optional
        The number of times to randomly select control samples.

    Returns:
    results_df : DataFrame
        A DataFrame containing the evaluation results of the model.
    """

    results = defaultdict(list)
    for cat in test_adata.obs[deg_uns_cat_key].unique():
        cov, cond, dose = cat.split('_')
        cov_ctrl_adata = ctrl_adata[ctrl_adata.obs['cell_type'] == cov]      # keep only control cells of the same cell type

        if control_group not in cat:
            cat_adata = test_adata[test_adata.obs[deg_uns_cat_key] == cat].copy()
            cat_adata.obsm['X_true'] = cat_adata.X
            drug = cat_adata.obs['condition'].unique()[0]

            deg_cat = f'{cat}'
            deg_list = adata.uns['rank_genes_groups_cov'][deg_cat]

            for seed in range(n_random_ctrl):
                np.random.seed(seed)
                sample_indices = np.random.choice(cov_ctrl_adata.shape[0], size=cat_adata.shape[0], replace=True)
                cat_adata.X = cov_ctrl_adata[sample_indices].copy().X
                model.predict(cat_adata, batch_size=cat_adata.shape[0])

                x_ctrl = cat_adata.X.toarray()
                x_true = cat_adata.obsm['X_true'].toarray()
                x_pred = cat_adata.obsm['CPA_pred']    
                if is_count_data:
                    x_ctrl = np.log1p(x_ctrl)
                    x_true = np.log1p(x_true)
                    x_pred = np.log1p(x_pred)    

                for n_top_deg in [10, 20, 50, None]:  
                    if n_top_deg is not None:
                        degs = np.where(np.isin(adata.var_names, deg_list[:n_top_deg]))[0]
                    else:
                        n_top_deg = 'all'
                        degs = np.arange(adata.n_vars)
                        
                    ### Calculation of model performance
                    r2_mean_deg, mse_mean_deg, pcc_mean_deg, ccc_mean_deg = evaluate_expression_metrics(x_true, x_pred, degs)
                    # add results
                    results['model'].append(model_name)
                    results['dataset'].append(data_name)
                    results['split_key'].append(split_key)

                    results['cell_type'].append(cov)
                    results['condition'].append(drug)
                    results['dose'].append(dose)
                    results['n_top_deg'].append(n_top_deg)

                    results['r2_mean_deg'].append(r2_mean_deg)
                    results['mse_mean_deg'].append(mse_mean_deg)
                    results['pcc_mean_deg'].append(pcc_mean_deg)
                    results['ccc_mean_deg'].append(ccc_mean_deg)

                    results['model_dir'].append(model_dir)

                    ### Calculation of control & true performance
                    r2_mean_deg, mse_mean_deg, pcc_mean_deg, ccc_mean_deg = evaluate_expression_metrics(x_true, x_ctrl, degs)
                    # add results
                    results['model'].append(model_name+'_noPerturb')
                    results['dataset'].append(data_name)
                    results['split_key'].append(split_key)

                    results['cell_type'].append(cov)
                    results['condition'].append(drug)
                    results['dose'].append(dose)
                    results['n_top_deg'].append(n_top_deg)

                    results['r2_mean_deg'].append(r2_mean_deg)
                    results['mse_mean_deg'].append(mse_mean_deg)
                    results['pcc_mean_deg'].append(pcc_mean_deg)
                    results['ccc_mean_deg'].append(ccc_mean_deg)

                    results['model_dir'].append(model_dir)

    results_df = pd.DataFrame(results)
    return results_df  


parser = argparse.ArgumentParser(description='Train CPA-based model with a given split key and dataset.')
parser.add_argument('--saved_dir', type=str, 
                    default='/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/chemcial_benchmark/saved_models/sciplex3_HDAC'
                    # default='/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/chemcial_benchmark/saved_models/sciplex3_all'
                    )
args = parser.parse_args()


### Retrieve models
saved_dir = args.saved_dir if hasattr(args, 'saved_dir') and args.saved_dir else os.getcwd()
print(saved_dir)
model_dirs = find_folders_with_model_pt(saved_dir)

result_file = os.path.join(saved_dir, 'results_df.csv')
if os.path.exists(result_file) and os.path.getsize(result_file) > 0:
    try:
        all_results_df = pd.read_csv(result_file, index_col=None)
        evaluated_models = list(set(all_results_df['model_dir']))
        model_dirs = [d for d in model_dirs if d not in evaluated_models]
    except pd.errors.EmptyDataError:
        all_results_df = pd.DataFrame()
else:
    all_results_df = pd.DataFrame()

if not all_results_df.empty:
    all_results_df.to_csv(result_file, index=False)

## Data Loading
DATA_NAME = saved_dir.split('/')[-1]
if  DATA_NAME == 'sciplex3_HDAC':
    data_path = '/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/chemcial_benchmark/data/processed_sciPlex3_HDAC.h5ad'
    adata = sc.read(data_path)
elif DATA_NAME == 'sciplex3_all':
    data_path = '/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/chemcial_benchmark/data/processed_sciPlex3_all.h5ad'
    adata = sc.read(data_path)
else:
    raise ValueError('Dataset not supported.')


### Adata setup infomation, keep same settings with trainning setup
MODEL = saved_dir.split('/')[-1]
if 'combo' in DATA_NAME:
    adata_raw.X = adata_raw.layers['counts'].copy()
    perturbation_key='condition_ID'
    dosage_key='log_dose'
    control_group='CHEMBL504'
    batch_key=None
    # smiles_key='smiles_rdkit' if use_rdkit_embeddings else None
    is_count_data=True
    categorical_covariate_keys=['cell_type']
    deg_uns_key='rank_genes_groups_cov'
    deg_uns_cat_key='cov_drug_dose'
    max_comb_len=2
else:
    perturbation_key='condition'
    dosage_key='dose_val'
    control_group='control'
    batch_key=None
    # smiles_key='SMILES' if use_rdkit_embeddings else None
    is_count_data=False
    categorical_covariate_keys=['cell_type']
    deg_uns_key='rank_genes_groups_cov'
    deg_uns_cat_key='cov_drug_dose_name'
    max_comb_len=1


### Evaluate models
for model_dir in model_dirs:
    # MODEL, DATA_NAME, SPLIT_KEY
    DATA_NAME, MODEL, SPLIT_KEY = model_dir.split('/')[-3:]
    print('\n\n======= MODEL: {}, DATA_NAME: {}, SPLIT_KEY: {}  =======\n\n'.format(MODEL, DATA_NAME, SPLIT_KEY))

    adata = copy.deepcopy(adata_raw)
    model = CPA.load(dir_path=model_dir,
                        adata=adata,
                        use_gpu=True)

    ctrl_adata = adata[(adata.obs[perturbation_key]==control_group)].copy() 
    # print(f"Control data shape: {ctrl_adata.shape}")
    test_adata = adata[(adata.obs[SPLIT_KEY]=='ood') | (adata.obs[SPLIT_KEY]=='test')].copy()
    # print(f"Test data shape: {test_adata.shape}")

    results_df = evaluate_model(
        model=model,
        ctrl_adata=ctrl_adata,
        test_adata=test_adata,
        is_count_data=is_count_data,
        model_name=MODEL,
        data_name=DATA_NAME,
        split_key=SPLIT_KEY,
        model_dir=model_dir,
        deg_uns_cat_key=deg_uns_cat_key,
        control_group=control_group,
        n_random_ctrl=100
    )

    if os.path.exists(result_file) and os.path.getsize(result_file) > 0:
        try:
            all_results_df = pd.read_csv(result_file, index_col=None)
        except pd.errors.EmptyDataError:
            all_results_df = pd.DataFrame()
    else:
        all_results_df = pd.DataFrame()
        
    all_results_df = pd.concat([all_results_df, results_df], axis=0)
    all_results_df.to_csv(result_file, index=False)  

    import gc
    del model, adata, ctrl_adata, test_adata, all_results_df, results_df
    gc.collect()

    print(f"{model_dir} evaluated Done!")


