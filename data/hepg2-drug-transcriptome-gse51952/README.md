# HepG2 药物处理转录组芯片（GSE51952）

## 是什么

一个小型的 HepG2 药物处理基因表达芯片数据集。
它在 [colab/hepg2_alignment_drive.ipynb](../../colab/hepg2_alignment_drive.ipynb) 中被用作练习用的替代转录组数据，
与 UniPert‑G2CP 论文无关。

## 来源

GEO：https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE51952
（只用 Series Matrix，不下载 CEL 原始文件）

## 状态

📝 Series Matrix 已下载到 notebook 作者的 Google Drive（`virtualcell_hepg2_alignment_v1/raw/`），本仓库中没有。

## 已知信息（来自 notebook 运行输出）

- HepG2，全部为 24 h，22 种药，105 个样本，每个条件 3 个生物学重复。
- 表达矩阵为 18,988 个特征 × 105 个样本，平台是 Brainarray Entrez CDF。
- 数值范围约 2.9–15，看起来像 log2 尺度，但 notebook 要求对照 GEO 的 `data_processing` 字段确认后才使用（`RNA_SCALE` 尚未填写）。
- 对照组分批次：DMSO_1 至 DMSO_7、PBS_1 至 PBS_4，另有 D‑mannitol；不同批次的 DMSO 不能混用。
- 剂量与蛋白组的 10 µM 大多不同，例如 Acetaminophen 为 10,000 µM。

## 结论

与 [MSV000101671 蛋白组](../hepg2-drug-proteome-msv000101671/README.md) 按药名匹配，只对上 Tolbutamide 一个药，
而且剂量为 2,000 µM，与蛋白组的 10 µM 不同，**没有可用的同条件配对**。
