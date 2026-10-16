# HepG2 药物与蛋白降解剂扰动蛋白组（Basu et al., 2026）

## 是什么

一项用高通量蛋白组研究蛋白降解剂肝毒性的工作，包含 HepG2 上的常规药物和 AR 靶向降解剂两部分。
它是项目成员提出的候选 HepG2 蛋白组数据。

## 来源

- 论文：Basu, Yu, …, Mülleder, Moreau, Ralser. Proteome-guided drug discovery maps and mitigates therapeutic degrader toxicity.
  Nature Chemical Biology, 2026‑10‑09. https://doi.org/10.1038/s41589-026-02347-2
  （标题、作者、期刊、日期经 Crossref 核实）
- 原始质谱：[PRIDE PXD062492](https://www.ebi.ac.uk/pride/archive/projects/PXD062492)。
- 最小分析数据集：[figshare 28578113](https://doi.org/10.6084/m9.figshare.28578113)。
- 代码：[Ralser-Lab/Proteomic-drug-discovery](https://github.com/Ralser-Lab/Proteomic-drug-discovery)。
- 以上编号已于 2026-10-15 从新下载的 [degrader-proteomics.pdf](../../pdf/degrader-proteomics.pdf) 的 Data availability / Code availability 确认；本次未访问数据包或核验实际文件清单。

## 状态

📝 已获取正式论文 PDF，并核对数据入口；**实验数据尚未下载**。此前“全文未读到、编号未找到”的记录已由本轮核查更新。PDF 在根目录 `pdf/`，不是 `docs/papers/`。

## 已知信息及可信度

| 内容 | 可信度 | 出处 |
|---|---|---|
| HepG2 是主要筛选背景；其他功能验证的细胞/原代样本须与主矩阵区分 | 高（主筛选） | 正式 PDF Results 与 Methods |
| 78 种 FDA 批准药，其中 31 种引起显著蛋白组变化、47 种没有 | 高 | 正式 PDF Results、Fig. 1 |
| 204 个 AR 靶向双功能降解剂（HBD） | 高 | 正式 PDF Results、Fig. 2 |
| 常规药物部分一致定量 3,331 个蛋白 | 高 | 正式 PDF Results；不是所有子实验的共同覆盖 |
| 降解剂部分设 0.1、1、10 µM 三个浓度，处理 24 h | 高 | 正式 PDF Results |
| HBD 筛选含对照 2,113 个样本、处理矩阵深度 4,043 个蛋白 | 高 | 正式 PDF Results、Extended Data Fig. 1/2；不表示每个样本无缺失测到全部蛋白 |

## 子数据集与文件类型

| 子集 / 资源 | 内容 | 获取与整理建议 |
|---|---|---|
| FDA-approved library | HepG2 常规药物的蛋白响应 | 正文 Supplementary Dataset 1；处理矩阵以 figshare 实际清单为准 |
| Experimental HBD library | 三剂量降解剂的蛋白响应 | 正文 Supplementary Dataset 2；保留化学系列、浓度与对照 |
| 模型/毒性及功能验证 | 通路拟合、预测、毒性分数和功能验证 | Supplementary Datasets 3–5 及 source data；不是都可直接当表达训练矩阵 |
| 原始 MS | 谱图等原始测量 | PRIDE PXD062492；若处理数据充分，不必先下载全部原始谱图 |

## 输入与存放

建议 `raw/fda/`、`raw/hbd/` 分开保留原始发布文件；`processed/<release>/` 放统一蛋白 ID、log 强度/变化量、缺失掩码和样本表。记录化合物结构、linker/化学系列、剂量、时间、plate、重复和对照；文件名与字段 schema 尚待实际下载核实。

## 使用前要回答的问题

1. 论文已给出 PRIDE 与最小分析数据入口；下载后核实实际可取得哪些重复级矩阵、结构与样本表。
2. 核对文件中的计量单位、缺失处理和各子集维度，与上表原文数字逐项对照。
3. 204 个降解剂几乎都是同一靶点（AR）的结构类似物：随机划分会导致训练集与测试集近似重复，应按分子骨架划分；
   以靶点为中心的药物表示（如 UniPert）也可能难以区分这些分子。
4. 78 种药中有 47 种蛋白组无显著变化：多数预测目标接近 0，“预测均值”这类简单基线会很强，评价必须基于变化量。
5. 新闻页提到的 RNA‑seq 是在前列腺肿瘤组织上做的，不是 HepG2，没有可配对的 HepG2 转录组。
