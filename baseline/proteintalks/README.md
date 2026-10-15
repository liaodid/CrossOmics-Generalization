# Baseline 2：ProteinTalks（对标对象）

> 状态（2026‑10‑15）：项目成员已确认，这就是“西湖那篇”，即本项目的主要对标对象。
> **代码已公开**，但还没有放进本仓库；**训练数据还没拿到**。

## 论文与代码

- Sun, Qian, Li, Liu, …, E, Zhou, Wen, Zhu, Guo. **An operational perturbation proteomics-based virtual cell model.** Nature, 2026.
  https://doi.org/10.1038/s41586-026-11001-9 （西湖大学郭天南组等）
- 代码：https://github.com/guomics-lab/PTV-1 ，2026‑10‑15 核对时的最新提交为 `1223e94`，`ProteinTalks/LICENCE.md` 为 MIT 许可证。
- 数据：见 [data/proteintalks](../../data/proteintalks/README.md)

## 代码仓库里有什么（2026‑10‑15 核对）

```text
PTV-1/
├── ProteinTalks/                 # 模型本体（Python 3.10.6）
│   ├── main.py                   #   训练入口
│   ├── model.py                  #   神经 ODE + 表型 head
│   ├── trainer.py / multi_task_learning.py / swag.py   # 训练、多任务损失、SWAG 不确定性
│   ├── dataset.py / config.py / metrics.py / utils.py / plot.py
│   ├── best_checkpoint.pth       #   训练好的权重
│   └── requirements.txt
├── ChemmineR.R                   # 生成 881 维药物分子指纹和 54 维理化性质
├── Differentially expressed analysis.R   # 计算 p 值和倍数变化
├── PertScore calculation.R       # 把蛋白分为上调 / 下调 / 不变
└── mFuzz analysis.R              # 时间序列聚类
```

训练示例（摘自其 README）：

```bash
cd ProteinTalks
python main.py \
    --dataset_file_dir /path/to/dataset/ \
    --trainval_file_prefix allcelltype_drugpair_crossdrug_ \
    --time_stamp_predict_drug 6_24_48 \
    --train_percent 0.7 --val_percent 0.2 --test_percent 0.1 \
    --batch_size 64 --learning_rate 0.0005 --lambda_pheno 0.8 --use_swag
```

需要的 7 个输入文件见 [data/proteintalks](../../data/proteintalks/README.md#代码需要的输入格式)。

### 放进本仓库的方式

按 [docs/collaboration.md](../../docs/collaboration.md) 的 `upstream/...` 流程，把 `PTV-1` 在固定提交上的内容原样放到本目录（`baseline/proteintalks/`），
并新建 `docs/upstream_commit.txt` 记录提交号。`best_checkpoint.pth` 会被 `.gitignore` 忽略，需另行下载。

## 方法概要

ProteinTalks 是一个**只用蛋白组**的扰动响应模型，分两个模块：

| 模块 | 输入 | 输出 | 做法 |
|---|---|---|---|
| 模块 1（Loss 1） | 加药前的蛋白组 P0h + 药物靶点注释 | 加药后各时间点的蛋白组（6 h、24 h、48 h） | 神经 ODE 建模蛋白组随时间的变化，再重建蛋白组 |
| 模块 2（Loss 2） | 药物分子指纹、药物理化性质、P0h、模块 1 预测的蛋白组轨迹 | 药效（敏感 / 不敏感）、药物组合协同 | 多层感知机 |

模型先在约 3,800 万个蛋白定量值上预训练，在新数据集（如 PTPC）上用少样本微调迁移。

代码 README 补充的细节：
- 扰动的输入是一个“与蛋白对齐的扰动描述”，即把药物靶点映射到蛋白上，思路与 UniPert 把药物映射到蛋白空间类似。
- 训练目标是 `(1 − λ) × 蛋白表达 MSE + λ × 表型 BCE`，默认 λ = 0.8。也就是说，**ProteinTalks 本身已经是多任务模型**。
  本项目的新意应落在“加入转录组数据”上。

## 论文中的评价协议与结果（摘录）

| 评价设置 | 指标 | ProteinTalks | 对比方法 |
|---|---|---|---|
| 留一细胞系交叉验证（17 个可评估细胞系） | AUPRC / AUROC / Accuracy | 0.89 / 0.95 / 0.90 | 优于 GeneCompass、Geneformer、UCE、Bagging、KNN、随机森林、DeepSynergy |
| 留一药物交叉验证 | AUPRC / AUROC / Accuracy | 0.57 / 0.64 / 0.76 | AUROC 比转录组基础模型高 13–23% |
| 独立新化合物测试 PTNC（81 种化合物，4 个三阴性乳腺癌系） | AUPRC / AUROC / Accuracy | 0.94 / 0.89 / 0.85 | Geneformer 0.70 / 0.51 / 0.31 等 |
| 跨癌种 PTPC（5 个非乳腺癌系，少样本） | AUPRC / AUROC | 0.41 / 0.77 | Geneformer 0.23 / 0.56，GeneCompass 0.28 / 0.72，UCE 0.19 / 0.54 |

注意：论文的主要评价指标是**药效分类**（AUPRC、AUROC），不是逐蛋白的表达预测误差。
本项目若要对标，需先决定比的是药效预测、蛋白组轨迹预测，还是两者都比。

## 与本项目的关系

- 论文对比的转录组方法都是**单细胞转录组基础模型**（Geneformer、GeneCompass、UCE），没有同时使用转录组和蛋白组扰动数据训练的模型。
  这与本项目“联合两种组学”的设想相关，但“没有人这样做过”仍需系统文献检索确认。
- PTPC 中的 A375 与 LINCS 重合，可作为转录组 + 蛋白组联合训练的首选细胞系候选，见 [docs/findings.md](../../docs/findings.md)。

## 复现进度

- [x] 确认对标对象就是 ProteinTalks（2026‑10‑15）
- [x] 确认公开代码包含完整的模型与训练代码（`guomics-lab/PTV-1@1223e94`）
- [ ] 把代码按固定提交放入本目录
- [ ] 获取训练数据（向西湖作者索取，或通过 iProX IPX0007409000 / db.prottalks.com）
- [ ] 跑通论文中的一个评价设置
- [ ] 与 Baseline 1 及本项目方法统一数据划分和指标
