# UniPert-G2CP 作者发布的数据、权重与中间结果

## 是什么

UniPert‑G2CP 论文作者在 Zenodo 发布的全部实验资源：处理好的 LINCS 和 CP‑JUMP1 数据、
PubChem 化合物‑靶点对、参考蛋白序列、UniPert 模型权重和中间结果。
复现 [Baseline 1](../../baseline/unipert-g2cp/README.md) 需要这些文件。

## 来源

- Zenodo：https://doi.org/10.5281/zenodo.20355906
- 论文：UniPert-G2CP bridges genetic and chemical screens from molecular representation to phenotype modeling，Cell，2026，https://doi.org/10.1016/j.cell.2026.06.005

## 状态

⏳ 待获取。下载包的文件清单尚未核对。

## 上游代码期望的位置

上游代码按以下相对路径读取数据（相对于 `baseline/unipert-g2cp/`）：

| 用途 | 期望路径 |
|---|---|
| UniPert 训练与推理数据 | `UniPert/data/`，如 `ref_target_seq.fasta`、`processed_pubchem_CPI_24Jan_cid8533_ua4250_i53963.csv` |
| UniPert 发布的推理模型 | `UniPert/current_model/` |
| G2CP 的 LINCS 数据 | `G2CP/data/LINCS/<细胞系>/<细胞系>_gene_chem_ctrl_adata.h5ad`，细胞系为 A549、A375、MCF7、PC3、HT29 |
| G2CP 的 CP‑JUMP1 数据 | `G2CP/data/CPJUMP1/<细胞系>/<细胞系>_gene_chem_ctrl_adata.h5ad`，细胞系为 A549、U2OS |

## 建议的存放方式

实体文件放在本目录 `raw/` 下，再从 baseline 目录建软链接，避免把大文件散落在代码目录里：

```bash
# 在仓库根目录执行；路径按解压后的实际层级调整
ln -s ../../../data/unipert-g2cp-zenodo/raw/UniPert/data baseline/unipert-g2cp/UniPert/data
ln -s ../../../data/unipert-g2cp-zenodo/raw/G2CP/data    baseline/unipert-g2cp/G2CP/data
```

## 使用注意

- 上游代码中有 96 处写死的作者机器路径（`/data/liyiming/...`、`/fionafyang/...`），放好数据后仍需修改，
  详见 Baseline 1 README 的 5.2 节。
- 下载后在本 README 中补充文件清单、大小与 SHA256。

## 本地 PDF 核查补充（2026-10-15）

依据 [unipert-g2cp.pdf](../../pdf/unipert-g2cp.pdf) 的 Datasets 与 Data availability。该文件为 **bioRxiv 2025 v2**，DOI [10.1101/2025.02.02.635055](https://doi.org/10.1101/2025.02.02.635055)；不是 Cell 2026 正式版，不能把两版补充表的数字混用。

| 原始资源 / 子集 | PDF 明确说明的内容 | 获取入口 / 存放建议 |
|---|---|---|
| LINCS 双域数据 | CMap2020 Level 5；A375、A549、HT29、MCF7、PC3；CRISPR 96 h，化合物 10 μM、24 h | [CMap2020](https://clue.io/data/CMap2020#LINCS2020)；优先复用作者处理文件 |
| CPJUMP1 | A549、U2OS；838 维 well-level 形态特征，由 CellProfiler / Pycytominer 处理 | [jump-cellpainting](https://github.com/jump-cellpainting)；这是形态而非蛋白组 |
| Dixit / Norman | GEARS 提供的遗传扰动处理数据 | [GEARS 数据说明](../gears/README.md) |
| sci-Plex3 / HDAC 子集 | 来源为 CPA；HDAC 留药物实验采用 17 种抑制剂、1 μM、24 h、3 细胞系 | [CPA 数据说明](../cpa/README.md)；保留作者筛选版本 |
| 序列、靶点与先验 | HGNC/UniProt 蛋白序列与家族，PubChem compound–target，ChEMBL 靶点/MOA 注释 | 它们属于编码器输入和注释，不是处理后蛋白丰度监督 |

上面的原始来源由预印本核对；本文件开头的 Zenodo 20355906 是此前登记的正式版发布入口，本次未打开其文件清单，也不把它当作在旧预印本已出现的 accession。

**状态仍为待获取**：本次只补文档，没有下载训练数据。建议保留 raw 原件、AnnData 的表达层/扰动向量、基因顺序、对照与作者固定划分；实际 `.obs`/`.uns` 字段需按数据文件和本地模型代码核对。[论文介绍](../../docs/literature/unipert-g2cp.md)。
