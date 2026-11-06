# ProteinTalks：MCF7 留出训练

本入口解释“先不使用 MCF7”为：MCF7 不参与训练、验证、早停和模型选择，保留为最终测试集。
没有改动 `baseline/proteintalks/PTV-1-main/ProteinTalks/` 下的官方文件。

## 划分

- 基于官方 `ProteomicsDataset.get_experiment_types()` 的样本顺序。
- 条件 ID 第一个 `_` 前面的字段作为细胞系，使用精确相等判断，避免子串匹配。
- MCF7 全部条件留出；其他细胞系的条件以独立的 Python RNG（seed=1995）打乱。
- 其余条件按 80% 训练、20% 验证；不分层。这是本项目选择，不是已确认的作者原始内部划分。
- 当前 CSV 的完整条件候选数：训练 1,152；验证 288；MCF7 测试 90。实际以服务器官方加载器输出为准。
- 训练、验证样本可以来自相同的非 MCF7 细胞系；只有测试细胞系整体隔离。
- 不使用官方 checkpoint。每次训练从随机初始化开始。
- 暂时保留作者标签与缺失处理：残余空表型被映射为 0；张量 NaN 被替换为 1e-6。MCF7 的 90 个条件中包含之前发现的空标签条件，结果仅属当前数据规则下的实验。
- 不改动上游基线索引选择和逐样本归一化；严格论文复现仍需核实数据版本、标签、基线及 SWAG 设置。

## 服务器使用

把 `script/proteintalks_cell_holdout.py` 上传到服务器项目的 `script/` 下。
所有命令都在项目根目录执行：

```bash
cd /data1/liaod/projects/CrossOmics-Generalization
```

先生成划分，不训练：

```bash
python -u script/proteintalks_cell_holdout.py \
  --holdout_cell_line MCF7 \
  --development_val_fraction 0.2 \
  --split_only \
  --dataset_file_dir data/proteintalks/PTV1_dataset_20261015 \
  --trainval_file_prefix allcelltype_drugpair_crossdrug_ \
  --dir_save results/proteintalks/mcf7_split_audit \
  --random_seed 1995
```

短程训练，检查管线，不测试 MCF7：

```bash
CUDA_VISIBLE_DEVICES=0 python -u script/proteintalks_cell_holdout.py \
  --holdout_cell_line MCF7 \
  --development_val_fraction 0.2 \
  --dataset_file_dir data/proteintalks/PTV1_dataset_20261015 \
  --trainval_file_prefix allcelltype_drugpair_crossdrug_ \
  --dir_save results/proteintalks/mcf7_smoke \
  --random_seed 1995 \
  --total_epoch 2 \
  --batch_size 8
```

完整运行示例（普通确定性模型；不等价于已验证的论文 SWAG 实验）：

```bash
CUDA_VISIBLE_DEVICES=0 python -u script/proteintalks_cell_holdout.py \
  --holdout_cell_line MCF7 \
  --development_val_fraction 0.2 \
  --dataset_file_dir data/proteintalks/PTV1_dataset_20261015 \
  --trainval_file_prefix allcelltype_drugpair_crossdrug_ \
  --dir_save results/proteintalks/mcf7_train \
  --random_seed 1995 \
  --total_epoch 1000 \
  --patience 500 \
  --batch_size 64 \
  --learning_rate 0.0005 \
  --hidden_size 64 \
  --dropout_rate 0 \
  --lambda_pheno 0.8 \
  --evaluate_holdout
```

若显存不足，降低 batch size 并在实验记录中注明。长任务按实验室规定使用 tmux 或作业系统。

不要传 `--test_file_prefix`、`--cp_save_dir_best`、`--train_percent`、`--val_percent` 或 `--test_percent`。
每次运行会新建结果子目录，避免覆盖。不要用短程测试结果选择正式运行参数。

## 输出和测试隔离

- `train_samples.csv`、`val_samples.csv`、`test_samples.csv`：索引、条件 ID、细胞系、有效标签、NaN 替换标记。
- `train_indices.pt`、`val_indices.pt`、`test_indices.pt`：相对官方加载后 Dataset 的索引，不是原始 CSV 行号。
- `split_summary.json`：配置、各组数量、环境版本、输入 CSV 和代码 SHA256。
- `best_checkpoint.pt`：由验证损失选择的最佳普通模型；官方 `Trainer` 的其他日志和图像保持原样。
- 只有显式添加 `--evaluate_holdout` 时，训练结束后才对最佳普通 checkpoint 测试，输出 `holdout_predictions.csv`、`holdout_metrics.json`。
- AUPRC 明确计算为 `sklearn.metrics.average_precision_score`；蛋白 MSE 位于作者预处理后的数值空间。

`Trainer` 始终只接收训练、验证 loader，测试 loader 为 `None`，避免训练过程中重复查看测试集。
即便指定 `--use_swag`，新增的最终测试也只评价 `best_checkpoint.pt`，不评价 SWAG 权重或采样。

## 本地验证范围

### 首次训练卷积报 cuDNN 内部错误

如果在 `model.conv1` 遇到 `CUDNN_STATUS_INTERNAL_ERROR`，先用 `nvidia-smi` 检查设备占用和当前可用资源。
可给短程命令增加 `--disable_cudnn` 进行诊断性重试：仍使用 CUDA GPU，但卷积不通过 cuDNN 后端。
该选项不改变划分和网络结构，但可能影响速度和数值细节，不能据此断言根因已解决。
`split_summary.json` 记录选项及 CUDA/cuDNN 版本和启用状态。不要同时更换 PyTorch 或数据处理。
如果关闭后仍失败，停止反复重试，提供完整报错及设备状态供诊断。

纯 Python 单元测试验证：集合不重叠、MCF7 精确匹配、无样本丢失、固定种子可重复、非法输入失败。
本地 CSV 检查得到 1,152 / 288 / 90 个完整条件候选。
当前本地运行时没有 PyTorch，未执行 GPU 训练或完整模型集成验证；需在已配置环境的服务器上按“划分检查 → 2 epoch 短程训练”验证。

```bash
python -m unittest discover -s script -p test_proteintalks_cell_holdout.py -v
```
