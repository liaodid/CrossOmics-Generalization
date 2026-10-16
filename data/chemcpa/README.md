# chemCPA 使用的 LINCS 与 sci-Plex3 数据

## 是什么

chemCPA 在 LINCS bulk RNA 上预训练，在 sci-Plex3 单细胞药物响应上适配和评估；这是 RNA 到 RNA 的跨数据迁移资源，没有配套质谱蛋白标签。

## 子数据集

| 数据 | 生物背景 / 条件 | 本地论文的规模与特征 | 用途 |
|---|---|---|---|
| LINCS L1000 | 多细胞系、小分子 | 约 130 万 bulk 观测、978 landmark 基因、接近 2 万药物 | 预训练；复用[现有 LINCS 目录](../lincs-l1000/README.md) |
| sci-Plex3 | A549、MCF7、K562；188 药物；10 nM、100 nM、1 μM、10 μM | Section 4 报告 649,340 细胞、7,561 基因 | 单细胞适配及未见药物评估 |
| 共同特征 / 扩展特征 | 两数据来源的基因映射 | 977 共同基因；另一个实验扩到 977 + 1,023 HVG = 2,000 基因 | 检验特征空间变化下的迁移 |

各方法对 sci-Plex3 的过滤不同；不要与 CPA、PerturbNet、biolord 的处理后细胞数混用。

## 来源与获取

- [本地 NeurIPS 2022 PDF](../../pdf/chemcpa.pdf)：Section 4 Datasets and transfer learning。
- [作者仓库](https://github.com/theislab/chemCPA)：处理文件、化合物特征和划分应优先按该方法复现说明获取。
- sci-Plex3 原始样本号由同时已下载的 CPA PDF 明确登记为 [GSM4150378](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM4150378)。这是样本号，不应写成 GEO Series。
- LINCS 来源与处理层级见[已有文档](../lincs-l1000/README.md)。

## 状态

📝 论文数据说明已核对；chemCPA 处理矩阵、分子嵌入与预定义划分未下载。本次没有检查在线数据包可访问性。

## 输入与整理约定

建议保存原始计数、归一化表达、基因映射、细胞系、药物名、标准化结构、剂量与对照标签，另存 977/2,000 基因两个版本的顺序和划分。作者 `.h5ad` 具体 `.obs` 键、嵌入与模型版本需按代码核对，不能仅凭文件扩展名确定。

原下载放 `raw/`，转换结果放 `processed/`；大体量 LINCS 实体优先复用已有目录，不复制一套。

## 与本项目的关系及注意

适合作为 RNA 预训练到蛋白微调方案的设计参考。该论文没有证明 RNA 到蛋白迁移有效。若 RNA 数据中含有蛋白测试药物的实测响应，应将其标为跨模态标签迁移；声称全新药物外推时需在两模态训练中共同隔离。

更多方法说明见 [chemCPA 论文介绍](../../docs/literature/chemcpa.md)。
