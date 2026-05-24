source activate unipert-g2cp-dev
export WANDB_MODE=offline

datasets=("LINCS-A549" "LINCS-A375" "LINCS-MCF7" "LINCS-PC3" "LINCS-HT29") 
seeds=(0)             
train_modes=("pretrain-finetune-ts" "ground-truth") 
train_fracs=(0.0)   
unipert_model_dir="/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/current_model"
python_script="/data/liyiming/Project/UniPert-G2CP_reproduce/G2CP/train_G2CP_ts.py"
gpu_num=6
printf "Starting multiple experiments...\n"

experiment_id=0
for train_mode in "${train_modes[@]}"; do
    for seed in "${seeds[@]}"; do
        for dataset in "${datasets[@]}"; do
            for train_frac in "${train_fracs[@]}"; do

                experiment_id=$((experiment_id+1))
                gpu_id=$((experiment_id % gpu_num))

                exp_name="LINCS_ts"
                save_dir="/data/liyiming/Project/UniPert-G2CP_reproduce/G2CP/saved_models/${exp_name}"

                mkdir -p "$save_dir"

                export CUDA_VISIBLE_DEVICES=$gpu_id
                nohup python "$python_script" --dataset "$dataset" --seed "$seed" --train_frac "$train_frac"\
                    --train_mode "$train_mode" --unipert_model_dir "$unipert_model_dir" --save_dir "$save_dir"\
                    > "${save_dir}/${train_mode}_${dataset}_${seed}_${train_frac}.log" 2>&1 &

                current_time=$(date '+%Y-%m-%d %H:%M:%S')
                echo "[$current_time] Experiment with train_mode=$train_mode, dataset=$dataset, seed=$seed, train_frac=$train_frac started on GPU $gpu_id. Logs saved to ${save_dir}/${train_mode}_${dataset}_${seed}.log"
                sleep 60

                unset CUDA_VISIBLE_DEVICES
            done
        done
    done
done

printf "Multiple experiments started.\n"
