# HepG2 药物扰动蛋白组（MSV000101671）

## 是什么

美国 Cedars‑Sinai 的 Meyer 实验室用半自动化样品制备、快速质谱和 AI agent 分析做的药物扰动蛋白组筛选：
HepG2 肝癌细胞分别用 172 种化合物处理，然后测蛋白组。
它是 [colab/hepg2_alignment_drive.ipynb](../../colab/hepg2_alignment_drive.ipynb) 中“RNA‑蛋白对齐”探索所用的蛋白侧数据。

## 来源

| 资源 | 内容 |
|---|---|
| MassIVE 数据集 | MSV000101671，“High throughput drug perturbational proteomics with automated interpretation at scale”<br>https://massive.ucsd.edu/ProteoSAFe/dataset.jsp?accession=MSV000101671<br>数据集 DOI 10.25345/C5GX45797，许可证 CC0 1.0 |
| 论文（预印本） | Robotic perturbation proteomics and AI agents enable scalable drug mechanism discovery. bioRxiv, 2026.<br>DOI 10.64898/2026.05.04.722718，PMC：https://pmc.ncbi.nlm.nih.gov/articles/PMC13174343/ |
| 处理结果（作者发布） | GitHub `jymbcrc/drug-portal`：`data/drug_meta.parquet`（药物元数据和 AI 生成的“药物身份卡”）、`data/df_ttest_all*.parquet`（每种药、每个蛋白的差异统计） |

MassIVE 上这个数据集的提交者账号名，和 GitHub 的 `jymbcrc` 一致，所以 `drug-portal` 基本可以确定就是作者本人发布的处理结果（2026‑10‑15 核对）。
notebook 最初尝试的 `xomicsdatascience/AI-robotics-proteomics` 里没有这些文件。

## 状态

📝 仅元数据。只下载了 `drug_meta.parquet`，蛋白层面的差异统计尚未下载。
下载记录保存在 notebook 作者的 Google Drive（`virtualcell_hepg2_alignment_v1/`）中，未进入本仓库。

## 已核实的信息（2026‑10‑15）

| 项目 | 内容 | 出处 |
|---|---|---|
| 细胞 | HepG2 | 预印本摘要 |
| 规模 | 172 种化合物，1,232 个蛋白组样本，定量蛋白超过 8,700 个，约 3 周完成 | 预印本摘要 |
| 仪器 | Orbitrap Astral | MassIVE |
| MassIVE 状态 | Partial Public（部分公开）；页面列出元数据、定量统计结果和转换后的峰文件，未列文件数和总大小 | MassIVE 页面 |
| 处理条件 | 24 h，10 µM，每种药 6 个生物学重复 | notebook 说明，**未对照原文 Methods 核实**；1,232 ≈ 172 × 6 + 对照，数量上吻合 |
| 药物元数据 | `drug_meta.parquet` 中唯一药名 170 个；字段有 `drug`、`target`、`pathway`、`research_area`、`n_sig_proteins_total`、显著性阈值、`ai_summary_md` 等 | notebook 运行输出 |

## 使用注意

- 药名带盐型，如 “Abemaciclib (methanesulfonate)”“Adiphenine (hydrochloride)”。与其他数据集按药名匹配会大量漏掉，应改用化学结构标识匹配。
- 训练模型需要的是每种药、每个蛋白的变化量。作者在 `drug-portal` 中发布的 `df_ttest_all*.parquet` 可能已经够用，不一定要从原始质谱重新定量。下载后需核对其中的字段和缺失值处理方式。
- 与 GSE51952 的同条件配对结果为 0，与 LINCS Phase I 的 24 h/10 µM 按药名匹配结果也为 0。
  后者的匹配方法有缺陷（见 [docs/findings.md](../../docs/findings.md)），不能视为最终结论。
