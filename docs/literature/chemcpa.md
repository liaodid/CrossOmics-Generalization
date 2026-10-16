# chemCPA：RNA 大数据迁移与未见药物预测的关键先例

> 整理日期：2026-10-15。阅读优先级：**P0**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。

## 论文与代码

- **正式引用 / 目标论文：** Leon Hetzel; Simon Böhm; Niki Kilbertus; Stephan Günnemann; Mohammad Lotfollahi; Fabian Theis. **Predicting Cellular Responses to Novel Drug Perturbations at a Single-Cell Resolution.** NeurIPS, 2022.
- DOI：[10.52202/068431-1937](https://doi.org/10.52202/068431-1937)
- 本地文件：[本地 PDF](../../pdf/chemcpa.pdf)
- **实际下载版本：** NeurIPS 2022 会议论文。
- 下载稿标题：Predicting Cellular Responses to Novel Drug Perturbations at a Single-Cell Resolution。
- 下载稿 DOI：[10.52202/068431-1937](https://doi.org/10.52202/068431-1937)。
- 篇幅：12 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：https://github.com/theislab/chemCPA
- 数据：见作者仓库的 LINCS 与 sci-Plex 处理数据

## 为什么值得优先阅读

它直接研究如何用 bulk RNA 高通量数据改善较小目标数据上的药物泛化，与用大规模 RNA 帮助稀缺蛋白任务的动机相近。

## 方法概要

沿用 CPA 的基础状态与属性解耦，引入化合物结构编码器，把分子嵌入和剂量映射为扰动向量。在潜在空间将基础状态、细胞系属性和剂量缩放的药物效应相加，再解码；通过架构调整处理来源和目标基因集合的差异。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 细胞输入 | RNA 表达与细胞属性 | 解耦基础状态 |
| 药物输入 | 分子表示与剂量 | 可泛化扰动向量 |
| 解码与迁移 | 组合隐表示、来源/目标数据 | 未见药物的转录响应 |

## 论文中的评价设置与结果解读

NeurIPS 2022 正式论文评估未见药物及药物–细胞组合，并比较 bulk 预训练对单细胞预测的帮助，包括来源和目标基因集合不同的情况。论文结论不能直接等同为 RNA 到蛋白迁移已获验证。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 为本项目的‘RNA 预训练再蛋白微调’提供强对照。应与同步联合训练在同样 RNA 数据、参数量及蛋白训练预算下比较，区分数据增加和训练策略的效应。

## 局限与对比时需要注意的条件

原始任务仍是 RNA 到 RNA，输出分布与蛋白不同。固定细胞系嵌入也不自动支持完全未见的细胞系；未见组合与全新药物必须分别报告。

## 复现与接入建议

阅读方法第 3 节和迁移部分，对照作者模型编码器、分子特征和剂量函数。优先做轻量的预训练迁移版本，并防止 RNA 数据提前包含蛋白测试药物响应而未披露。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.52202/068431-1937](https://doi.org/10.52202/068431-1937)
- [https://papers.nips.cc/paper_files/paper/2022/hash/aa933b5abc1be30baece1d230ec575a7-Abstract-Conference.html](https://papers.nips.cc/paper_files/paper/2022/hash/aa933b5abc1be30baece1d230ec575a7-Abstract-Conference.html)
- [https://arxiv.org/abs/2204.13545](https://arxiv.org/abs/2204.13545)
- 实际 PDF 来源：[下载地址](https://proceedings.nips.cc/paper_files/paper/2022/file/aa933b5abc1be30baece1d230ec575a7-Paper-Conference.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
