source activate unipert-g2cp-dev
export WANDB_MODE=offline

train_modes=("pretrain-finetune-pool")      
datasets=("LINCS-A549" "LINCS-A375" "LINCS-MCF7" "LINCS-PC3") 
seeds=(1310 229 52 1519 564)                    
finetune_fracs=(0.9 0.8 0.7 0.6 0.5 0.4 0.3 0.2 0.1)
unipert_model_dir="/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/current_model"
python_script="/data/liyiming/Project/UniPert-G2CP_reproduce/G2CP/train_G2CP_pool.py"
gpu_num=6
printf "Starting multiple experiments...\n"

experiment_id=5
for train_mode in "${train_modes[@]}"; do
    for dataset in "${datasets[@]}"; do
        for seed in "${seeds[@]}"; do   
            for finetune_frac in "${finetune_fracs[@]}"; do

                experiment_id=$((experiment_id+1))
                gpu_id=$((experiment_id % gpu_num))

                exp_name="LINCS_pool"
                save_dir="/data/liyiming/Project/UniPert-G2CP_reproduce/G2CP/saved_models/${exp_name}"

                mkdir -p "$save_dir"

                export CUDA_VISIBLE_DEVICES=$gpu_id
                nohup python "$python_script" --dataset "$dataset" --seed "$seed" --train_frac "$finetune_frac"\
                    --train_mode "$train_mode" --unipert_model_dir "$unipert_model_dir" --save_dir "$save_dir"\
                    > "${save_dir}/${train_mode}_${dataset}_${seed}_${finetune_frac}.log" 2>&1 &

                current_time=$(date '+%Y-%m-%d %H:%M:%S')
                echo "[$current_time] Experiment with train_mode=$train_mode, dataset=$dataset, seed=$seed, finetune_frac=$finetune_frac started on GPU $gpu_id. Logs saved to ${save_dir}/${train_mode}_${dataset}_${seed}_${finetune_frac}.log"
                sleep 1

                unset CUDA_VISIBLE_DEVICES

            done
            sleep 10
        done
        sleep 300
    done
    sleep 1
done
printf "Multiple experiments started.\n"