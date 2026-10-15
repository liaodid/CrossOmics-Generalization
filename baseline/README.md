# baseline/：对比方法

每个子目录放一个已发表方法的代码和复现说明，作为本项目新方法的对比对象。

| 目录 | 方法 | 预测什么 | 组学 | 代码状态 | 在项目中的角色 |
|---|---|---|---|---|---|
| [unipert-g2cp](unipert-g2cp/README.md) | UniPert‑G2CP（Cell 2026，腾讯 / 中南大学） | 扰动后的转录组（L1000）或细胞形态特征 | 转录组 | ✅ 上游代码已入库，未运行 | 转录组侧参考方法；其 UniPert 扰动表示可复用 |
| [proteintalks](proteintalks/README.md) | ProteinTalks（Nature 2026，西湖大学） | 扰动后的蛋白组时间轨迹，以及药效和协同 | 蛋白组 | 🔓 代码已公开（`guomics-lab/PTV-1`），尚未放入本仓库；训练数据未拿到 | **主要对标对象**（已确认） |

## 约定

- 上游代码保持原样放入，并在该目录的 `docs/upstream_commit.txt` 中记录来源提交。
- 为跑通而做的修改（路径、依赖等）单独提交，并在该 baseline 的 README 中列出。
- 每个 baseline 的 README 至少写清：任务定义、输入、输出、数据、评价指标、复现步骤、复现进度。
- 与本项目方法比较时，必须使用统一的数据划分和指标，见 [docs/findings.md](../docs/findings.md) 的“待定事项”。
