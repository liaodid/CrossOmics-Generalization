# 协作约定

本文适用于整个仓库，原为 `baseline/unipert-g2cp/README.md` 第 8 节，重构时移至此处。

## 1. 分支与 Pull Request

- `main`：保留经过检查的代码和文档。
- `docs/...`：文档更新。
- `fix/...`：运行问题修复。
- `exp/...`：实验改动。
- `refactor/...`：目录结构或代码组织调整，不改变实验行为。
- `upstream/...`：引入或更新他人（原作者）的代码，例如补充 UniPert‑G2CP 作者的分析源码。

示例：

```bash
git switch -c exp/a549-baseline

# 修改并验证后，按实际文件选择提交
git add baseline/unipert-g2cp/README.md
git commit -m "docs: update baseline instructions"
git push -u origin exp/a549-baseline
```

在自己的协作仓库中提交 Pull Request。
PR 说明应包含修改目的、验证方式和受影响的实验。

## 2. 建议分工

| 工作 | 交付物 |
|---|---|
| 环境与路径修正 | 可复现环境文件、运行说明 |
| 数据准备 | 数据清单、校验值、划分说明（写入对应的 `data/<数据集>/README.md`） |
| 原论文实验 | 命令、日志、指标与论文对应关系 |
| 新方法比较 | 统一评估协议和结果表 |

在 Issues 中记录待办、运行错误和复现差异，
避免仅依赖聊天记录传递实验设置。
重要结论和已核实的事实同步写入 [findings.md](findings.md)。

## 3. GitHub 中保存什么

提交代码、配置、说明文档和小型结果汇总。
大型数据、模型权重、缓存和训练日志通过作者数据入口
或团队共享存储管理，并在文档中记录位置。

`.gitignore` 的规则：

- 任意层级 `data/` 目录下只跟踪 `README.md`，数据文件本身不进 Git。
- `*.h5ad`、`*.pkl`、`*.pt` 等数据与权重格式全局忽略。
- `saved_models/`、`results/`、`logs/`、`wandb/` 忽略。
- 根目录 `pdf/` 下的论文 PDF 不提交（版权和体积原因）；下载清单 `pdf/download_manifest.json` 和手动下载入口会提交。早期约定的 `docs/papers/` 已不再使用，同样不提交。

被忽略的文件不会随普通 Git 克隆自动下载，
新成员需按各 `data/<数据集>/README.md` 的说明自行获取。

## 4. 新增内容放在哪里

| 内容 | 位置 | 命名 |
|---|---|---|
| 新的对比方法（他人论文代码） | `baseline/<方法名>/` | 小写短横线，如 `baseline/proteintalks/` |
| UniPert‑G2CP 作者的补充源码 | 按 [baseline/unipert-g2cp/README.md 第 11 节](../baseline/unipert-g2cp/README.md#11-补充原作者源码放在哪里) 的对照表放置，并在 `baseline/unipert-g2cp/extra/README.md` 登记来源 | 保持作者原始文件名 |
| 数据集 | `data/<数据集名>/`，附 `README.md` | `<来源或内容>-<编号>`，如 `data/hepg2-drug-proteome-msv000101671/` |
| 可复用的分析脚本 | `script/` | 动词开头，如 `audit_lincs_metadata.sh` |
| 探索性 / Colab notebook | `colab/` | 内容描述，如 `hepg2_alignment_drive.ipynb` |
| 项目文档 | `docs/` | — |
| 论文 | PDF 放根目录 `pdf/`（不提交）；在 [papers.csv](papers.csv) 加一行，`pdf_file` 填 PDF 文件名、`pdf_version` 写清是预印本还是正式版；逐篇介绍放 `docs/literature/<key>.md` | `key` 用小写短横线，PDF 命名为 `<key>.pdf`，如 `proteintalks.pdf` |
| 某篇论文所用数据的说明 | `data/<方法名>/README.md`，并在 `data/README.md` 的“论文与数据文档对应表”登记 | 与 `papers.csv` 的 `key` 一致，如 `data/gears/` |
| 分析结果（小型 CSV/JSON/图） | `reports/<分析名>-<日期>/`，附 `summary.json` 或 README，见 [reports/README.md](../reports/README.md) | 如 `reports/ptds-unipert-2026-10-16/` |
| 汇报材料（幻灯片、综述） | `output/<名称>-<日期>/`，附 README，见 [output/README.md](../output/README.md) | 如 `output/overleaf-expanded-2026-10-16/` |

上游代码放入 `baseline/` 后保持原样；必须修改时单独提交，并在该 baseline 的 README 中记录改动。
