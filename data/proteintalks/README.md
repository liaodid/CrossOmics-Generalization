# ProteinTalks 扰动蛋白组数据（西湖大学）

## 是什么

西湖大学郭天南组为训练蛋白组虚拟细胞模型 ProteinTalks 产生的大规模药物扰动蛋白组数据（DIA 质谱）。
这是本项目的对标对象 [baseline/proteintalks](../../baseline/proteintalks/README.md) 所用的数据。

## 来源

- 论文：Sun, Qian, Li, Liu, …, Zhu, Guo. An operational perturbation proteomics-based virtual cell model. Nature, 2026.
  https://doi.org/10.1038/s41586-026-11001-9
- 原始质谱数据：ProteomeXchange / iProX，项目编号 **IPX0007409000**
- PTDS 蛋白矩阵及相关资源：https://db.prottalks.com（论文称供学术、非商业用途使用）
- 论文的 Reporting Summary 另写有 “Data are available upon request for non-commercial purposes”，实际能否直接下载需确认。

## 状态

⏳ 待获取。截至 2026‑10‑15，项目成员尚未拿到数据。

## 数据组成（摘自论文正文和 Reporting Summary，2026‑10‑15 核对）

| 子集 | 细胞系 | 扰动 | 时间点 | 规模 |
|---|---|---|---|---|
| PTDS | 18 个乳腺癌细胞系（16 个三阴性、2 个非三阴性） | 63 种 FDA 批准药 + 59 种药物组合 | 6 h、24 h、48 h，生物学三重复 | 16,311 个 DIA‑MS 文件，另有 23,482 个细胞毒性测量 |
| mtPTDS | 3 个细胞系 | 55 种单药 + 57 种组合 | 11 个时间点（0–60 h） | 2,528 个样本 |
| PTPC | A375、HCT116、NCI‑H1975、NCI‑H2170、Panc 10.05 | 708 种老药新用化合物 | 6 h、24 h | 2,307 个样本（2,021 个独立样本），定量 5,171 个蛋白 |

## 与转录组数据的潜在配对

- A375（PTPC 中）是 LINCS 核心细胞系，有大量药物签名，也有 CRISPR 敲除数据。
- 论文正文提到 MCF7 和 T47D，二者可能就是 PTDS 中那 2 个非三阴性系，**需查补充表 1a 确认**。MCF7 同样是 LINCS 核心细胞系，有 CRISPR 敲除数据。
- 同一细胞系上的转录组 + 蛋白组联合训练，在这些细胞系上有数据基础；在 HepG2 上目前没有。
