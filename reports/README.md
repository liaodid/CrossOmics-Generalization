# reports/：分析结果

存放分析跑出来的**小型结果文件**（CSV、JSON、少量图），让不运行代码的人也能看到结论。

## 约定

- 每次分析一个目录，命名为 `<分析名>-<日期>/`，例如 `ptds-unipert-2026-10-16/`。重跑时新建目录，不覆盖旧结果。
- 目录里至少要有一个 `summary.json`（或 README），写明：
  - 输入数据和版本（最好带 SHA256）；
  - 生成它的代码（`colab/` 或 `script/` 中的哪个文件）；
  - 运行时间、关键参数和主要数字。
- 只放小文件。原始数据、大矩阵、h5ad 不放这里，放 `data/<数据集>/processed/`（不提交）。
- 结论性的数字同步写进 [docs/findings.md](../docs/findings.md)。

## 结果清单

| 目录 | 内容 | 生成代码 | 主要结论 |
|---|---|---|---|
| [ptds-unipert-2026-10-16/](ptds-unipert-2026-10-16/) | PTDS（ProteinTalks 主数据集）与 UniPert‑G2CP 作者的 LINCS MCF7 子集，按化学结构做药物对齐 | [colab/ptds_unipert_lincs_alignment_drive.ipynb](../colab/ptds_unipert_lincs_alignment_drive.ipynb) | MCF7 上 63 种 PTDS 药物中有 20 种在 LINCS 中也有签名：200 条 RNA 签名、174 个蛋白样本，不限剂量和时间；Verteporfin 待复核。见 [findings 第 11 节](../docs/findings.md) |

### ptds-unipert-2026-10-16 里的文件

| 文件 | 内容 |
|---|---|
| `summary.json` | 运行参数和主要计数，含 PTDS 样本表的 SHA256 |
| `schema_audit.json` | 作者 MCF7 h5ad 的列名、形状和扰动类型 |
| `ptds_drug_resolution.csv` | 63 种 PTDS 药物的 PubChem 结构解析结果 |
| `drug_resolution_review.csv` | 解析失败、需要人工复核的药物 |
| `matched_pairs.csv` | 匹配上的“PTDS 药物 ↔ LINCS BRD 编号”，以及两边的样本数 |
| `matched_ptds_samples.csv` | 匹配药物对应的 PTDS 样本（细胞系、剂量、时间、重复） |
| `matched_rna_obs.csv` | 匹配药物对应的 LINCS 签名元数据 |
| `unmatched_ptds_drugs.csv` | 没匹配上的 PTDS 药物 |
