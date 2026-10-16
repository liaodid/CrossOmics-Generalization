# GEARS：本地 G2CP 骨干和遗传扰动知识图基线

> 整理日期：2026-10-15。阅读优先级：**P1**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。

## 论文与代码

- **正式引用 / 目标论文：** Yusuf Roohani; Kexin Huang; Jure Leskovec. **Predicting transcriptional outcomes of novel multigene perturbations with GEARS.** Nature Biotechnology, 2023.
- DOI：[10.1038/s41587-023-01905-6](https://doi.org/10.1038/s41587-023-01905-6)
- 本地文件：[本地 PDF](../../pdf/gears.pdf)
- **实际下载版本：** 出版社论文版本。
- 下载稿标题：Predicting transcriptional outcomes of novel multigene perturbations with GEARS。
- 下载稿 DOI：[10.1038/s41587-023-01905-6](https://doi.org/10.1038/s41587-023-01905-6)。
- 篇幅：23 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：https://github.com/snap-stanford/GEARS
- 数据：见作者仓库公开的 Perturb-seq 数据

## 为什么值得优先阅读

G2CP 直接使用了 GEARS 骨干，MultiPert 也利用其扰动表示。它是理解现有代码和共享扰动表示来源的关键。

## 方法概要

分别以基因共表达图和 GO 派生图传播基因嵌入与扰动嵌入，将多个扰动组合为细胞响应表征，通过跨基因层和基因特异输出预测处理后表达。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 状态输入 | 未扰动表达 | 基因状态表示 |
| 扰动输入 | 被扰动的一个或多个基因、GO 图 | 组合扰动表示 |
| 响应预测 | 图传播和跨基因融合 | 处理后转录组 |

## 论文中的评价设置与结果解读

原文评估单基因未见扰动，以及双基因组合中零个、一个或两个组分从未被扰动的设置。指标包含差异表达基因误差、变化量相关性与遗传交互识别。在线发表为 2023 年，卷期归档为 2024 年。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 可以帮助理解 G2CP 如何从控制表达预测变化，以及如何为遗传辅助数据构造先验。药物映射到靶点后并不等同于基因敲除，两类干预应保留区别。

## 局限与对比时需要注意的条件

没有直接的化合物结构输入，也没有蛋白组监督。GO 图能提供生物先验，但若以全数据计算共表达或预训练响应表示，需要区分可允许的信息与测试标签泄漏。

## 复现与接入建议

对照本地 G2CP/backbone_model/GEARS 读原文 Fig. 1 和 Methods；保留 no-perturb 与简单线性基线，不只比较复杂模型之间的分数。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.1038/s41587-023-01905-6](https://doi.org/10.1038/s41587-023-01905-6)
- [https://www.nature.com/articles/s41587-023-01905-6](https://www.nature.com/articles/s41587-023-01905-6)
- [https://github.com/snap-stanford/GEARS](https://github.com/snap-stanford/GEARS)
- 实际 PDF 来源：[下载地址](https://www.nature.com/articles/s41587-023-01905-6.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
