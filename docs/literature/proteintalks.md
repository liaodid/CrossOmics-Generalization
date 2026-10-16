# ProteinTalks：本项目既定的蛋白组主要对标对象

> 整理日期：2026-10-15。阅读优先级：**P0**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。 本地 PDF 为早期预印本，正式版的补充结论仅来自明确列出的正式版页面或既有项目记录；不能将两个版本的数字混用。

## 论文与代码

- **正式引用 / 目标论文：** Rui Sun; Liujia Qian; Yongge Li; Tong Liu; Honghan Cheng; Xuedong Zhang; et al.. **An operational perturbation proteomics-based virtual cell model.** Nature, 2026.
- DOI：[10.1038/s41586-026-11001-9](https://doi.org/10.1038/s41586-026-11001-9)
- 本地文件：[本地 PDF](../../pdf/proteintalks.pdf)
- **实际下载版本：** bioRxiv 2025 v1；不是 Nature 2026 正式版。
- 下载稿标题：A perturbation proteomics-based foundation model for virtual cell construction。
- 下载稿 DOI：[10.1101/2025.02.07.637070](https://doi.org/10.1101/2025.02.07.637070)。
- 篇幅：45 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：https://github.com/guomics-lab/PTV-1
- 数据：https://db.prottalks.com ; iProX IPX0007409000

## 为什么值得优先阅读

它直接建模药物扰动后的蛋白组时间响应，并关联药效与协同效应，与你希望提升的蛋白组泛化能力最贴近。

## 方法概要

以对照蛋白组和与蛋白对齐的药物靶点描述驱动神经 ODE，预测多个时间点的蛋白组；结合药物分子指纹、理化性质和预测轨迹，通过表型模块估计药效或组合协同。现有仓库文档记录其蛋白表达与表型联合损失。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 动态模块 | 基础蛋白组、扰动描述、时间 | 药物处理后的蛋白组轨迹 |
| 表型模块 | 药物特征、初始蛋白组和预测轨迹 | 药效或组合协同概率 |

## 论文中的评价设置与结果解读

论文包含留细胞系、留药物、新化合物及跨癌种迁移等设置。必须分清药效 AUROC/AUPRC 与逐蛋白响应重建质量；既有 baseline 文档中的数字应在正式版本表图中逐一核实。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 保留它作为主要对标，但需增加转录组辅助训练后的直接消融。特别要注意，正式版扩展数据图 8 已涉及由蛋白组预训练迁移到 PDX 转录组的模型，因此不能笼统宣称 ProteinTalks 完全没有跨组学迁移探索。

## 局限与对比时需要注意的条件

现有训练数据获取仍是瓶颈。模型已有蛋白组与表型多任务训练；新意必须落在额外 RNA 监督如何提升蛋白终点，而非多任务本身。预印本与 Nature 正式版不能混用数字。

## 复现与接入建议

配合 baseline/proteintalks/README.md 阅读模型和输入文件格式。固定相同药物划分、微调预算和对照条件，分别评价 Δ 蛋白相关性与药效分类，记录零样本与少样本的区别。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.1038/s41586-026-11001-9](https://doi.org/10.1038/s41586-026-11001-9)
- [https://www.nature.com/articles/s41586-026-11001-9](https://www.nature.com/articles/s41586-026-11001-9)
- [https://github.com/guomics-lab/PTV-1](https://github.com/guomics-lab/PTV-1)
- 实际 PDF 来源：[下载地址](https://www.biorxiv.org/content/10.1101/2025.02.07.637070v1.full.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
