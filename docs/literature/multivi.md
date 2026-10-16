# MultiVI：不完整模态与部分配对数据整合方法

> 整理日期：2026-10-15。阅读优先级：**P1**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。

## 论文与代码

- **正式引用 / 目标论文：** Tal Ashuach; Mariano I. Gabitto; Rohan V. Koodli; Giuseppe-Antonio Saldi; Michael I. Jordan; Nir Yosef. **MultiVI: deep generative model for the integration of multimodal data.** Nature Methods, 2023.
- DOI：[10.1038/s41592-023-01909-9](https://doi.org/10.1038/s41592-023-01909-9)
- 本地文件：[本地 PDF](../../pdf/multivi.pdf)
- **实际下载版本：** 出版社论文版本。
- 下载稿标题：MultiVI: deep generative model for the integration of multimodal data。
- 下载稿 DOI：[10.1038/s41592-023-01909-9](https://doi.org/10.1038/s41592-023-01909-9)。
- 篇幅：15 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：https://github.com/scverse/scvi-tools
- 数据：原文配对 RNA/ATAC、DOGMA-seq 与 TEA-seq 数据

## 为什么值得优先阅读

本项目目前难以获得严格配对 RNA/蛋白数据，MultiVI 对完整多模态与单模态样本共存的处理值得借鉴。

## 方法概要

模态专用编码器生成各自潜在分布，通过对齐约束形成联合表示，再由各模态生成模型解码。主要展示 RNA 与 ATAC，并扩展到含表面蛋白的三模态数据，允许部分样本缺少模态。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 样本输入 | RNA、ATAC 或多模态观测 | 模态专用潜分布 |
| 对齐融合 | 各模态表示及配对信息 | 联合潜状态 |
| 解码 | 联合或单模态推断的状态 | 观测模态和缺失模态估计 |

## 论文中的评价设置与结果解读

作者通过人为拆开配对样本、跨批次整合、缺失模态插补与三模态实验检验性能。插补的相关性不等于未见药物外推，应区分评价问题。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 可借鉴掩码损失、模态专用噪声和部分配对训练。完全不配对、无共同锚点的 RNA 与蛋白数据，仍可能无法识别唯一对应关系。

## 局限与对比时需要注意的条件

主要任务是观测模态整合，不是药物扰动预测。它利用桥接配对数据的能力不能直接推断为无锚点的任意跨组学对齐能力。

## 复现与接入建议

先明确本项目有没有共同细胞条件、共享基因–蛋白映射或少量配对样本，再决定采用何种对齐约束。只有真实蛋白测试标签才能评价预测泛化。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.1038/s41592-023-01909-9](https://doi.org/10.1038/s41592-023-01909-9)
- [https://www.nature.com/articles/s41592-023-01909-9](https://www.nature.com/articles/s41592-023-01909-9)
- [https://pmc.ncbi.nlm.nih.gov/articles/PMC10406609/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10406609/)
- 实际 PDF 来源：[下载地址](https://www.nature.com/articles/s41592-023-01909-9.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
