#!/bin/bash
cd /data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/
source activate unipert-g2cp-dev

target_embedders=(ESM2 OntoProtein PseAAC)  # ESM2 OntoProtein PseAAC 
compound_embedders=(ECFP4 UniMol KPGT)      # ECFP4 UniMol KPGT

python_script="/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/train_unipert.py"
gpu_num=6
printf "Starting grid search...\n"
experiment_id=0
for tgt in "${target_embedders[@]}"; do
    for cp in "${compound_embedders[@]}"; do

        experiment_id=$((experiment_id+1))
        gpu_id=$((experiment_id % gpu_num))

        exp_name="unipert_embedder_gs/${tgt}_${cp}"
        save_dir="/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/saved_models/${exp_name}"

        mkdir -p "$save_dir"

        export CUDA_VISIBLE_DEVICES=$gpu_id
        nohup python "$python_script" --target_embedder "$tgt" --compound_embedder "$cp" --exp_name "${exp_name}"\
            > "${save_dir}.log" 2>&1 &

        echo "Experiment with tgt=$tgt, cp=$cp started on GPU $gpu_id. Logs saved to ${save_dir}.log"
        sleep 3
        unset CUDA_VISIBLE_DEVICES
    done
done
printf "Grid search finished.\n"