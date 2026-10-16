# UniPert-G2CP：本地已有源码的扰动编码和迁移学习基线

> 整理日期：2026-10-15。阅读优先级：**P0**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。 本地 PDF 为早期预印本，正式版的补充结论仅来自明确列出的正式版页面或既有项目记录；不能将两个版本的数字混用。

## 论文与代码

- **正式引用 / 目标论文：** Yiming Li; Min Zeng; Jun Zhu; Linjing Liu; Fang Wang; Longkai Huang; et al.. **UniPert-G2CP bridges genetic and chemical screens from molecular representation to phenotype modeling.** Cell, 2026.
- DOI：[10.1016/j.cell.2026.06.005](https://doi.org/10.1016/j.cell.2026.06.005)
- 本地文件：[本地 PDF](../../pdf/unipert-g2cp.pdf)
- **实际下载版本：** bioRxiv 2025 v2；不是 Cell 2026 正式版。
- 下载稿标题：Genetic-to-Chemical Perturbation Transfer Learning Through Unified Multimodal Molecular Representations。
- 下载稿 DOI：[10.1101/2025.02.02.635055](https://doi.org/10.1101/2025.02.02.635055)。
- 篇幅：53 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：https://github.com/lynn-1998/UniPert-G2CP_reproduce
- 数据：https://doi.org/10.5281/zenodo.20355906

## 为什么值得优先阅读

本项目已引入它的代码。它为化学与遗传扰动提供共同表示，可作为跨组学模型共享扰动编码器的起点。

## 方法概要

UniPert 对蛋白序列和化合物进行统一表示学习；G2CP 利用遗传扰动训练响应模型，再迁移到化合物响应。现有本地代码显示 G2CP 采用对照表达加预测变化量的残差输出，扰动表示由数据文件提供。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| UniPert | 蛋白序列、结构指纹及靶点关系 | 统一扰动向量 |
| G2CP | 对照表达、扰动向量 | 扰动后的表达谱 |

## 论文中的评价设置与结果解读

论文关注遗传到化学的迁移以及不同细胞环境的泛化；正式版还涉及不同表型域。项目当前入库的具体实现主要用于转录组响应。切勿把‘多模态扰动表示’等同于‘RNA 与蛋白表达共同监督’。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 可以保持 UniPert 编码器相同，仅改变输出端和训练数据：蛋白组单任务、RNA 预训练后微调、RNA/蛋白联合训练。这样更容易归因额外 RNA 是否有用。

## 局限与对比时需要注意的条件

本地已有固定路径、输入数据和运行环境问题，详见既有 baseline 文档。本次没有运行训练。全表达谱相关性可能主要反映对照状态，需同步计算变化量指标。

## 复现与接入建议

先使用已有代码中的最小配置跑通单个划分，确认扰动向量来源与测试药物隔离；不要直接运行大规模后台作业脚本。遗传辅助监督与 RNA 辅助监督应分别消融。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.1016/j.cell.2026.06.005](https://doi.org/10.1016/j.cell.2026.06.005)
- [https://www.sciencedirect.com/science/article/pii/S0092867426006549](https://www.sciencedirect.com/science/article/pii/S0092867426006549)
- [https://github.com/lynn-1998/UniPert-G2CP_reproduce](https://github.com/lynn-1998/UniPert-G2CP_reproduce)
- 实际 PDF 来源：[下载地址](https://www.biorxiv.org/content/10.1101/2025.02.02.635055v2.full.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
