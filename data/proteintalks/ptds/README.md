# PTDS：ProteinTalks 主数据集（乳腺癌，3 个时间点）

PTDS 即 ProteinTalks Dataset（按 mtPTDS 的全称推断）。总体来源、获取方式和代码输入格式见上一级 [README](../README.md)。

## 内容（摘自论文正文与 Reporting Summary，2026‑10‑15 核对）

| 项目 | 内容 |
|---|---|
| 细胞系 | 18 个乳腺癌细胞系：16 个三阴性（TNBC），2 个非三阴性。完整名单在论文补充表 1a |
| 扰动 | 63 种 FDA 批准小分子药物（分 5 大类、13 小类），加 59 种药物组合；组合参考已发表的组合筛选，共选了 914 个“药物组合 × 细胞系”组合 |
| 时间点 | 6 h、24 h、48 h，外加 0 h 基线 |
| 重复 | 生物学三重复 |
| 规模 | 16,311 个 DIA‑MS 质谱文件（约 6,668 小时仪器时间），另有 23,482 个细胞毒性测量 |
| 公开形式 | PTDS 蛋白矩阵在 https://db.prottalks.com （学术、非商业用途）；原始质谱在 iProX IPX0007409000 |

## 在论文中的用途

- ProteinTalks 的主要训练数据。
- 留一细胞系交叉验证（17 个可评估细胞系）：AUPRC 0.89，AUROC 0.95。
- 留一药物交叉验证：AUPRC 0.57，AUROC 0.64。

## 与 LINCS 转录组的重合（2026‑10‑15，`script/lincs_cell_line_coverage.sh`）

论文正文提到的乳腺癌细胞系中，在 LINCS 里能按常见命名找到的有：

| 细胞系 | LINCS 化合物签名（Phase I / Phase II） | LINCS CRISPR 敲除 |
|---|---|---|
| MCF7（非三阴性） | 29,312 / 12,737 | 有（Phase II，约 353 个基因 × 2 批） |
| BT20 | 1,406 / 1,416 | 无 |
| HS578T | 1,400 / 1,412 | 无 |
| MDA‑MB‑231 | 1,405 / 1,411 | 无 |

HCC 系列、MDA‑MB‑453、MDA‑MB‑468、BT549、T47D 等，在 LINCS 中按常见命名没有找到。
**MCF7 确实属于 PTDS**（2026‑10‑16 由 PTDS 样本表确认）。按化学结构匹配，MCF7 上有 20 种 PTDS 药物在 LINCS 中也有签名，
共 200 条 RNA 签名、174 个 PTDS 样本（不限剂量和时间），详见 [docs/findings.md 第 11 节](../../../docs/findings.md) 和
[reports/ptds-unipert-2026-10-16/](../../../reports/ptds-unipert-2026-10-16/)。它和 A375 是转录组 + 蛋白组联合训练最有价值的两个细胞系。

## 状态

🟡 部分获取（2026‑10‑16）：

| 文件 | 状态 | 说明 |
|---|---|---|
| `01_sample_info.xlsx`（PTDS 样本表） | 项目成员本地已有 | SHA256 `01b2497c43c0de79621c383fe9686854a1c58e22b779837d76270190f58f2007`（记录于 `reports/ptds-unipert-2026-10-16/summary.json`）。列包括 `Sample_ID`、`Cell_Line`、`Pert_Name1/2`、`Pert_Does1/2`（剂量）、`Pert_Time`、`BioRep`、`Machine`、`Drug_Type`。按约定应放在本目录的 `raw/` 下 |
| 蛋白强度矩阵 | 未获取 | 正在与西湖作者联系 |

拿到其余文件后，原始文件放 `raw/`，整理好的数据放 `processed/`，并在此登记文件清单和 SHA256。
