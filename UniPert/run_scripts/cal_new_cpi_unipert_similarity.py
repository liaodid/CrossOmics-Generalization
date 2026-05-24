#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
import torch
import gc
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# 添加项目路径
sys.path.append('../')
from unipert import UniPert

# ========== 配置部分 ==========
# 模型路径列表
model_paths = [
    '../saved_models/unipert_graph_rd_1008/50%_weighted_directed_256',
    '../saved_models/unipert_graph_rd_1008/unweighted_undirected_256',
    '../saved_models/unipert_graph_rd_1008/weighted_directed_256',
    '../saved_models/unipert_graph_rd_1008/weighted_undirected_256',

    '../saved_models/unipert_graph_rd_1224/50%_weighted_directed_256_2025',
    '../saved_models/unipert_graph_rd_1224/unweighted_undirected_256_2025',
    '../saved_models/unipert_graph_rd_1224/weighted_directed_256_2025',
    '../saved_models/unipert_graph_rd_1224/weighted_undirected_256_2025',

    '../saved_models/unipert_graph_rd_1225/50%_weighted_directed_256_2026',
    '../saved_models/unipert_graph_rd_1225/unweighted_undirected_256_2026',
    '../saved_models/unipert_graph_rd_1225/weighted_directed_256_2026',
    '../saved_models/unipert_graph_rd_1225/weighted_undirected_256_2026',

    '../saved_models/unipert_graph_rd_1225/50%_weighted_directed_256_2027',
    '../saved_models/unipert_graph_rd_1225/unweighted_undirected_256_2027',
    '../saved_models/unipert_graph_rd_1225/weighted_directed_256_2027',
    '../saved_models/unipert_graph_rd_1225/weighted_undirected_256_2027',

    '../saved_models/unipert_graph_rd_1225/50%_weighted_directed_256_2028',
    '../saved_models/unipert_graph_rd_1225/unweighted_undirected_256_2028',
    '../saved_models/unipert_graph_rd_1225/weighted_directed_256_2028',
    '../saved_models/unipert_graph_rd_1225/weighted_undirected_256_2028',

    '../saved_models/unipert_embedder_gs_1230/OntoProtein_ECFP4_2024',
    '../saved_models/unipert_embedder_gs_1230/PseAAC_ECFP4_2024',

    '../saved_models/unipert_embedder_gs_1230/OntoProtein_ECFP4_2025',
    '../saved_models/unipert_embedder_gs_1230/PseAAC_ECFP4_2025',

    '../saved_models/unipert_embedder_gs_1230/OntoProtein_ECFP4_2026',
    '../saved_models/unipert_embedder_gs_1230/PseAAC_ECFP4_2026',

    '../saved_models/unipert_embedder_gs_1230/OntoProtein_ECFP4_2027',
    '../saved_models/unipert_embedder_gs_1230/PseAAC_ECFP4_2027',

    '../saved_models/unipert_embedder_gs_1230/OntoProtein_ECFP4_2028',
    '../saved_models/unipert_embedder_gs_1230/PseAAC_ECFP4_2028',
    
]

new_cpi_path = '/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/data/processed_pubchem_CPI_25Oct_cid37820_as1216_i81650.csv'
cp_df_path = '/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/data/processed_new_compound_cid37820.csv'
# tgt_fa_path = '/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/data/ref_target_seq.fasta'
data_dir = '/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/data'

max_workers = 18  

def normalize(vec):
    v = np.array(vec)
    norm = np.linalg.norm(v)
    return v / norm if norm != 0 else v

