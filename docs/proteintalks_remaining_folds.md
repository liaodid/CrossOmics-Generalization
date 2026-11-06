# 其余 15 个细胞系：训练、验证和独立测试

> 2026-11-06 归档更新：下文保留 11 月 2 日初始 batch_size=32 的运行方案。随后 15 折完成的正式结果实际使用 **batch_size=64**，此前 BT20 的 32 批大小运行已中断并保留记录。当前结果见 [进度快照](progress-2026-11-06.md)。脚本已统一放在仓库 `script/`，克隆后无需另传脚本压缩包；如需重新运行同配置，须显式添加 `--batch_size 64`，先做 dry run，避免重复已完成实验。

2026-11-02。MCF7 和 HS578T 已完成，不重复运行。当前协议沿用 HS578T：
batch_size=32、seed=1995、开发集 80%/20%、最多 1000 epoch、patience=500，
每折从头训练，按验证联合损失选择 best_checkpoint.pt。其他参数由单折 launcher 固定。
训练不访问该折的测试集；训练结束后独立 evaluator 执行测试，不依据测试分数修改配置。
同一细胞系在自己的测试折中不能训练，在其他细胞系的开发集中可以出现。

## 上传

本地 outputs/proteintalks_5090/remaining_folds_bundle.zip 内含 script/ 下的四个脚本：
run_proteintalks_remaining.py、run_proteintalks_fold.py、proteintalks_cell_holdout.py、
evaluate_proteintalks_holdout.py。把压缩包内容解压合并到远端
E:\liaodi\CrossOmics-Generalization，脚本放到该项目的 script/ 下。
无需上传数据、权重或重新安装环境。该包只更新脚本，不修改上游源码和环境。

## 远端 PowerShell

```powershell
chcp 65001
Set-Location "E:\liaodi\CrossOmics-Generalization"
conda run --no-capture-output -n proteintalks5090 python -u script/run_proteintalks_remaining.py --dry_run
conda run --no-capture-output -n proteintalks5090 python -u script/run_proteintalks_remaining.py
```

第一条 Python 命令只检查路径和 CSV 候选数量，不写结果、不启动训练。
第二条从 BT20 开始，依次运行其余 15 折。保持终端打开，关闭电脑休眠；
ToDesk 断开本身不等于终止远端进程。不要同时启动另一份批量任务。
不需要额外 Tee-Object，脚本已保存日志。暂时无输出可查看 nvidia-smi 和 train.log。

只运行下一折也可使用：

```powershell
conda run --no-capture-output -n proteintalks5090 python -u script/run_proteintalks_remaining.py --cells BT20
```

每次不带 --resume 都创建一个新批次，不会自动合并其他批次。

## 运行顺序和 CSV 候选数量

这些是完整 6/24/48h 条件数量，一个条件对应一个模型样本，不是单个蛋白数量。
实际训练数量以每折 split_summary.json 为准。

|测试细胞系|训练|验证|测试|
|---|---:|---:|---:|
|BT20|1150|288|92|
|BT549|1153|289|88|
|HCC1143|1151|288|91|
|HCC1187|1159|290|81|
|HCC1395|1156|289|85|
|HCC1806|1151|288|91|
|HCC1937|1162|291|77|
|HCC38|1160|291|79|
|HCC70|1157|290|83|
|MDA-MB-231|1149|288|93|
|MDA-MB-436|1155|289|86|
|MDA-MB-453|1148|288|94|
|MDA-MB-453(ATCC)|1160|291|79|
|MDA-MB-468|1156|289|85|
|T47D|1152|289|89|

DU4475 不列为雷达图测试折，但仍可进入其他折的开发数据。
MDA-MB-453 两个名称保持 CSV 中的独立名称，暂不猜测其与论文 -1/-2 的对应关系。

## 结果目录

每折训练文件保持现有结构：

```text
results/proteintalks/cell_holdout/BT20/seed1995_bs32/train_时间_编号/
  selected_model.json
  train.log
  run_status.json
  source_snapshot/
  training/6_24_48h_编号/
    split_summary.json
    train_samples.csv / val_samples.csv / test_samples.csv
    best_checkpoint.pt
    holdout_evaluation/
      holdout_metrics.json
      holdout_predictions.csv
      holdout_proteomics.npz
```

批次管理和汇总位于：

```text
results/proteintalks/batches/remaining_时间_编号/
  batch_state.json
  fold_metrics.csv
  BT20.log / BT549.log / ...
```

fold_metrics.csv 每完成一折更新一次，含各折样本量、测试 AP/AUROC/Accuracy/F1、
归一化蛋白 MSE、最佳 epoch 和训练目录。CSV 中的 AUPRC 为 average precision。
不覆盖已有 MCF7/HS578T 结果，也不混入它们的不同 batch size 成绩。

## 中断与继续

批次遇到错误立即停止，不跳过失败后继续测试其他模型。
对同一个批次，已完成的折会跳过；已训练成功但测试失败的折只重试测试。
如果训练完成后、记录状态前中断，脚本能从新增的 completed 运行目录恢复。
恢复会检查代码和数据哈希，禁止改变配置后混写同一批次。

```powershell
conda run --no-capture-output -n proteintalks5090 python -u script/run_proteintalks_remaining.py --resume "E:\liaodi\CrossOmics-Generalization\results\proteintalks\batches\remaining_实际时间_实际编号"
```

若启动时指定了 --cells 或其他参数，恢复时须提供同样的参数。
训练本身中途失败或中断时不会从中间 checkpoint 恢复；脚本保留日志并停止。
排查原因、确认旧进程退出后，用 --cells 指定未完成的细胞系创建新批次，从头训练。
不要为了恢复而删除失败记录或覆盖原结果。

## 本地检查范围

已对实际 CSV 完成 dry run，并用模拟子进程检查测试失败恢复、已完成折跳过、
权重哈希对应和指标汇总。未在本地启动 GPU 训练。
这些实验为当前公开数据上的独立留细胞系验证；原论文划分及标签版本尚未完全对齐。
MCF7 既有 batch size=8，后续若统一比较可另设固定协议重新训练，保留原结果。
