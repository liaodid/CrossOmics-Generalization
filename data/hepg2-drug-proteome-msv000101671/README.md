# HepG2 药物扰动蛋白组（MSV000101671）

## 是什么

HepG2 肝癌细胞系在多种药物处理后的蛋白组（质谱）数据。
它是 [colab/hepg2_alignment_drive.ipynb](../../colab/hepg2_alignment_drive.ipynb) 中“RNA‑蛋白对齐”探索所用的蛋白侧数据。

## 来源

- MassIVE 编号：MSV000101671
- 方法论文：https://pmc.ncbi.nlm.nih.gov/articles/PMC13174343/
- 处理结果：
  - notebook 原计划使用 GitHub `xomicsdatascience/AI-robotics-proteomics`，但其中找不到 `data/drug_meta.parquet`；
  - 改用 GitHub `jymbcrc/drug-portal` 的 `data/drug_meta.parquet`（药物元数据）和 `data/df_ttest_all*.parquet`（作者的差异统计）。
  - **`jymbcrc/drug-portal` 与原论文是否为同一份数据，尚未核实。**

## 状态

📝 仅元数据。只下载了 `drug_meta.parquet`，蛋白层面的差异统计尚未下载。
下载记录保存在 notebook 作者的 Google Drive（`virtualcell_hepg2_alignment_v1/`）中，未进入本仓库。

## 已知信息

| 项目 | 内容 | 出处 |
|---|---|---|
| 细胞 | HepG2 | notebook 说明 |
| 处理 | 24 h，10 µM，每种药 6 个生物学重复 | notebook 说明（未对照原文核实） |
| 药物数 | 文献称 172 种；`drug_meta.parquet` 中唯一药名 170 个 | notebook 运行输出 |
| 元数据字段 | `drug`、`target`、`pathway`、`research_area`、`n_sig_proteins_total`、`protein_log2fc` 阈值等 | notebook 运行输出 |

## 使用注意

- 药名带盐型，如 “Abemaciclib (methanesulfonate)”“Adiphenine (hydrochloride)”，与其他数据集按药名匹配会大量漏掉，应改用化学结构标识匹配。
- 与 GSE51952 的同条件配对结果为 0，与 LINCS Phase I 的 24 h/10 µM 按药名匹配结果也为 0。
  后者的匹配方法有缺陷（见 [docs/findings.md](../../docs/findings.md)），不能视为最终结论。
