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
| 处理条件 | 24 h，10 µM，每种药 6 个生物学重复 | 2026-10-15 补核本地预印本 Methods 与 Results：已由原文确认；质控后各药的保留重复数仍需样本表核对 |
| 药物元数据 | `drug_meta.parquet` 中唯一药名 170 个；字段有 `drug`、`target`、`pathway`、`research_area`、`n_sig_proteins_total`、显著性阈值、`ai_summary_md` 等 | notebook 运行输出 |

## 使用注意

- 药名带盐型，如 “Abemaciclib (methanesulfonate)”“Adiphenine (hydrochloride)”。与其他数据集按药名匹配会大量漏掉，应改用化学结构标识匹配。
- 训练模型需要的是每种药、每个蛋白的变化量。作者在 `drug-portal` 中发布的 `df_ttest_all*.parquet` 可能已经够用，不一定要从原始质谱重新定量。下载后需核对其中的字段和缺失值处理方式。
- 与 GSE51952 的同条件配对结果为 0，与 LINCS Phase I 的 24 h/10 µM 按药名匹配结果也为 0。
  后者的匹配方法有缺陷（见 [docs/findings.md](../../docs/findings.md)），不能视为最终结论。

## 本地 PDF 核查与获取补充（2026-10-15）

依据新下载的 [robotic-proteomics.pdf](../../pdf/robotic-proteomics.pdf)，bioRxiv 2026 v1；重点核对 Results、Cell treating and Sample preparation、Data Availability 和 Code Availability。

- 原文确认 172 种化合物、1,232 个蛋白组、超过 8,700 个定量蛋白；药物筛选跨 13 块 96 孔板，六个生物学重复。Methods 确认终浓度 10 μM 和处理 24 h。
- 原文数据入口为 **MSV000101671**，FTP：[massive-ftp.ucsd.edu/v12/MSV000101671](ftp://massive-ftp.ucsd.edu/v12/MSV000101671/)；交互与逐药结果：[drug-ai-robotics-proteomics.streamlit.app](https://drug-ai-robotics-proteomics.streamlit.app/)。代码：[xomicsdatascience/AI-robotics-proteomics](https://github.com/xomicsdatascience/AI-robotics-proteomics)。
- 这些是 PDF 提供的入口；上方 `jymbcrc/drug-portal` 与其字段来自此前 notebook 调研，不混写成论文正文列出的文件清单。本次没有在线重新核验门户，也没有新增下载实验数据。

### 输入与存放

训练表达响应优先需要**重复级蛋白强度矩阵、样本表和对照**；逐药差异统计可用于变化量分析，但不能在未核实字段时把 t-test 结果当作重复级表达谱。记录蛋白 accession/基因映射、原始与 log 强度、缺失掩码、药物结构、plate、给药时间剂量和生物/技术重复。

原始文件存 `raw/`，标准化与对照差分放 `processed/`。若只有跨重复的差异统计，需明确模型任务是条件平均变化预测。本地仓库仍未获得训练矩阵；既有元数据在 notebook 作者 Drive 中。[论文介绍](../../docs/literature/robotic-proteomics.md)。
