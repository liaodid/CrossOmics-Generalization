# Tahoe-100M 单细胞药物扰动转录组

## 是什么

大规模单细胞药物扰动转录组图谱：50 个癌细胞系，在约 1,100 个药物‑剂量条件下，
共测了 1 亿个细胞的转录组。采用 “Mosaic” 混池设计，以降低批次效应。

## 来源

- 论文：Zhang, Ubas, Svensson, …, Goodarzi, Yu. Tahoe-100M: Mapping drug-induced molecular phenotypes at single-cell resolution.
  Cell 189, 5945–5961, 2026. https://doi.org/10.1016/j.cell.2026.08.035
- 数据：https://huggingface.co/datasets/tahoebio/Tahoe-100M （论文称为公开发布）

## 状态

⏳ 待评估，尚未下载。数据量很大，下载前应先用 `diskusage_report` 确认存储配额。

## 与本项目的关系

- 细胞系中包含 **HepG2/C3A**（论文图 4G 图注）。它是 HepG2 的克隆衍生株，与 HepG2 不完全相同。
- 这是单细胞数据，而 LINCS 和各蛋白组数据都是群体（bulk）水平的。混用前要先决定聚合方式，例如按条件求伪 bulk。
- State 论文（`docs/references.md`）使用了 Tahoe 的子集。

## 本地 PDF 版本与数据准备补充（2026-10-15）

本次下载的 [tahoe-100m.pdf](../../pdf/tahoe-100m.pdf) 是 **bioRxiv 2025 v2**，标题为 *Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas for Context-Dependent Gene Function and Cellular Modeling*，DOI [10.1101/2025.02.20.639398](https://doi.org/10.1101/2025.02.20.639398)，不是上方引用的 Cell 2026 正式版。

- 该预印本摘要描述约一亿细胞、50 个癌细胞系和约 1,100 个 small-molecule perturbations；正式版和方法复用表的“条件数”统计可能不同，不能直接解释为不同化合物数。
- [State 数据文档](../state/README.md)记录其旧预印本 Table 1 的 100,648,790 细胞与 1,138 扰动，这是 State 使用口径；不能用它自动替换 Tahoe 发布版本的药物清单。
- 预印本 Fig. 4G 涉及 HepG2/C3A；仍须把它与 HepG2 区分。是否包含本项目所需 A375/MCF7、相应药物与浓度，下载元数据后逐项核实，不从“50 个细胞系”推断覆盖。

### 建议的输入与存放

先获取药物与样本元数据，保留原始 cell-line ID、药物结构/标识、剂量及单位、处理时间、对照、plate/batch 和 cell barcode。RNA counts 与归一化层分开，按同细胞系–药物–剂量–时间–批次聚合 pseudobulk，记录每组细胞数；真实基因集合与作者文件键名待文件核对。

作者发布原件放 `raw/`；下载清单和可复现聚合产物放 `processed/<release>/`。State 或其他模型复用该资源时引用同一 raw 位置，只把各自的过滤与划分单独版本化。**本次未下载这些数据，状态仍为待获取。** [论文介绍](../../docs/literature/tahoe-100m.md)。
