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
