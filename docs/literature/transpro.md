# TransPro：最直接的跨组学药物扰动先例与候选基线

> 整理日期：2026-10-15。阅读优先级：**P0**。PDF：**需手动下载**。
> 核验范围：未取得可验证的本地 PDF；本介绍依据出版社/PMC HTML 正文与作者仓库，属于初步阅读笔记。

## 论文与代码

- **正式引用 / 目标论文：** You Wu; Qiao Liu; Lei Xie. **Hierarchical multi-omics data integration and modeling predict cell-specific chemical proteomics and drug responses.** Cell Reports Methods, 2023.
- DOI：[10.1016/j.crmeth.2023.100452](https://doi.org/10.1016/j.crmeth.2023.100452)
- 本地文件：[出版社入口](https://doi.org/10.1016/j.crmeth.2023.100452)（自动获取未成功）
- 代码：https://github.com/XieResearchGroup/TransPro
- 数据：https://doi.org/10.5281/zenodo.7699298

## 为什么值得优先阅读

与你的共享药物编码器、转录组输出和蛋白组输出设想高度接近。判断创新性时，应先于一般单细胞基础模型阅读。

## 方法概要

以未扰动转录组表征细胞，用 GNN 表征化学结构，通过注意力建模细胞与药物交互；transmitter 将转录组隐状态传到蛋白组隐状态，两种组学分别解码，并可连接药敏和不良反应预测模块。

| 模块 | 输入 | 输出 / 作用 |
|---|---|---|
| 细胞与药物输入 | 基础转录组、药物结构 | 细胞背景与化学表示 |
| 组学预测 | 药物诱导的隐状态 | 扰动后转录组及蛋白组 |
| 下游表型 | 蛋白组隐状态 | 药敏回归、不良反应分类 |

## 论文中的评价设置与结果解读

原文区分随机划分、未见细胞系和未见化合物的分布外测试。它验证的是化学诱导蛋白组及下游表型预测，与你的终点较接近；不同数据覆盖、蛋白面板和预处理条件下的分数不能直接横比。

以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。

## 与本项目的关系

**以下为针对本项目的分析与建议：** 不能再将‘首次利用 RNA 与蛋白联合建模药物响应’作为未经限定的创新点。更有价值的比较是：本项目能否在质谱全蛋白组、非严格配对数据、药物骨架外推、时间响应或低样本蛋白组迁移中优于 TransPro。

## 局限与对比时需要注意的条件

论文使用 CPPA 等蛋白测量资源，不能直接等同于 ProteinTalks 的深度质谱蛋白组；需要核实共同蛋白、细胞背景和药物覆盖。多阶段训练与联合训练的实际切换顺序必须读代码，不能仅凭结构图认为与拟议方法完全相同。

## 复现与接入建议

优先检查作者数据文件和训练脚本，提取组学损失、缺失标签处理及 OOD 划分。先在共同蛋白集合复现，再设计同数据的蛋白组单任务、RNA 预训练和联合训练消融。

- [x] 核对论文身份和项目相关性。
- [ ] 获取并验证本地 PDF。
- [ ] 在本项目数据上复现；本次未安装或运行该方法。
- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。

## 原始来源与建议阅读位置

- [https://doi.org/10.1016/j.crmeth.2023.100452](https://doi.org/10.1016/j.crmeth.2023.100452)
- [https://pmc.ncbi.nlm.nih.gov/articles/PMC10163019/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10163019/)
- [https://github.com/XieResearchGroup/TransPro/blob/master/README.md](https://github.com/XieResearchGroup/TransPro/blob/master/README.md)
- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。
