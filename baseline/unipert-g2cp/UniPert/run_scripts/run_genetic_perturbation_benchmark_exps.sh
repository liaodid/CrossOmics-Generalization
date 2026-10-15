cd /data/liyiming/Project/UniPert-G2CP_reproduce/
source activate unipert-g2cp-dev

datasets=("norman" "dixit") 
seeds=(1310 229 52 1519 564 ) 
models=("No-Perturb" "GEARS" "UniPert" "ESM2" "OntoProtein" "PseAAC")
unipert_model_dir="/UniPert/current_model"
python_script="/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/genetic_benchmark/train_GEARS_exps.py"
gpu_num=4
printf "Starting multiple experiments...\n"

experiment_id=0
for model in "${models[@]}"; do
    for dataset in "${datasets[@]}"; do
        for seed in "${seeds[@]}"; do

            gpu_id=$((experiment_id % gpu_num))
            experiment_id=$((experiment_id+1))

            save_dir="/data/liyiming/Project/UniPert-G2CP_reproduce/UniPert/perturbation_tasks/genetic_benchmark/saved_models"

            mkdir -p "$save_dir"

            export CUDA_VISIBLE_DEVICES=$gpu_id
            nohup python "$python_script" --dataset "$dataset" --seed "$seed" --save_dir "$save_dir"\
                 --model_name "$model" --unipert_model_dir "$unipert_model_dir"\
                > "${save_dir}/${model}_${dataset}_${seed}.log" 2>&1 &

            echo "Experiment with model_name=$model, dataset=$dataset, seed=$seed started on GPU $gpu_id. Logs saved to ${save_dir}/${model}_${dataset}_${seed}.log"
            sleep 10

            unset CUDA_VISIBLE_DEVICES
        done
    done
done

printf "Multiple experiments started.\n"