def process_model(args):
    import sys
    if '../' not in sys.path:
        sys.path.append('../')
    from unipert import UniPert
    
    model_path, new_cpi_path, cp_df_path, data_dir, gpu_id = args
    
    if torch.cuda.is_available() and gpu_id is not None:
        if gpu_id < torch.cuda.device_count():
            torch.cuda.set_device(gpu_id)
            device = f'cuda:{gpu_id}'
        else:
            device = 'cpu'
            gpu_id = None
    else:
        device = 'cpu'
        gpu_id = None
    print(f"\n{'='*80}")
    print(f"处理模型: {model_path}")
    if gpu_id is not None:
        print(f"使用 GPU: {gpu_id}")
    print(f"{'='*80}")
    
    try:
        # 1. 获取 new_cpi 涉及的 protein、compound 序列
        print(f"\n[1/5] 获取 new_cpi 涉及的 protein、compound 序列...")
        new_cpi = pd.read_csv(new_cpi_path)
        print(f"✅ 加载 new_cpi 数据: {len(new_cpi)} 个 pairs")
        print(f"   Compounds: {len(new_cpi['Compound_CID'].value_counts())}, Targets: {len(new_cpi['Approved symbol'].value_counts())}")
        
        # 处理 compound 数据
        if not os.path.exists(cp_df_path):
            print(f"⚠️  Compound CSV 文件不存在，从 new_cpi 生成...")
            cp_df = new_cpi.loc[:, ['Compound_CID', 'SMILES']].drop_duplicates()
            cp_df.to_csv(cp_df_path, index=False)
            print(f"✅ 已保存 compound 数据到: {cp_df_path}")
        else:
            cp_df = pd.read_csv(cp_df_path)
            print(f"✅ 已加载 compound 数据: {len(cp_df)} 个化合物")
        
        # 2. 初始化 UniPert
        print(f"\n[2/5] 初始化 UniPert 模型...")
        unipert = UniPert(data_dir=data_dir, model_hparams={'save_dir': model_path}, device=device)
        unipert.load_unipert_reps()
        print(f"✅ 模型加载成功: {unipert.save_dir}")
        print(f"   当前 unipert_reps 中的键数量: {len(unipert.unipert_reps.keys())}")
        
        # 3. 生成所有涉及的 protein、compounds embedding
        print(f"\n[3/5] 生成所有涉及的 protein、compounds embedding...")
        
        # 编码 reference perturbagens
        print("   编码 reference perturbagens...")
        unipert.encode_ref_perturbagens(save=True)
        print(f"   当前 unipert_reps 中的键数量: {len(unipert.unipert_reps.keys())}")

        # 编码 compound embedding
        print("   编码 compound embedding...")
        cp_emb = unipert.encode_chemical_perturbagens_from_cp_sms_csv(
            cp_df_path, 
            cp_col_name='compound', 
            sms_col_name='SMILES', 
            save=True
        )
        print(f"✅ Compound embedding 生成完成，共 {len(cp_emb)} 个化合物")
        print(f"   当前 unipert_reps 中的键数量: {len(unipert.unipert_reps.keys())}")

        # 4. 加载 unipert_reps
        print(f"\n[4/5] 加载 unipert_reps...")
        unipert_reps_path = os.path.join(model_path, 'unipert_reps.pkl')
        if os.path.exists(unipert_reps_path):
            with open(unipert_reps_path, 'rb') as f:
                data = pickle.load(f)
        else:
            data = unipert.unipert_reps
        print(f"✅ 加载完成，共 {len(data)} 个 embedding")
        
        # 5. 计算 new_cpi pairs 的 cosine 相似度
        print(f"\n[5/5] 计算 new_cpi pairs 的 cosine 相似度...")
        
        # 获取所有涉及的 compounds 和 targets
        cps = list(new_cpi['compound'].value_counts().index)
        gns = list(new_cpi['target'].value_counts().index)
        print(f"   涉及 {len(cps)} 个 compounds, {len(gns)} 个 targets")
        
        # 归一化所有 embedding
        print("   归一化 embedding...")
        for key in (cps + gns):
            if key in data:
                data[key] = normalize(data[key])
        
        # 计算每个 pair 的 cosine 相似度
        similarities = []
        missing_compounds = set()
        missing_targets = set()
        
        for idx, row in new_cpi.iterrows():
            compound = row['compound']
            target = row['target']
            
            # 检查 embedding 是否存在
            if compound not in data:
                missing_compounds.add(compound)
                continue
            if target not in data:
                missing_targets.add(target)
                continue
            
            # 确保是二维数组 (1, n_features)
            cp_vec = np.array(data[compound], dtype=np.float32)
            tgt_vec = np.array(data[target], dtype=np.float32)
            
            if cp_vec.ndim == 1:
                cp_vec = cp_vec.reshape(1, -1)
            if tgt_vec.ndim == 1:
                tgt_vec = tgt_vec.reshape(1, -1)
            
            # 计算 cosine 相似度
            sim = cosine_similarity(cp_vec, tgt_vec)[0][0]
            similarities.append({
                'compound': compound,
                'target': target,
                'UniPert_similarity': float(sim)
            })
        
        # 创建结果 DataFrame
        result_df = pd.DataFrame(similarities)
        print(result_df.describe())
        
        # 保存结果
        output_path = os.path.join(model_path, 'new_cpi_unipert_cosine_similarity.csv')
        result_df.to_csv(output_path, index=False)
        
        print(f"✅ Cosine 相似度计算完成:")
        print(f"   成功计算: {len(result_df)} 个 pairs")
        if missing_compounds:
            print(f"   ⚠️  缺失 compound embedding: {len(missing_compounds)} 个")
        if missing_targets:
            print(f"   ⚠️  缺失 target embedding: {len(missing_targets)} 个")
        print(f"   结果已保存到: {output_path}")
        
        print(f"\n✅ 模型 {model_path} 处理完成！")
        
        # 清理 GPU 内存
        print("   清理 GPU 内存...")
        del unipert
        del data
        if 'cp_emb' in locals():
            del cp_emb
        if 'tgt_emb' in locals():
            del tgt_emb
        
        # 清理 Python 垃圾回收
        gc.collect()
        
        # 清理 CUDA 缓存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print(f"   ✅ GPU 内存已清理 (当前 GPU 使用: {torch.cuda.memory_allocated() / 1024**3:.2f} GB)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 处理模型 {model_path} 时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 即使出错也要清理内存
        if 'unipert' in locals():
            del unipert
        if 'data' in locals():
            del data
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return False

