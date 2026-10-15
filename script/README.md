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

用法：

```bash
bash script/audit_lincs_metadata.sh              # HEPG2
CELL=A375 bash script/audit_lincs_metadata.sh    # 其他细胞系
bash script/lincs_cell_line_coverage.sh A375 MCF7  # 先跑上一行缓存元数据
```
