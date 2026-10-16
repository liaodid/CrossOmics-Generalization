# output/：汇报材料

存放给导师或组会看的成品：幻灯片、文献综述、报告等。

## 约定

- 每份材料一个目录，命名为 `<名称>-<日期>/`，目录里要有 README，写清怎么编译或查看。
- 提交源文件和编译好的 PDF；LaTeX 编译中间文件已在根目录 `.gitignore` 中忽略。
- 材料中引用的结论和数字，应能在 [docs/findings.md](../docs/findings.md) 或 [reports/](../reports/README.md) 中找到出处。

## 清单

| 目录 | 内容 | 查看方式 |
|---|---|---|
| [overleaf-expanded-2026-10-16/](overleaf-expanded-2026-10-16/README.md) | “虚拟细胞与扰动响应预测”幻灯片：18 页正文 + 7 页附录（Beamer，杭电模板），附文献综述、arXiv 2026 检索结果和数据核查记录 | 直接看 `main.pdf`；修改时上传到 Overleaf，用 XeLaTeX 编译 `main.tex` |
