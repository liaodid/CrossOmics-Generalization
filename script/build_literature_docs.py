"""Build the reviewed literature index from curated notes and verified downloads."""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/literature'
CACHE=ROOT/'tmp/literature'
DATE='2026-10-15'
VERSIONS={
 'proteintalks':('bioRxiv 2025 v1；不是 Nature 2026 正式版','10.1101/2025.02.07.637070','A perturbation proteomics-based foundation model for virtual cell construction'),
 'unipert-g2cp':('bioRxiv 2025 v2；不是 Cell 2026 正式版','10.1101/2025.02.02.635055','Genetic-to-Chemical Perturbation Transfer Learning Through Unified Multimodal Molecular Representations'),
 'state':('bioRxiv 2025 v1；不是 Cell 2026 正式版','10.1101/2025.06.26.661135','Predicting cellular responses to perturbation across diverse contexts with State'),
 'tahoe-100m':('bioRxiv 2025 v2；不是 Cell 2026 正式版','10.1101/2025.02.20.639398','Tahoe-100M: A Giga-Scale Single-Cell Perturbation Atlas for Context-Dependent Gene Function and Cellular Modeling'),
 'robotic-proteomics':('bioRxiv 2026 v1，预印本','10.64898/2026.05.04.722718','Robotic perturbation proteomics and AI agents enable scalable drug mechanism discovery'),
 'totalvi':('作者接受稿，由 UC eScholarship 存储；对应 Nature Methods 2021 正式论文','10.1038/s41592-020-01050-x','Joint probabilistic modeling of single-cell multi-omic data with totalVI'),
 'chemcpa':('NeurIPS 2022 会议论文','10.52202/068431-1937','Predicting Cellular Responses to Novel Drug Perturbations at a Single-Cell Resolution'),
}

