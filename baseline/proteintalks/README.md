# Baseline 2：ProteinTalks（对标对象）

> 状态：⏳ 代码与数据都未入库。本 README 依据论文 PDF 整理（2026‑10‑15），供决定复现方案时参考。

## 论文与代码

- Sun, Qian, Li, Liu, …, E, Zhou, Wen, Zhu, Guo. **An operational perturbation proteomics-based virtual cell model.** Nature, 2026.
  https://doi.org/10.1038/s41586-026-11001-9 （西湖大学郭天南组等）
- 代码：https://github.com/guomics-lab/PTV-1
  （论文 Code availability 写的是 “project data analysis codes”，其中是否包含完整的模型训练代码，需要克隆后确认）
- 数据：见 [data/proteintalks](../../data/proteintalks/README.md)

## 方法概要

ProteinTalks 是一个**只用蛋白组**的扰动响应模型，分两个模块：

| 模块 | 输入 | 输出 | 做法 |
|---|---|---|---|
| 模块 1（Loss 1） | 加药前的蛋白组 P0h + 药物靶点注释 | 加药后各时间点的蛋白组（6 h、24 h、48 h） | 神经 ODE 建模蛋白组随时间的变化，再重建蛋白组 |
| 模块 2（Loss 2） | 药物分子指纹、药物理化性质、P0h、模块 1 预测的蛋白组轨迹 | 药效（敏感 / 不敏感）、药物组合协同 | 多层感知机 |

模型先在约 3,800 万个蛋白定量值上预训练，在新数据集（如 PTPC）上用少样本微调迁移。

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

- [ ] 获取数据（iProX IPX0007409000 / db.prottalks.com）
- [ ] 克隆 `guomics-lab/PTV-1`，确认是否包含模型代码，记录提交号
- [ ] 跑通论文中的一个评价设置
- [ ] 与 Baseline 1 及本项目方法统一数据划分和指标
