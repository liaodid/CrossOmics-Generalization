# Tahoe-100M：大规模药物转录组辅助训练数据

> 整理日期：2026-10-15。阅读优先级：**P1**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。 本地 PDF 为早期预印本，正式版的补充结论仅来自明确列出的正式版页面或既有项目记录；不能将两个版本的数字混用。

## 论文与代码

- **正式引用 / 目标论文：** Jesse Zhang; Airol A. Ubas; Valentine Svensson; Nicole Thomas; Vishvak Subramanyam; Christopher Carpenter; et al.. **Tahoe-100M: Mapping drug-induced molecular phenotypes at single-cell resolution.** Cell, 2026.
- DOI：[10.1016/j.cell.2026.08.035](https://doi.org/10.1016/j.cell.2026.08.035)
- 本地文件：[本地 PDF](../../pdf/tahoe-100m.pdf)
- **实际下载版本：** bioRxiv 2025 v2；不是 Cell 2026 正式版。
- 下载稿标题：Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas for Context-Dependent Gene Function and Cellular Modeling。
- 下载稿 DOI：[10.1101/2025.02.20.639398](https://doi.org/10.1101/2025.02.20.639398)。
- 篇幅：27 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：未在本次核验中单独确认；以论文 Code availability 为准。
- 数据：https://huggingface.co/datasets/tahoebio/Tahoe-100M

## 为什么值得优先阅读

可为蛋白组稀缺场景提供药物响应监督，但其主要价值是资源与覆盖，不是一个可以直接比较的蛋白预测模型。

## 方法概要

通过 Mosaic 平台把不同细胞模型混合成平衡的 cell villages，对药物条件并行开展单细胞转录组测量，形成大规模药物响应图谱。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 实验条件 | 癌细胞模型、化合物与剂量 | 单细胞转录组测量 |
| 本项目中的用途 | 筛选后的 RNA 响应与元数据 | 共享扰动编码器的辅助监督 |

## 论文中的评价设置与结果解读

正式版摘要报告约一亿转录组、50 个癌细胞系和 1,100 个药物–剂量条件。条件数不能直接当作不同药物数；下载预印本时还需核对版本之间的口径变化。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 先查 A375、MCF7 等目标细胞背景和蛋白数据药物交集，再决定使用哪些条件。可以比较同细胞 RNA、其他细胞 RNA 及全量 RNA 对蛋白组泛化的贡献。

## 局限与对比时需要注意的条件

大量单细胞不是同等数量的独立干预；药物、批次和细胞系分布可能不平衡。即使细胞系相同，也不代表时间、剂量和培养条件严格配对。

## 复现与接入建议

先只下载元数据做交集和划分，按化合物结构规范化，再生成 pseudobulk。预训练数据排除蛋白测试药物与否，需作为两种明确协议报告。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.1016/j.cell.2026.08.035](https://doi.org/10.1016/j.cell.2026.08.035)
- [https://pubmed.ncbi.nlm.nih.gov/42753697/](https://pubmed.ncbi.nlm.nih.gov/42753697/)
- [https://www.tahoebio.ai/news/open-sourcing-tahoe-100m](https://www.tahoebio.ai/news/open-sourcing-tahoe-100m)
- [https://www.biorxiv.org/content/10.1101/2025.02.20.639398v2](https://www.biorxiv.org/content/10.1101/2025.02.20.639398v2)
- 实际 PDF 来源：[下载地址](https://www.biorxiv.org/content/10.1101/2025.02.20.639398v2.full.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
