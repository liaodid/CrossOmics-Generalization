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
