# GitHub 同步与换电脑迁移：2026-11-06

## GitHub 保存什么

提交项目脚本与测试、研究和运行说明、环境候选清单、小型结果摘要。当前更新也包含此前尚未进入 main 的 ProteinTalks 上游代码。数据、权重、完整日志、论文、汇报及临时分析文件通过压缩包迁移。

`outputs/` 整体忽略；其中适合公开的小型摘要已复制到 `reports/proteintalks-2026-11-06/`。根目录两份误生成的 Git 文本输出、嵌套 `script/script/` 也被忽略，原文件仍保留在迁移快照。

## 迁移文件

包和校验清单位于仓库根目录 `transfer-2026-11-06/`：

- `CrossOmics-Generalization.zip`：仓库文件快照，包含 Git 跟踪文件和未提交/被忽略的研究文件，包括 `data/`、`results/`、`baseline/` 的原始表格、`pdf/`、`outputs/`、`output/` 和 `tmp/`。保留临时研究数据，避免遗漏。
- `杭医所项目.zip`：该目录文件快照，包括 `dataset/c39.h5ad`、文献、Colab、Overleaf 源码及汇报。
- `SHA256SUMS.txt`：两个 ZIP 的 SHA256。
- `*.manifest.csv`：逐文件路径、字节数与 SHA256，ZIP 内也有一份。
- `transfer_summary.json`：文件数、体积、排除目录及验证状态。

仅排除 `.git/`、Python 字节码与 `__pycache__/`、符号链接以及迁移输出目录本身。Git 历史和本地认证不随 ZIP 迁移，在新电脑通过 GitHub clone 重建仓库。ZIP 带顶层目录，支持 ZIP64。若遇超长路径，解压到短目录，例如 `D:\research`。

## 新电脑恢复步骤

1. 传输整个 `transfer-2026-11-06/` 文件夹。
2. 在该文件夹运行 `Get-FileHash -Algorithm SHA256 -LiteralPath .\CrossOmics-Generalization.zip, .\杭医所项目.zip`，与 `SHA256SUMS.txt` 对比。
3. 克隆本次进度分支（本机迁移目录的 `恢复说明.md` 记录实际分支和提交），将 `CrossOmics-Generalization.zip` 解压到克隆目录的父目录，合并到同名仓库目录。ZIP 也包含代码快照，合并时应克隆同一次提交，避免覆盖之后的改动。
4. 将 `杭医所项目.zip` 解压到所需位置，保留相对目录结构。
5. 重新创建 Python/Conda 环境，参考 `env/requirements-proteintalks-5090.txt` 与成功运行目录的 `environment_freeze.txt`。候选清单不是完整环境锁，GPU、CUDA、Python 版本需在目标机验证；本次未打包 Conda 环境和驱动。
6. 在仓库根目录运行以下检查，不启动 GPU 训练：

```powershell
python -m unittest discover -s script -p "test_proteintalks*.py" -v
python script/run_proteintalks_remaining.py --batch_size 64 --dry_run
```

历史 JSON 和命令可能保留 `E:\liaodi\...` 等原机绝对路径。保留其历史记录，新实验及独立 evaluator 根据 `--help` 指定目标机实际目录。不要直接重复已完成的全部 15 折。

## 后续同步

从最新 main 建工作分支，按实际文件逐项 `git add`，用 `git diff --cached --stat` 和 `git diff --cached` 检查，再 commit、push，通过 Pull Request 合入 main。不要用 `git add -f` 上传被忽略数据。

具体提交和 GitHub 地址见本机迁移目录 `恢复说明.md`。压缩包覆盖本机这两个目录；未下载到本机的 Google Drive、服务器、其他电脑数据，以及在线 Overleaf 的更新不在此次快照中。
