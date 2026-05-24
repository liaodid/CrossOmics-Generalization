#!/bin/bash

source activate py310

dataset="sciplex3_HDAC"
models=("chemCPA" "UniPert" "UniMol" "KPGT") 
split_ids=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17)  

# dataset="sciplex3_all"
# models=("chemCPA" "UniPert") 
# split_ids=(1 2 3 4 5)

python_script="/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/chemcial_benchmark/train_CPA_exps.py"
printf "Starting multiple experiments...\n"
gpu_num=4
experiment_id=0
for model in "${models[@]}"; do
    for i in "${split_ids[@]}"; do

        gpu_id=$((experiment_id % gpu_num))
        experiment_id=$((experiment_id+1))
        
        save_dir="/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/chemical_benchmark/saved_models"

        export CUDA_VISIBLE_DEVICES=$gpu_id

        nohup python "$python_script"\
            --model "$model"\
            --dataset "$dataset"\
            --split_id "$i"\
            > "${save_dir}/${model}/${dataset}/split_${i}.log" 2>&1 &

        echo "Experiment with model=$model, dataset=$dataset, split=$i started on GPU $gpu_id. Logs saved to ${save_dir}/${model}/${dataset}/split_${i}.log"
        sleep 10
        unset CUDA_VISIBLE_DEVICES
    done
done
