# CPA：可组合扰动表示与解耦学习基础方法

> 整理日期：2026-10-15。阅读优先级：**P2**。PDF：**已下载**。
> 核验范围：已提取本地 PDF 正文并核对首页；结合下列原始来源整理。

## 论文与代码

- **正式引用 / 目标论文：** Mohammad Lotfollahi; Anna Klimovskaia Susmelj; Carlo De Donno; Leon Hetzel; Yuge Ji; Ignacio L Ibarra; et al.. **Predicting cellular responses to complex perturbations in high‐throughput screens.** Molecular Systems Biology, 2023.
- DOI：[10.15252/msb.202211517](https://doi.org/10.15252/msb.202211517)
- 本地文件：[本地 PDF](../../pdf/cpa.pdf)
- **实际下载版本：** 出版社论文版本。
- 下载稿标题：Predicting cellular responses to complex perturbations in high‐throughput screens。
- 下载稿 DOI：[10.15252/msb.202211517](https://doi.org/10.15252/msb.202211517)。
- 篇幅：19 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。
- 代码：https://github.com/theislab/cpa
- 数据：见作者仓库与原文 Data availability

## 为什么值得优先阅读

多个后续药物响应模型以 CPA 为起点。理解它有助于区分‘已见因子的未见组合’和‘全新药物’这两种泛化。

## 方法概要

通过对抗训练把细胞表达编码为不含扰动与协变量信息的基础状态，将药物、剂量和细胞属性嵌入组合后重建表达；属性可以在推断时重新组合。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 编码 | 单细胞表达与属性 | 基础状态 |
| 组合 | 基础状态、扰动及剂量/背景嵌入 | 目标条件隐状态 |
| 解码 | 组合隐状态 | 目标条件表达分布 |

## 论文中的评价设置与结果解读

论文包含剂量、时间、细胞背景、药物组合和遗传组合等实验；不同实验提供不同形式的泛化证据。只有引入可用的化学结构表示，才能针对未见分子做结构外推。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 可以把 RNA 和蛋白视作不同的输出模态，借用其属性分解思想，但这属于需要实现和验证的扩展。作为基础方法可帮助解释为什么共享扰动空间可能有效。

## 局限与对比时需要注意的条件

基础模型中的离散药物嵌入并不具备新分子的输入表示。潜在空间相加的假设可能无法充分描述复杂非线性与强组合效应。

## 复现与接入建议

优先理解方法总图和 adversarial loss。若使用作者实现做对照，应明确其可接受的输入以及测试扰动是否在训练词表中。

- [x] 核对论文身份和项目相关性。
- [x] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.15252/msb.202211517](https://doi.org/10.15252/msb.202211517)
- [https://github.com/theislab/cpa](https://github.com/theislab/cpa)
- 实际 PDF 来源：[下载地址](https://link.springer.com/content/pdf/10.15252/msb.202211517.pdf)。
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
