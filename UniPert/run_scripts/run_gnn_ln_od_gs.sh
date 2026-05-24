#!/bin/bash
cd /data/liyiming/Project/UniPert-G2CP_reproduce/
source activate unipert-g2cp-dev

target_embedder="ESM2"
compound_embedder="ECFP4"

gnn_types=("GCN")   
layer_nums=(1 2 3)       # 1 2 3
out_dims=(64 128 256)    # 64 128 256

python_script="/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/train_unipert.py"
gpu_num=6
printf "Starting grid search...\n"
experiment_id=4

for gnn_type in "${gnn_types[@]}"; do
    for layer_num in "${layer_nums[@]}"; do
        for out_dim in "${out_dims[@]}"; do
            gpu_id=$((experiment_id % gpu_num))
            experiment_id=$((experiment_id+1))

            exp_name="unipert_gnn_gs/${gnn_type}_${layer_num}_${out_dim}"
            save_dir="/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/saved_models/${exp_name}"

            mkdir -p "$save_dir"

            export CUDA_VISIBLE_DEVICES=$gpu_id
            nohup python "$python_script" --gnn_type "$gnn_type" --layer_num "$layer_num" --out_dim "$out_dim" \
                --exp_name "${exp_name}" > "${save_dir}.log" 2>&1 &

            echo "Experiment with gnn_type=$gnn_type, layer_num=$layer_num, out_dim=$out_dim, started on GPU $gpu_id. Logs saved to ${save_dir}.log"
            sleep 3
            unset CUDA_VISIBLE_DEVICES
        done
    done
done
printf "Grid search finished.\n"