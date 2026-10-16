# State 使用的单细胞扰动与观测数据

## 是什么

State 的状态转移模型（ST）使用多来源单细胞扰动数据，细胞表示模型（SE）另外使用大规模观测数据。它们没有提供本项目所需的质谱蛋白响应标签。

## 子数据集

下表逐项采用**本地 bioRxiv 2025 v1 的 Table 1**，不是 Cell 2026 正式版统计，也不是独立化合物数量清单。

| ST 数据 | 细胞数 | 扰动数（原表口径） | 背景数（原表口径） | 本项目用途 |
|---|---:|---:|---|---|
| Replogle–Nadig | 624,158 | 1,677 | 4 | 遗传扰动跨背景评估 |
| Jiang | 234,845 | 24 | 30 | 背景迁移；具体实验标签需核对原资源 |
| Srivatsan | 762,795 | 189 | 3 | 药物转录组；与 sci-Plex 同源 |
| McFaline-Figueroa | 354,758 | 122 | 3 | 扰动响应迁移；实验标签需核对原资源 |
| Tahoe-100M | 100,648,790 | 1,138 | 50 | 大规模药物 RNA；参见[已有目录](../tahoe-100m/README.md) |
| Parse-PBMC | 9,697,974 | 90 | 12 donors / 18 cell types | 信号刺激跨 donor/细胞类型 |

SE 的 Table 2 还列出 Arc scBaseCount、CZ CELLxGENE 与 Tahoe 的训练/验证数据；这些观测数据和 ST 的扰动标签必须分别登记。不要把训练、验证及多个表的细胞数相加后声称是无重复的新样本总数。

## 来源与获取

- 本次依据：[本地预印本 PDF](../../pdf/state.pdf)，4.5 Datasets、Table 1/2、Code and model availability。
- 预印本 DOI：[10.1101/2025.06.26.661135](https://doi.org/10.1101/2025.06.26.661135)；正式论文 DOI：[10.1016/j.cell.2026.07.052](https://doi.org/10.1016/j.cell.2026.07.052)。
- 论文列出的复现入口：[ArcInstitute/State-reproduce](https://github.com/ArcInstitute/State-reproduce)；模型代码：[ArcInstitute/State](https://github.com/ArcInstitute/State)。
- Parse-PBMC：论文链接到 [10 million human PBMCs in a single experiment](https://www.parsebiosciences.com/datasets/10-million-human-pbmcs-in-a-single-experiment/)。
- 权重：[SE-600M](https://huggingface.co/arcinstitute/SE-600M)、[ST-Tahoe](https://huggingface.co/arcinstitute/ST-Tahoe)、[ST-Parse](https://huggingface.co/arcinstitute/ST-Parse)。**这些链接是模型权重入口，不代表完整训练数据下载包。**

## 状态

📝 已整理论文列出的来源与口径；本仓库未下载 State 数据。各集合确切下载文件、许可证和版本需按复现入口与原始发布逐项确认，本次未做在线可访问性检查。

## 输入与整理约定

论文将 ST 数据映射到 19,790 个编码蛋白的人类 Ensembl 基因，按每细胞总计数 10,000 归一化并 `log1p`；HVG 实验取每数据集 2,000 个高变基因。保留 raw counts，避免将已经归一化的矩阵再次按原始计数处理。

建议保存细胞条码、扰动、对照、cell line/cell type、donor、batch 和条件标签；实际作者 schema 需读入下载文件后核对。数据实体按 `raw/<source>/`、`processed/<source>/<version>/` 分开存放；Tahoe 和 sci-Plex 已有实体时复用，不重复下载。

## 与本项目的关系

可为 RNA 支路或评价协议提供参考；蛋白标签仍需来自 ProteinTalks 等资源。State 的“蛋白语言模型”特征是序列表征，不是实验测得的蛋白丰度。上下文留出、药物留出和细胞随机划分应分别报告。

## 待核实

原始 accession、各子集过滤步骤、预训练是否包含目标测试药物，以及正式版是否更换数据或划分。[论文介绍](../../docs/literature/state.md)记录方法层面的关系。
