#!/bin/bash
cd /data/liyiming/Project/UniPert_G2CP/UniPert/
source activate unipert-g2cp-dev

graph_types=("weighted_directed" "weighted_undirected" 50%_weighted_directed)               
out_dims=(256)
seeds=(2023)

python_script="/data/liyiming/Project/UniPert_G2CP/UniPert/train_unipert.py"
gpu_num=6
printf "Starting grid search...\n"
experiment_id=4

for graph_type in "${graph_types[@]}"; do
    for out_dim in "${out_dims[@]}"; do
        for seed in "${seeds[@]}"; do
            gpu_id=$((experiment_id % gpu_num))
            experiment_id=$((experiment_id+1))

            exp_name="unipert_graph_rd_1225/${graph_type}_${out_dim}_${seed}"
            save_dir="/data/liyiming/Project/UniPert_G2CP/UniPert/saved_models/${exp_name}"

            mkdir -p "$save_dir"

            export CUDA_VISIBLE_DEVICES=$gpu_id
            nohup python "$python_script" --graph_type "$graph_type" --out_dim "$out_dim" \
                --exp_name "${exp_name}" --seed "$seed" > "${save_dir}.log" 2>&1 &

            echo "Experiment with graph_type=$graph_type, out_dim=$out_dim, started on GPU $gpu_id. Logs saved to ${save_dir}.log"
            sleep 3
            unset CUDA_VISIBLE_DEVICES
        done
    done
done
printf "Run graph weight direct redundancy experiments finished.\n"