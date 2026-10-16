# MultiPert 使用的单细胞多组学扰动数据

## 是什么

MultiPert 复用的 RNA–蛋白、RNA–染色质及染色质–蛋白数据集合。主实验的蛋白来自抗体衍生标签（ADT），**不是质谱全蛋白组**。它适合检验多组学扰动预测，但不能直接替代 ProteinTalks 数据。

## 子数据集

下表规模来自本地正式版 PDF 的 Datasets 小节；是该方法使用的处理口径，并非原始项目总规模。

| 子目录 | 生物背景 | 模态与扰动 | 论文使用规模 | 用途 |
|---|---|---|---|---|
| [thp1](thp1/README.md) | THP-1 急性髓系白血病细胞 | ECCITE-seq；RNA + ADT；基因敲除 | 8,984 细胞、16,826 基因、4 蛋白；10 种单基因扰动，过滤后评估 9 种 | 主模型与未见扰动测试 |
| [kidney](kidney/README.md) | 人胚肾上皮细胞 | CaRPool-seq；RNA + ADT；7 种扰动 | 8,802 细胞、20,639 基因、7 蛋白 | 跨组织、跨技术评估 |
| [pbmc](pbmc/README.md) | 人 PBMC | RNA + ATAC / ATAC + ADT；IL2 与 anti-CD3/CD28 处理 16 h | 细胞与特征数需查原始文件 | 额外模态实验 |

## 来源与获取

- 论文：[MultiPert，PLOS Computational Biology 2026](https://doi.org/10.1371/journal.pcbi.1014054)。
- THP-1：[Zenodo 7041849](https://zenodo.org/records/7041849)。
- 肾脏：[GEO GSE213957](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE213957)。
- PBMC：[GEO GSE156478](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE156478)。
- 作者代码：[MengyuanZhaoo/MultiPert](https://github.com/MengyuanZhaoo/MultiPert)。

以上是论文登记的入口，本次未实际下载或重新验证数据包可访问性。

## 状态

📝 已核对论文中的数据说明；数据矩阵、样本元数据及作者 demo 尚未下载到本仓库。PDF 已下载不等于数据已获取。

## 输入与整理约定

作者仓库说明使用 `RNA.h5ad`、`protein.h5ad` 和扰动嵌入 `pert_embeddings.npz`；本次未审查数据读取代码，因此矩阵放在 `.X` 还是 `.layers`、具体 `.obs` 字段及轴顺序仍待核对。

建议保存原始 RNA/ADT 计数、细胞条码、基因与抗体标识、靶基因、对照标签、批次与实验条件。两模态需通过条码关联，不按行号默认配对；仅在两个模态都存在时启用相应监督。

数据实体放各子目录 `raw/`，可复现转换结果放 `processed/`；跨模态对齐不能把测试扰动的响应标签带入预训练嵌入。

## 与本项目的关系

适合先验证联合预测架构和模态专用损失。蛋白仅 4 或 7 个，且主任务是遗传扰动，不能据此宣称已经验证小分子对数千质谱蛋白的泛化。PBMC 的 GSE156478 还被 [MultiVI](../multivi/README.md) 使用，但子集和预处理未必相同。

## 核验依据

- [本地 PDF](../../pdf/multipert.pdf)：Data availability statement；Materials and methods → Datasets、Preprocessing、Integrative training。
- [论文方法介绍](../../docs/literature/multipert.md)。字段建议是本项目的整理方案，不是已核验的作者文件 schema。
