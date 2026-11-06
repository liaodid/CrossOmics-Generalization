# HS578T 留细胞系训练与验证

下一折固定为 HS578T。使用现有作者处理数据，不载入官方或 MCF7 权重。
HS578T 全部完整条件留作测试；其余细胞系（包括 MCF7）进入开发集。
开发集按独立随机种子 1995、80%/20% 划分训练和验证，维持现有标签与 NaN 处理规则。

当前 CSV 的完整条件候选数量：训练 1,156；验证 290；HS578T 测试 84。
实际以官方 Dataset 加载后的 split_summary.json 为准。

## 训练配置

- batch_size=32，比上一折的 8 增大；先做 2 epoch 的显存/流程检查。
- 正式训练最多 1,000 epoch，验证联合损失连续 500 epoch 不改善则停止。
- AdamW，learning_rate=0.0005，weight_decay=0.0001，hidden_size=64，dropout=0。
- 联合损失中表型权重 0.8，普通确定性模型，不使用 SWAG。
- HS578T 的测试 loader 不进入 Trainer，结束后也不自动测试。
- batch size 的变化改变每轮更新步数和优化过程；不能仅将相对 MCF7 的成绩差异归因于细胞系。

## 5090 Windows 上执行

把 `script/run_proteintalks_fold.py` 上传到远端项目的 `script/` 文件夹，保留已有最新版的
`proteintalks_cell_holdout.py`。不需要重新安装环境。

```powershell
chcp 65001
cd "E:\liaodi\CrossOmics-Generalization"

conda run --no-capture-output -n proteintalks5090 python -u script/run_proteintalks_fold.py --holdout_cell_line HS578T --batch_size 32 --mode smoke
```

先确认上面的检查成功，再执行正式训练：

```powershell
conda run --no-capture-output -n proteintalks5090 python -u script/run_proteintalks_fold.py --holdout_cell_line HS578T --batch_size 32 --mode train
```

可添加 `--dry_run` 只检查路径、显示计划，不创建结果目录，不启动 GPU 工作。
启动前应确认 GPU 可用。正式训练从随机初始化重新开始，不接续 smoke 的权重。

## 结果存储

每次都生成唯一目录，不覆盖先前实验，也不覆盖短程与正式运行：

```text
results/proteintalks/cell_holdout/HS578T/seed1995_bs32/
  smoke_日期_时间_唯一后缀/
  train_日期_时间_唯一后缀/
    command.json
    environment_freeze.txt
    gpu_before.txt
    train.log
    run_status.json
    selected_model.json
    source_snapshot/
    training/
      6_24_48h_唯一编号/
        split_summary.json
        train_samples.csv / val_samples.csv / test_samples.csv
        train_indices.pt / val_indices.pt / test_indices.pt
        best_checkpoint.pt
        training_log.pkl
        其他官方输出
```

- `train.log`：实时记录子进程标准输出、警告和错误，不需要额外 Tee-Object。
- `run_status.json`：起止时间、参数、训练 PID、退出码、完成/失败/中断状态。
- `source_snapshot/`：启动时的入口和上游 Python 代码，不拷贝大型数据。
- `split_summary.json`：数据和代码哈希、环境、实际划分等，沿用原入口。
- `selected_model.json`：最佳普通 checkpoint 的路径、SHA256、轮次和验证指标。
- 指标 NaN/Inf 在机器可读摘要中写为 null，不将其当有效成绩。
- 使用 `best_checkpoint.pt`，不要依据带最佳 epoch 文件名的 `.pth` 推断其真实参数轮次。

只有完成正式训练后，才用独立 evaluator 和该折保存的 test_samples.csv 进行测试。
训练入口依然按官方代码主要每 200 epoch 输出进度，中间无新输出不等于卡死。
遇显存不足时保留失败日志，降低 batch_size 后启动新的运行目录，不混写结果。

## 本地验证范围

完成路径/参数 dry run、Python 语法检查和条件数量核查。
GPU 训练由远端 5090 执行，本地未启动训练，也未评价 HS578T。
