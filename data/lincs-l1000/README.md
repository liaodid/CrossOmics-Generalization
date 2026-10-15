# LINCS L1000（CMap）

## 是什么

美国 NIH LINCS 计划用 L1000 平台测得的大规模扰动转录组数据：
对很多细胞系施加药物、shRNA 敲低、CRISPR 敲除、基因过表达等扰动，测量表达变化。

- L1000 只直接测 978 个“地标基因”，其余基因由算法推断。
- Level 5 数据是“签名”（signature）：同一条件的重复已经聚合成一条 moderated z‑score，
  不是原始计数，也不是 log2FC，不能把一条签名当作一个独立的生物学重复。

## 来源

| 阶段 | GEO 编号 | 链接 |
|---|---|---|
| Phase I | GSE92742 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE92742 |
| Phase II | GSE70138 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE70138 |

文件说明：https://clue.io/connectopedia/category/Data

## 状态

📝 仅元数据。`script/audit_lincs_metadata.sh` 会把两个阶段的 `sig_info` 表下载到 `raw/metadata/`。
压缩后的 Level 5 表达矩阵约 20 GB，尚未下载。

已下载的元数据文件（2026‑10‑15）：

| 文件 | SHA256 |
|---|---|
| `GSE92742_Broad_LINCS_sig_info.txt.gz` | `19da29c0ee12ddf27f9698cd0da40beaff58657dcde9d382aae068737e831299` |
| `GSE70138_Broad_LINCS_sig_info_2017-03-06.txt.gz` | `b78284478d62029f600d4397334c538d363123110affd2454bf0055bd0678e01` |

## 已核实的事实（2026‑10‑15，由 `script/audit_lincs_metadata.sh` 得出）

- **CRISPR 敲除（`trt_xpr`）只出现在 Phase II**，细胞系为 A375、A549、HA1E、HELA、HT29、MCF7、PC3、YAPC，每个约 353 个基因。
  **HepG2 没有 CRISPR 敲除数据。** 这也解释了 UniPert‑G2CP 为什么只用 5 个细胞系。
- HepG2 的遗传扰动只有 shRNA 敲低：Phase I 中 `trt_sh` 12,868 条（另有 `trt_sh.cgs` 3,341 条、`trt_sh.css` 2,518 条）。
- HepG2 的化合物签名：
  - Phase I：5,774 条，其中 6 h 4,726 条、24 h 1,048 条；24 h 且 10 µM 的有 199 条，涉及 176 种化合物（不少只有 BRD 内部编号）。
  - Phase II：1,775 条，全部为 24 h，剂量 0.04–10 µM；24 h 且 10 µM 的有 305 条，涉及 268 种化合物。

## 使用注意

- 两个阶段 `sig_info` 的列不同：Phase I 的剂量写作 `10 µM`（UTF‑8 的 µ），Phase II 写作 `10.0 um`。
- 药名 `pert_iname` 是不带盐型的小写通用名。与其他数据集按药名匹配时，
  应改用化学结构标识（InChIKey、PubChem CID）匹配，否则带盐型的名字（如 “Abemaciclib (methanesulfonate)”）会全部漏掉。
- Baseline 1 使用的是作者处理好的 LINCS 子集（见 [unipert-g2cp-zenodo](../unipert-g2cp-zenodo/README.md)），不直接读取这里的原始文件。
