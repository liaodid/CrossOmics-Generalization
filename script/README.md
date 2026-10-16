# script/：分析脚本

放可重复运行的分析与数据处理脚本。约定：

- 默认从仓库根目录运行，输入输出路径写成参数或环境变量，不写死个人机器路径。
- 下载类脚本只把文件写入 `data/<数据集>/raw/`，并打印 SHA256，方便登记到对应的数据集 README。
- 结论性的输出（数字、表格）同步记录到 [docs/findings.md](../docs/findings.md)，并注明是哪个脚本、哪天生成的。
- 在 Vulcan 集群上，重计算必须通过 Slurm 提交，不能在登录节点上跑。

## 脚本清单

| 脚本 | 作用 | 资源 |
|---|---|---|
| [audit_lincs_metadata.sh](audit_lincs_metadata.sh) | 统计 LINCS 两个阶段中，某细胞系（默认 HEPG2）的化合物签名按时间和剂量的分布，以及哪些细胞系有 CRISPR 敲除数据 | 下载约 13 MB 元数据；只用 curl、awk，几秒钟即可跑完 |
| [lincs_cell_line_coverage.sh](lincs_cell_line_coverage.sh) | 给定一组细胞系，统计各自在 LINCS 中的化合物、CRISPR、shRNA 签名数；默认查 ProteinTalks 论文中出现的细胞系 | 复用上一个脚本缓存的元数据，不下载 |
| [collect_literature.py](collect_literature.py) | 按脚本内的 DOI 列表下载论文 PDF 到 `pdf/`，用 pypdf 校验文件确实是 PDF，并记录来源和 SHA256（`pdf/download_manifest.json`） | 需要联网和 `pypdf`；缓存写在 `tmp/literature/` |
| [retry_literature.py](retry_literature.py) | 对上一步没下载成功的论文，换作者主页或出版社链接重试，不覆盖已有 PDF | 同上 |
| [build_literature_docs.py](build_literature_docs.py) | 根据整理好的笔记（`docs/literature_notes.json`）和下载清单，生成 `docs/literature/` 下的阅读索引和逐篇介绍 | 只读本地文件 |

用法：

```bash
bash script/audit_lincs_metadata.sh              # HEPG2
CELL=A375 bash script/audit_lincs_metadata.sh    # 其他细胞系
bash script/lincs_cell_line_coverage.sh A375 MCF7  # 先跑上一行缓存元数据

# 文献脚本：在自己电脑或 Colab 上运行（需要 Python 和 pypdf），不要在集群登录节点上跑
python script/collect_literature.py
python script/retry_literature.py
python script/build_literature_docs.py
```

PTDS 与 LINCS、Tahoe‑100M 的药物对齐目前写在 `colab/` 的 notebook 里，结果放在 [reports/](../reports/README.md)。