def main():
    notes=json.loads((ROOT/'docs/literature_notes.json').read_text(encoding='utf-8'))
    OUT.mkdir(exist_ok=True)
    manifest=[]
    summaries=[]
    for rank,(key,n) in enumerate(notes.items(),1):
        raw=json.loads((CACHE/(key+'.json')).read_text(encoding='utf-8'))
        meta=raw.get('crossref',{})
        title=meta.get('title',[VERSIONS.get(key,('','',''))[2]])[0]
        doi=raw.get('doi') or VERSIONS.get(key,('','',''))[1]
        venue=(meta.get('container-title') or ['bioRxiv' if key=='robotic-proteomics' else 'NeurIPS'])[0]
        year=meta.get('issued',{}).get('date-parts',[[2022]])[0][0]
        authors='; '.join((a.get('given','')+' '+a.get('family','')).strip() for a in meta.get('author',[])[:6])
        if not authors and key=='chemcpa': authors='Leon Hetzel; Simon Böhm; Niki Kilbertus; Stephan Günnemann; Mohammad Lotfollahi; Fabian Theis'
        if len(meta.get('author',[]))>6: authors+='; et al.'
        paper_url='https://doi.org/'+doi
        path=ROOT/'pdf'/f'{key}.pdf'
        ok=path.exists() and raw.get('pdf_status')=='downloaded'
        version,pdf_doi,pdf_title=VERSIONS.get(key,('出版社论文版本',doi,title))
        status='已下载' if ok else '需手动下载'
        local=f'[本地 PDF](../../pdf/{key}.pdf)' if ok else f'[出版社入口]({paper_url})（自动获取未成功）'
        evidence='已提取本地 PDF 正文并核对首页；结合下列原始来源整理。' if ok else '未取得可验证的本地 PDF；本介绍依据出版社/PMC HTML 正文与作者仓库，属于初步阅读笔记。'
        if ok and key in ['proteintalks','unipert-g2cp','state','tahoe-100m']:
            evidence+=' 本地 PDF 为早期预印本，正式版的补充结论仅来自明确列出的正式版页面或既有项目记录；不能将两个版本的数字混用。'
        text=f'# {n["name"]}：{n["role"]}\n\n> 整理日期：{DATE}。阅读优先级：**{n["priority"]}**。PDF：**{status}**。\n> 核验范围：{evidence}\n\n## 论文与代码\n\n- **正式引用 / 目标论文：** {authors}. **{title}.** {venue}, {year}.\n- DOI：[{doi}]({paper_url})\n- 本地文件：{local}\n'
        if ok:
            text+=f'- **实际下载版本：** {version}。\n- 下载稿标题：{pdf_title}。\n- 下载稿 DOI：[{pdf_doi}](https://doi.org/{pdf_doi})。\n- 篇幅：{raw["pages"]} 页；文件完整性 SHA-256 见 [下载清单](../../pdf/download_manifest.json)。\n'
        text+=f'- 代码：{n["code"] or "未在本次核验中单独确认；以论文 Code availability 为准。"}\n- 数据：{n["data"]}\n\n## 为什么值得优先阅读\n\n{n["reason"]}\n\n## 方法概要\n\n{n["method"]}\n\n| 模块 | 输入 | 输出 / 作用 |\n|---|---|---|\n'
        text+=''.join('| '+' | '.join(row)+' |\n' for row in n['io'])
        text+=f'\n## 论文中的评价设置与结果解读\n\n{n["evaluation"]}\n\n以上是原文设定的归纳，不是本仓库复现实验结果。本次不抄录缺乏同版本表图核验的精确性能数字。\n\n## 与本项目的关系\n\n**以下为针对本项目的分析与建议：** {n["relation"]}\n\n## 局限与对比时需要注意的条件\n\n{n["limits"]}\n\n## 复现与接入建议\n\n{n["next"]}\n\n- [x] 核对论文身份和项目相关性。\n- [{"x" if ok else " "}] 获取并验证本地 PDF。\n- [ ] 在本项目数据上复现；本次未安装或运行该方法。\n- [ ] 统一测试药物、蛋白集合、训练预算和评价指标。\n\n## 原始来源与建议阅读位置\n\n'
        text+=''.join(f'- [{u}]({u})\n' for u in dict.fromkeys([paper_url]+n['sources']))
        if ok: text+=f'- 实际 PDF 来源：[下载地址]({raw["pdf_url"].split("?error=")[0]})。\n'
        text+='- 建议先读：Abstract / Summary、方法总图、数据划分与评价、Data availability；再结合上述复现建议阅读 Methods。\n'
        (OUT/f'{key}.md').write_text(text,encoding='utf-8')
        rec=dict(key=key,method=n['name'],priority=n['priority'],title=title,authors=authors,year=year,venue=venue,doi=doi,paper_url=paper_url,project_role=n['role'],code=n['code'],data=n['data'],review_path=f'docs/literature/{key}.md',pdf_path=f'pdf/{key}.pdf' if ok else '',pdf_status=status,pdf_version=version if ok else '',downloaded_doi=pdf_doi if ok else '',downloaded_title=pdf_title if ok else '',checked_date=DATE)
        if ok:
            assert hashlib.sha256(path.read_bytes()).hexdigest()==raw['sha256']
            rec.update(pdf_url=raw['pdf_url'].split('?error=')[0],pages=raw['pages'],bytes=raw['bytes'],sha256=raw['sha256'])
        else: rec['attempts']=raw.get('attempts',[])
        manifest.append(rec)
        summaries.append(f'| {rank} | {n["priority"]} | [{n["name"]}]({key}.md) | {n["role"]} | {status} | {version if ok else "待手动获取"} |')
    with (ROOT/'docs/literature.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=[k for k in manifest[0] if k not in ('attempts',)]
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore')
        writer.writeheader(); writer.writerows(manifest)
    (ROOT/'pdf/download_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    catalogue=ROOT/'docs/papers.csv'
    with catalogue.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        catalogue_fields=list(dict.fromkeys(reader.fieldnames+['review_path','pdf_dir','pdf_status','pdf_version']))
        existing=list(reader)
    by_doi={r['doi'].lower():r for r in existing}
    for rec in manifest:
        row=by_doi.get(rec['doi'].lower())
        if row is None:
            row={k:'' for k in catalogue_fields}
            row.update({k:rec[k] for k in ('key','title','authors','year','venue','doi','project_role','code','data')})
            row['method']=rec['method']
            existing.append(row)
        row.update(pdf_file=Path(rec['pdf_path']).name if rec['pdf_path'] else '',review_path=rec['review_path'],pdf_dir='pdf',pdf_status=rec['pdf_status'],pdf_version=rec['pdf_version'])
    with catalogue.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=catalogue_fields)
        writer.writeheader(); writer.writerows(existing)
    count=sum(bool(r['pdf_path']) for r in manifest)
    readme=f'''# 与 CrossOmics-Generalization 最相关的 18 篇论文

检索与整理日期：{DATE}。已验证下载 **{count}/18 篇 PDF**；每篇均有单独中文介绍，未下载条目也提供初步解读及手动入口。

## 选文依据

项目目标是用转录组与蛋白组扰动数据联合训练，改善蛋白组响应泛化。先选择直接跨组学先例与 ProteinTalks/UniPert-G2CP，再补充药物泛化、公开蛋白/RNA 数据和评价方法；不是按引用量排列。

P0：先读，影响创新性与主实验；P1：建模、数据或评估的重要参考；P2：方法基础。列表已包括仓库原先登记的核心文献，而非声称 18 篇都是新发现。

远端 GitHub 连接器与匿名原始文件入口返回 404；通过已配置 Git 凭据查询到远端 HEAD 为 `6464fb0aac7084a5df2ff01e4709b3430c00d772`，与读取时的本地 HEAD 一致。项目判断依据该版本本地 README、findings、数据文档和 ProteinTalks baseline。没有把远端读取失败写成已成功读取网页。

## 阅读索引

| 顺序 | 优先级 | 方法 / 论文介绍 | 本项目中的角色 | PDF | 实际保存版本 |
|---|---|---|---|---|---|
'''+ '\n'.join(summaries)+'''

## 对论文定位的直接影响

1. **TransPro 已涉及从转录组到药物诱导蛋白组及表型的建模**；[作者仓库](https://github.com/XieResearchGroup/TransPro)提供含扰动 RNA 辅助数据的训练设置。不能笼统声称首次联合 RNA 与蛋白预测药物响应。
2. **MultiPert 已联合预测 RNA 与蛋白扰动响应**，但主要蛋白读出是 ADT 表面蛋白，且与本项目的小分子质谱场景不同。参见[原论文](https://doi.org/10.1371/journal.pcbi.1014054)。
3. **ProteinTalks 正式版还探索了由蛋白预训练迁移至 PDX 转录组**，见[正式版扩展数据图 8](https://www.nature.com/articles/s41586-026-11001-9)。主训练数据以蛋白为主，与“完全没有跨组学探索”不是同一断言。
4. 更合适的候选研究问题是：**非严格配对的大规模 RNA 辅助监督，是否在同样的蛋白数据和预算下，提高质谱蛋白组对未见药物、未见骨架或新细胞背景的泛化？** 这是本次检索后的建议，尚待数据和实验证明，也不构成穷尽性新颖性检索结论。

## 建议的最小对比

| 比较 | 要回答的问题 |
|---|---|
| 对照不变、训练平均变化、结构特征岭回归 | 是否优于简单强基线？ |
| 同架构蛋白组单任务 | RNA 辅助数据是否有增益？ |
| RNA 预训练后蛋白微调 | 同步联合训练是否必要？ |
| RNA/蛋白联合训练 | 主设想是否成立？ |
| TransPro、ProteinTalks 及适配后的 MultiPert | 相比已有直接先例有何改进？ |

按药物及结构骨架隔离重复；细胞背景泛化单列；报告 Δ 蛋白相关性、MSE、方向与差异蛋白恢复。药效分类另报 AUROC/AUPRC，不能与表达重建混成一个结论。用于验证的特征集合与预处理不能由测试标签决定。

RNA 中若出现蛋白测试药物，应明确称为跨模态标签迁移设置；若声称全新药物外推，则应从各组学训练数据中隔离这些药物。非配对的双 head 在工程上能训练，但是否能有效迁移取决于共同扰动、细胞背景、先验或桥接样本，不能保证可辨识性。

## 文件与版本说明

- PDF 在根目录 `pdf/`，与用户指定一致；中文介绍在 `docs/literature/`，仿照 ProteinTalks baseline 的结构，而不是把所有相关工作都当成已经安装的 baseline。
- [18 篇详细表格](../literature.csv)包括版本、DOI、介绍路径及下载状态；[下载清单](../../pdf/download_manifest.json)包含页数、大小、SHA-256 和来源。
- [手动下载清单](../../pdf/MANUAL_DOWNLOADS.md)包含尚缺 PDF 和仅获取预印本的正式版。
- 成功仅表示文件以 PDF 魔数开头、可解析页数与正文且人工核对了首页论文身份，不代表完成全文精读或模型复现。
- 不覆盖既有 baseline，不提交或推送 Git；PDF 被 `.gitignore` 排除。
'''
    (OUT/'README.md').write_text(readme,encoding='utf-8')
    missing='# 需要手动补充的 PDF\n\n整理日期：'+DATE+'。下载完成后请按下列文件名放入本目录；现有介绍可继续使用。\n\n## 未获取到正文 PDF\n\n'
    for r in manifest:
        if not r['pdf_path']:
            missing+=f'- **{r["method"]}**：{r["title"]}。\n  - [出版社 / DOI]({r["paper_url"]})；保存为 `{r["key"]}.pdf`。\n  - [中文介绍](../{r["review_path"]})。\n  - 原因：公开自动下载入口返回访问限制、HTML 验证页或连接失败；不表示论文没有开放版本。\n'
    missing+='\n## 已有预印本，仍建议补充正式版\n\n'
    for r in manifest:
        if r['key'] in ('proteintalks','unipert-g2cp','state','tahoe-100m'):
            missing+=f'- **{r["method"]}**：[正式版]({r["paper_url"]})。已有 `{r["key"]}.pdf` 为 {r["pdf_version"]}；正式版建议保存为 `{r["key"]}-published.pdf`，保留版本区分。\n'
    missing+='\n## 补充后如何同步\n\n本次清单反映实际检查时状态。手动放入文件后，需同步修改清单和介绍中的版本状态；不要把新文件自动当成已核验。本次未调用学校订阅或登录个人账号。\n'
    (ROOT/'pdf/MANUAL_DOWNLOADS.md').write_text(missing,encoding='utf-8')
    (ROOT/'pdf/README.md').write_text(f'# 项目论文 PDF\n\n已验证下载 {count}/18 篇。请从[18 篇阅读索引](../docs/literature/README.md)开始；每篇 PDF 都有中文介绍。\n\n- [未获取 PDF 与正式版补充入口](MANUAL_DOWNLOADS.md)\n- [文件来源、版本和 SHA-256](download_manifest.json)\n\nPDF 仅保留在本地，不随 Git 提交。ProteinTalks、UniPert-G2CP、State、Tahoe-100M 当前为作者预印本；totalVI 为作者接受稿，详见清单。\n',encoding='utf-8')
    print(f'Built {len(manifest)} reviews; {count} verified PDFs.')

if __name__=='__main__': main()