# ========== 执行主流程 ==========
if __name__ == '__main__':
    try:
        mp.set_start_method('spawn', force=True)
    except RuntimeError:
        pass
    
    print("="*80)
    print("UniPert 多模型 Embedding 生成和 Cosine 相似度计算脚本 (并行版本)")
    print("="*80)
    print(f"待处理模型数量: {len(model_paths)}")
    print(f"New CPI 数据路径: {new_cpi_path}")
    print(f"Compound CSV 路径: {cp_df_path}")
    # print(f"Target FASTA 路径: {tgt_fa_path}")
    print("="*80)
    
    # 检查 GPU 状态
    num_gpus = 0
    if torch.cuda.is_available():
        num_gpus = torch.cuda.device_count()
        print(f"✅ GPU 可用: {num_gpus} 个 GPU")
        for i in range(num_gpus):
            print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
            print(f"      内存: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB")
    else:
        print("⚠️  GPU 不可用，将使用 CPU")
    print("="*80)
    
    # 确定并行进程数
    if max_workers is None:
        # 自动检测：如果有 GPU，每个 GPU 一个进程；否则使用 CPU 核心数的一半
        if num_gpus > 0:
            max_workers = min(num_gpus, len(model_paths))
        else:
            max_workers = min(mp.cpu_count() // 2, len(model_paths))
    else:
        # 使用手动设置的并行数
        max_workers = min(max_workers, len(model_paths))
    
    print(f"\n并行配置: 使用 {max_workers} 个进程")
    print("="*80)
    
    # 准备任务参数：为每个模型分配 GPU ID
    tasks = []
    for i, model_path in enumerate(model_paths):
        # 如果有多个 GPU，循环分配；否则使用 None（让每个进程自己选择）
        gpu_id = i % num_gpus if num_gpus > 0 else None
        tasks.append((model_path, new_cpi_path, cp_df_path, data_dir, gpu_id))
    
    # 并行处理模型
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_model = {
            executor.submit(process_model, task): task[0] 
            for task in tasks
        }
        
        # 使用 tqdm 显示进度
        with tqdm(total=len(tasks), desc="处理模型") as pbar:
            for future in as_completed(future_to_model):
                model_path = future_to_model[future]
                try:
                    success = future.result()
                    results.append((model_path, success))
                    status = "✅" if success else "❌"
                    pbar.set_postfix_str(f"{status} {os.path.basename(model_path)}")
                except Exception as e:
                    print(f"\n❌ 处理模型 {model_path} 时发生异常: {str(e)}")
                    results.append((model_path, False))
                finally:
                    pbar.update(1)
    
    # 汇总结果
    print("\n\n" + "="*80)
    print("处理结果汇总")
    print("="*80)
    for model_path, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status}: {model_path}")
    
    success_count = sum(1 for _, success in results if success)
    print(f"\n总计: {success_count}/{len(model_paths)} 个模型处理成功")
    print("="*80)
