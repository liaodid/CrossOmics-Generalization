# colab/：探索性 Notebook

放在 Google Colab 上运行的探索性 notebook。
成熟、需要反复运行的逻辑应整理成 `script/` 中的脚本。

约定：

- 文件开头写清目的、数据来源、运行环境，以及输出保存在哪里。
- 输出若存放在个人 Google Drive，要在本 README 中注明路径；其他成员无法直接访问，关键结论需另外记录到 [docs/findings.md](../docs/findings.md)。
- 提交前保留关键单元的输出，便于不运行也能看到结果。

上游论文的作图 notebook 不在这里，而在 `baseline/unipert-g2cp/analysis_assets/`。
它们通过 `../UniPert/...` 这样的相对路径读取文件，必须与上游代码放在一起。

## Notebook 清单

| Notebook | 目的 | 结果 | 输出位置 |
|---|---|---|---|
| [hepg2_alignment_drive.ipynb](hepg2_alignment_drive.ipynb) | 为 HepG2 的药物扰动蛋白组（MSV000101671）寻找同细胞、同药、同剂量、同时长的转录组数据，并做基因层面的 RNA‑蛋白对齐 | **对齐的基因行数为 0**：GSE51952 没有可用配对，LINCS Phase I 按药名匹配为 0；之后的 RNA 差异计算、蛋白统计下载和基因映射都没有执行 | 作者的 Google Drive：`MyDrive/virtualcell_hepg2_alignment_v1/` |

### hepg2_alignment_drive.ipynb 的已知问题

- 只检查了 LINCS Phase I。Phase II 中 HepG2 在 24 h、10 µM 下有 268 种化合物，没有被检查。
- 药名精确匹配不去除盐型，蛋白组那边的药名（如 “Abemaciclib (methanesulfonate)”）几乎不可能对上 LINCS。
- 第 1 节的数据仓库读取失败，改用了 `jymbcrc/drug-portal`。2026‑10‑15 已核对：MassIVE 数据集的提交者账号名与它一致，基本可以确定是作者本人发布的处理结果。
- 这个 notebook 由 AI 工具生成，第 1 个单元中关于“未读到本地 PDF”等说明，描述的是生成时的工具环境。
