# 虚拟细胞与扰动响应预测：Overleaf 扩展版

本版日期：2026-10-16。18 页主讲 + 7 页附录，共 25 页。保留原项目的 SimplePlus 深蓝主题、16:9 版式、中文字体和杭州电子科技大学校徽。

## 查看与编辑

- `main.pdf`：扩展后的完整幻灯片。
- `main.tex`：主文件；页面顺序、日期与正文页数在此设置。
- `pages/22-*.tex` 至 `pages/29-*.tex`：新增 8 页正文。
- `pages/30-references-5.tex`：新增 1 页参考文献。
- `speaker-notes.md`：与本版页码一致的讲述提示；原稿讲稿保存在 `speaker-notes-original.md`。
- `research/data-audit.md`：逐篇数据、版本与疑点核查；`selected-sources.json` 增加 [22–25]。

## 上传 Overleaf

上传本目录的源码文件，主文件选 `main.tex`，编译器选 **XeLaTeX**。必须保留 `pages/`、`theme/`、`assets/`。使用完整项目 ZIP 上传时，压缩包根目录就是本工程。

## 本地编译

安装 XeLaTeX、Beamer、ctex、fontawesome5 和 Fandol 后，在本目录运行：

```powershell
./scripts/build.ps1
```

已有 Linux 构建脚本保留在 `scripts/build.sh`，其 TeX Live 2021 回退逻辑来自原稿。本次本地构建使用便携式 Tectonic；它不是项目运行或 Overleaf 的依赖，不需要随源码上传。

## 与原稿的关系

原目录有 21 页的旧 PDF，但此次读取到的 `main.tex` 仅启用 10 页主讲 + 6 页附录。本版以源文件为准，未自动重新启用未引用的旧页面；再加入 8 页正文与 1 页参考文献。封面日期与正文页脚同步更新。

三篇核心论文采用用户提供的正式版 PDF，CPT 采用 2026-08-19 v1 预印本。研究建议明确标为假设，未展示本人复现结果。实验数据大小是论文报告的样本/特征口径，不是下载文件 TB 数或本项目已获取数据量。
