#!/usr/bin/env python3
"""Build the figures and tables for the 2026-10-16 weekly report.

Every number is computed from files already in this repo (or cached by
script/audit_lincs_metadata.sh), or is copied from a paper and marked as such
in the FACTS block below.

Inputs
  data/lincs-l1000/raw/metadata/GSE92742_Broad_LINCS_sig_info.txt.gz      (run audit_lincs_metadata.sh first)
  data/lincs-l1000/raw/metadata/GSE70138_Broad_LINCS_sig_info_2017-03-06.txt.gz
  reports/ptds-unipert-2026-10-16/*.csv                                     (PTDS x LINCS MCF7 alignment)
  docs/literature.csv

Outputs (default reports/weekly-2026-10-16/)
  figures/*.png   one PNG per figure, sized for a 16:9 Beamer slide
  tables/*.csv    the data behind each figure
  summary.json    headline numbers quoted in the slides and docs/findings.md

Usage (from the repo root; on Vulcan run it inside a Slurm job, not on the login node)
  python script/make_weekly_figures.py [--out reports/weekly-2026-10-16]
"""
import argparse
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
LINCS_DIR = ROOT / "data/lincs-l1000/raw/metadata"
ALIGN_DIR = ROOT / "reports/ptds-unipert-2026-10-16"

# ---- palette: dataviz reference categorical slots 1-3 (validated all-pairs, light) + deck ink ----
RNA, PROT, BOTH = "#2a78d6", "#eb6834", "#1baf7a"   # transcriptome / proteome / both
INK, MUTED, GRID, AXIS = "#24292F", "#626B76", "#e6e6e3", "#bdbcb6"
SEQ = {"none": "#f1f1ef", "weak": "#9ec5f4", "strong": "#2a78d6"}  # blue ramp steps 200 / 450
ORDINAL = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab"]           # blue ramp 250 / 350 / 450 / 550

# ---- facts copied from papers / dataset docs (not computed here) ----
FACTS = {
    # cell lines, compounds (single agents) -- see data/*/README.md
    "landscape": [
        # label, omics, n_cell_lines, n_compounds, source note
        ("Tahoe-100M", "RNA", 50, 380, "State 正式版口径：380 种药物"),
        ("PTDS", "PROT", 18, 63, "ProteinTalks：63 种单药（另有 59 种组合）"),
        ("mtPTDS", "PROT", 3, 55, "ProteinTalks：55 种单药，11 个时间点"),
        ("PTPC", "PROT", 5, 708, "ProteinTalks：708 种化合物"),
        ("HepG2 蛋白组\n(MSV000101671)", "PROT", 1, 172, "Jiang et al. 2026：172 种化合物"),
        ("HepG2 蛋白组\n(Basu 2026)", "PROT", 1, 282, "Basu et al. 2026：78 种 FDA 药 + 204 个降解剂"),
        ("GSE51952", "RNA", 1, 22, "HepG2 芯片：22 种药"),
    ],
    # PTPC few-shot drug-response benchmark, ProteinTalks paper (Nature 2026) main text
    "ptpc_benchmark": [
        ("ProteinTalks", "PROT", 0.41, 0.77),
        ("GeneCompass", "RNA", 0.28, 0.72),
        ("Geneformer", "RNA", 0.23, 0.56),
        ("UCE", "RNA", 0.19, 0.54),
    ],
    # HepG2 pairing attempt (colab/hepg2_alignment_drive.ipynb outputs; LINCS audit)
    "hepg2": {
        "proteome_drugs": 170,
        "gse51952_drugs": 22,
        "gse51952_name_overlap": 1,
        "gse51952_same_dose": 0,
        "lincs_p1_24h_10uM_compounds": 176,
        "lincs_p1_name_overlap": 0,
        "lincs_p2_24h_10uM_compounds": 268,
    },
    # cell-line membership beyond LINCS: 2 = confirmed, 1 = mentioned / candidate only
    "membership": {
        "PTDS": {"MCF7": 2, "BT549": 2, "HCC1806": 2, "HS578T": 2, "MDA-MB-468": 2,
                 "BT20": 1, "MDA-MB-231": 1, "HCC1143": 1, "MDA-MB-453": 1},
        "mtPTDS": {"HCC1806": 2, "HCC1143": 2, "MDA-MB-453": 2},
        "PTPC": {"A375": 2, "HCT116": 2, "NCI-H1975": 2, "NCI-H2170": 2, "Panc 10.05": 2},
        "Tahoe-100M": {"HepG2": 1, "BT20": 1, "HCC1143": 1, "HS578T": 1, "MCF7": 1},
        "HepG2 蛋白组": {"HepG2": 2},
    },
}
CELL_ROWS = ["MCF7", "A375", "HepG2", "HCT116", "BT20", "HS578T", "MDA-MB-231", "BT549",
             "MDA-MB-468", "HCC1806", "HCC1143", "MDA-MB-453", "NCI-H1975", "NCI-H2170", "Panc 10.05"]

TISSUE = {"MCF7": "乳腺癌", "A375": "黑色素瘤", "HepG2": "肝癌", "HCT116": "结直肠癌",
          "NCI-H1975": "肺癌", "NCI-H2170": "肺癌", "Panc 10.05": "胰腺癌"}


def cell_label(cell):
    """Cell line name plus tumour type, for a clinical audience."""
    return f"{cell} · {TISSUE.get(cell, '乳腺癌')}"


LIT_ROWS = ["跨组学先例", "扰动预测模型", "数据资源", "评价方法"]
LIT_ROLE = {
    "transpro": ("跨组学先例", "BOTH"), "multipert": ("跨组学先例", "BOTH"),
    "totalvi": ("跨组学先例", "BOTH"), "multivi": ("跨组学先例", "RNA"),
    "proteintalks": ("扰动预测模型", "PROT"), "unipert-g2cp": ("扰动预测模型", "RNA"),
    "state": ("扰动预测模型", "RNA"), "xpert": ("扰动预测模型", "RNA"),
    "perturbnet": ("扰动预测模型", "RNA"), "chemcpa": ("扰动预测模型", "RNA"),
    "cpa": ("扰动预测模型", "RNA"), "gears": ("扰动预测模型", "RNA"),
    "biolord": ("扰动预测模型", "RNA"),
    "tahoe-100m": ("数据资源", "RNA"), "l1000": ("数据资源", "RNA"),
    "robotic-proteomics": ("数据资源", "PROT"), "degrader-proteomics": ("数据资源", "PROT"),
    "linear-baselines": ("评价方法", "RNA"),
}
SHORT = {"robotic-proteomics": "HepG2 机器人蛋白组", "degrader-proteomics": "降解剂蛋白组",
         "linear-baselines": "线性基线评测", "l1000": "L1000/CMap"}
OMICS_COLOR = {"RNA": RNA, "PROT": PROT, "BOTH": BOTH}
OMICS_LABEL = {"RNA": "转录组", "PROT": "蛋白组", "BOTH": "转录组 + 蛋白组"}


def setup_style():
    for fname in ("NotoSansCJKsc-Regular.otf", "NotoSansCJKsc-Bold.otf"):
        for base in (Path.home() / ".local/share/fonts/noto-cjk", Path("/usr/share/fonts")):
            p = base / fname
            if p.exists():
                font_manager.fontManager.addfont(str(p))
    plt.rcParams.update({
        "font.family": ["Noto Sans CJK SC", "DejaVu Sans"], "font.size": 7.5, "axes.unicode_minus": False,
        "text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": INK,
        "axes.edgecolor": AXIS, "axes.linewidth": 0.6, "axes.grid": False,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5,
        "ytick.major.size": 0, "figure.dpi": 100, "savefig.dpi": 300,
        "savefig.facecolor": "white", "figure.facecolor": "white", "axes.facecolor": "white",
        "legend.frameon": False, "legend.fontsize": 7,
    })


def clean_axes(ax, grid_axis="x"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)


def plain_log(ax, axis="x"):
    """Show log-axis ticks as plain numbers (1, 10, 100, 1,000) instead of 10^k."""
    fmt = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}" if v >= 1 else "")
    target = ax.xaxis if axis == "x" else ax.yaxis
    target.set_major_locator(matplotlib.ticker.LogLocator(base=10, numticks=5))
    target.set_major_formatter(fmt)
    target.set_minor_formatter(matplotlib.ticker.NullFormatter())
    target.set_minor_locator(matplotlib.ticker.NullLocator())


def save(fig, out, name):
    fig.savefig(out / "figures" / f"{name}.png", bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def norm_cell(name):
    c = re.sub(r"\.\d+$", "", str(name).upper())
    c = re.sub(r"[- .]", "", c)
    return re.sub(r"^NCI", "", c)


# ---------------------------------------------------------------- LINCS
def load_lincs():
    p1 = LINCS_DIR / "GSE92742_Broad_LINCS_sig_info.txt.gz"
    p2 = LINCS_DIR / "GSE70138_Broad_LINCS_sig_info_2017-03-06.txt.gz"
    for p in (p1, p2):
        if not p.exists():
            raise SystemExit(f"missing {p}; run script/audit_lincs_metadata.sh first")
    cols = ["sig_id", "pert_id", "pert_type", "cell_id"]
    a = pd.read_csv(p1, sep="\t", usecols=cols, low_memory=False).assign(phase="GSE92742")
    b = pd.read_csv(p2, sep="\t", usecols=cols, low_memory=False).assign(phase="GSE70138")
    d = pd.concat([a, b], ignore_index=True)
    d["cell"] = d["cell_id"].map(norm_cell)
    return d


def lincs_counts(lincs):
    want = {norm_cell(c): c for c in CELL_ROWS}
    sub = lincs[lincs.cell.isin(want) & lincs.pert_type.isin(["trt_cp", "trt_xpr", "trt_sh"])]
    t = sub.groupby(["cell", "pert_type"]).size().unstack(fill_value=0)
    t = t.reindex(index=list(want), columns=["trt_cp", "trt_xpr", "trt_sh"], fill_value=0)
    t.index = [want[i] for i in t.index]
    return t


# ---------------------------------------------------------------- figures
def fig_literature(out):
    lit = pd.read_csv(ROOT / "docs/literature.csv", encoding="utf-8-sig")
    rows = []
    for r in lit.itertuples():
        role, omics = LIT_ROLE[r.key]
        rows.append(dict(key=r.key, label=SHORT.get(r.key, r.method), year=int(r.year),
                         row=role, omics=omics, priority=r.priority))
    t = pd.DataFrame(rows).sort_values(["row", "year", "key"])
    t.to_csv(out / "tables/literature_map.csv", index=False)

    # Years with papers are spaced evenly (ordinal axis) so labels have room; ticks name the year.
    years = sorted(t.year.unique())
    xpos = {y: i for i, y in enumerate(years)}
    fig, ax = plt.subplots(figsize=(5.65, 2.1))
    ypos = {r: len(LIT_ROWS) - i for i, r in enumerate(LIT_ROWS)}
    for (row, year), g in t.groupby(["row", "year"]):
        n = len(g)
        offsets = np.linspace(-0.36, 0.36, n) if n > 1 else [0.0]
        for off, r in zip(offsets, g.itertuples()):
            x, y = xpos[year], ypos[row] + off
            p0 = r.priority == "P0"
            ax.scatter(x, y, s=46 if p0 else 26, color=OMICS_COLOR[r.omics],
                       edgecolor="white", linewidth=1.2, zorder=3)
            ax.text(x + 0.12, y, r.label, va="center", fontsize=6.4,
                    fontweight="bold" if p0 else "normal", color=INK)
    ax.set_yticks(list(ypos.values()), list(ypos.keys()))
    ax.set_ylim(0.45, len(LIT_ROWS) + 0.55)
    ax.set_xlim(-0.4, len(years) - 1 + 1.25)
    ax.set_xticks(range(len(years)), [str(y) for y in years])
    ax.tick_params(axis="x", labelsize=6.5)
    ax.set_xlabel("发表年份（只列有论文的年份，非等距）", fontsize=6.4, color=MUTED)
    clean_axes(ax, "x")
    ax.spines["left"].set_visible(False)
    handles = [Line2D([], [], marker="o", ls="", color=OMICS_COLOR[k], markersize=5,
                      label=OMICS_LABEL[k]) for k in ("RNA", "PROT", "BOTH")]
    handles.append(Line2D([], [], ls="", label="粗体 = P0 优先阅读"))
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, 1.13), ncol=4,
              fontsize=6.6, handletextpad=0.2, columnspacing=1.0)
    save(fig, out, "fig1_literature_map")
    return {"papers": int(len(t)), "by_row": t.row.value_counts().to_dict(),
            "involving_protein": int(t.omics.isin(["PROT", "BOTH"]).sum())}


def fig_landscape(out, lincs):
    cp = lincs[lincs.pert_type == "trt_cp"]
    lincs_pt = ("LINCS L1000", "RNA", int(cp.cell.nunique()), int(cp.pert_id.nunique()),
                "GSE92742 + GSE70138 元数据计算")
    pts = [lincs_pt] + FACTS["landscape"]
    t = pd.DataFrame(pts, columns=["dataset", "omics", "n_cell_lines", "n_compounds", "note"])
    t.to_csv(out / "tables/dataset_landscape.csv", index=False)

    fig, ax = plt.subplots(figsize=(2.85, 2.2))
    for r in t.itertuples():
        ax.scatter(r.n_cell_lines, r.n_compounds, s=48, color=OMICS_COLOR[r.omics],
                   edgecolor="white", linewidth=1.2, zorder=3)
        dx, dy, ha, va = 1.2, 1.0, "left", "center"
        if r.dataset == "LINCS L1000":
            dx, ha = 0.82, "right"
        elif "Basu" in r.dataset:
            dy, va = 1.12, "bottom"
        elif "MSV" in r.dataset:
            dy, va = 0.9, "top"
        ax.text(r.n_cell_lines * dx, r.n_compounds * dy, r.dataset.replace("\n", " "),
                va=va, ha=ha, fontsize=6.3, color=INK)
    ax.set_xscale("log")
    ax.set_yscale("log")
    plain_log(ax, "x")
    plain_log(ax, "y")
    ax.set_xlim(0.7, 700)
    ax.set_ylim(12, 60000)
    ax.set_xlabel("细胞系数（对数）", fontsize=7)
    ax.set_ylabel("化合物数（对数）", fontsize=7)
    clean_axes(ax, "both")
    handles = [Line2D([], [], marker="o", ls="", color=OMICS_COLOR[k], markersize=5,
                      label=OMICS_LABEL[k]) for k in ("RNA", "PROT")]
    ax.legend(handles=handles, loc="lower right", fontsize=6.6)
    save(fig, out, "fig2_dataset_landscape")
    return {"lincs_cell_lines_with_compounds": lincs_pt[2], "lincs_unique_compounds": lincs_pt[3]}


def fig_cellline_overlap(out, counts):
    cols = ["LINCS 化合物", "LINCS CRISPR", "PTDS", "mtPTDS", "PTPC", "Tahoe-100M", "HepG2 蛋白组"]
    level = pd.DataFrame(0, index=CELL_ROWS, columns=cols)
    text = pd.DataFrame("", index=CELL_ROWS, columns=cols)
    for cell in CELL_ROWS:
        for col, pt in (("LINCS 化合物", "trt_cp"), ("LINCS CRISPR", "trt_xpr")):
            n = int(counts.loc[cell, pt])
            level.loc[cell, col] = 2 if n > 0 else 0
            text.loc[cell, col] = (f"{n/1e4:.1f}万" if n >= 10000 else f"{n:,}") if n else "–"
    for col, m in FACTS["membership"].items():
        for cell, v in m.items():
            level.loc[cell, col] = v
            text.loc[cell, col] = "✓" if v == 2 else "?"
    level.to_csv(out / "tables/cellline_overlap_level.csv")
    text.to_csv(out / "tables/cellline_overlap_text.csv")

    # Landscape layout for a full-width slide: datasets as rows, cell lines as columns.
    lv, tx = level.T, text.T
    cmap = matplotlib.colors.ListedColormap([SEQ["none"], SEQ["weak"], SEQ["strong"]])
    fig, ax = plt.subplots(figsize=(5.65, 1.5))
    ax.imshow(lv.values, cmap=cmap, vmin=0, vmax=2, aspect="auto")
    ax.set_xticks(range(len(CELL_ROWS)), [cell_label(c) for c in CELL_ROWS], rotation=38, ha="left",
                  va="bottom", fontsize=6.0, rotation_mode="anchor")
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(cols)), cols, fontsize=6.6)
    ax.tick_params(length=0)
    for i in range(len(cols)):
        for j in range(len(CELL_ROWS)):
            v = lv.iat[i, j]
            ax.text(j, i, tx.iat[i, j], ha="center", va="center", fontsize=6.0,
                    color="white" if v == 2 else (INK if v == 1 else MUTED))
    ax.set_xticks(np.arange(-.5, len(CELL_ROWS)), minor=True)
    ax.set_yticks(np.arange(-.5, len(cols)), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.5)
    ax.tick_params(which="minor", length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    for j in (0, 1):  # outline the two candidate cell lines (MCF7, A375)
        ax.add_patch(plt.Rectangle((j - .5, -.5), 1, len(cols), fill=False, ec=INK, lw=1.0,
                                   zorder=5, clip_on=False))
    handles = [Patch(color=SEQ["strong"], label="有数据（✓ 或签名数）"),
               Patch(color=SEQ["weak"], label="论文提及 / 元数据候选（?）"),
               Patch(color=SEQ["none"], label="无"),
               Patch(fill=False, ec=INK, lw=1.0, label="首选细胞系")]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.45, -0.02), ncol=4,
              fontsize=6.4, handlelength=1.0, columnspacing=1.2)
    save(fig, out, "fig3_cellline_overlap")


def fig_lincs_coverage(out, counts):
    cells = ["MCF7", "A375", "HepG2", "BT20", "HS578T", "MDA-MB-231", "HCT116"]
    t = counts.loc[cells]
    t.to_csv(out / "tables/lincs_coverage.csv")
    panels = [("trt_cp", "化合物签名"), ("trt_xpr", "CRISPR 敲除签名"), ("trt_sh", "shRNA 敲低签名")]
    fig, axes = plt.subplots(1, 3, figsize=(5.65, 1.7), sharey=True)
    y = np.arange(len(cells))[::-1]
    for ax, (col, title) in zip(axes, panels):
        vals = t[col].values
        ax.barh(y, np.where(vals > 0, vals, np.nan), height=0.62, color=RNA,
                edgecolor="white", linewidth=1.0)
        top = max(vals.max(), 1)
        for yi, v in zip(y, vals):
            label = f"{v:,}" if v else "无"
            ax.text(v * 1.15 if v else 1.2, yi, label, va="center", fontsize=6.2,
                    color=INK, fontweight="normal" if v else "bold")
        ax.set_xscale("log")
        ax.set_xlim(1, top * 12)
        plain_log(ax, "x")
        ax.set_title(title, fontsize=7.2, color=INK, loc="left")
        clean_axes(ax, "x")
        ax.tick_params(axis="x", labelsize=6)
    axes[0].set_yticks(y, [cell_label(c) for c in cells], fontsize=6.6)
    save(fig, out, "fig4_lincs_coverage")


def fig_hepg2(out):
    h = FACTS["hepg2"]
    lanes = [
        ("与 GSE51952 配对", [("蛋白组药物", h["proteome_drugs"]), ("转录组药物", h["gse51952_drugs"]),
                            ("药名重叠", h["gse51952_name_overlap"]), ("同剂量", h["gse51952_same_dose"])]),
        ("与 LINCS Phase I 配对", [("蛋白组药物", h["proteome_drugs"]),
                                  ("24 h / 10 µM 化合物", h["lincs_p1_24h_10uM_compounds"]),
                                  ("药名精确匹配", h["lincs_p1_name_overlap"])]),
    ]
    pd.DataFrame([(lane, s, v) for lane, st in lanes for s, v in st],
                 columns=["lane", "stage", "n"]).to_csv(out / "tables/hepg2_attempt.csv", index=False)
    fig, axes = plt.subplots(2, 1, figsize=(2.85, 2.1), sharex=True,
                             gridspec_kw={"height_ratios": [4, 3], "hspace": 0.55})
    for ax, (lane, stages) in zip(axes, lanes):
        y = np.arange(len(stages))[::-1]
        vals = [v for _, v in stages]
        ax.barh(y, vals, height=0.6, color=[ORDINAL[min(i, 3)] for i in range(len(stages))],
                edgecolor="white", linewidth=1.0)
        for yi, v in zip(y, vals):
            ax.text(v + 3, yi, str(v), va="center", fontsize=6.4,
                    color=INK, fontweight="bold" if v == 0 else "normal")
        ax.set_yticks(y, [s for s, _ in stages], fontsize=6.5)
        ax.set_title(lane, fontsize=7, loc="left", color=INK)
        clean_axes(ax, "x")
        ax.tick_params(axis="x", labelsize=6)
    axes[-1].set_xlim(0, 200)
    save(fig, out, "fig5_hepg2_attempt")


def load_alignment():
    rd = lambda n: pd.read_csv(ALIGN_DIR / n, encoding="utf-8-sig")
    pairs, samples = rd("matched_pairs.csv"), rd("matched_ptds_samples.csv")
    rna, resol = rd("matched_rna_obs.csv"), rd("ptds_drug_resolution.csv")
    rna = rna.merge(pairs[["rna_pert_id", "ptds_drug"]].rename(columns={"rna_pert_id": "pert_id"}),
                    on="pert_id", how="left", validate="many_to_one")
    assert rna.ptds_drug.notna().all(), "RNA signature without a matched PTDS drug"
    return pairs, samples, rna, resol


def short_drug(s):
    s = re.sub(r"\s*\(=#\d+\)", "", s)
    for salt in (" Hydrochloride", " Monohydrate", " Ditosylate Hydrate", " Hydrate", " Tosylate",
                 " sulfate"):
        s = s.replace(salt, "")
    return s


def fig_ptds_alignment(out, pairs, samples, rna, resol):
    n_ptds = int(resol.ptds_drug.nunique())
    n_resolved = int((resol.status == "resolved").sum())
    n_matched = int(pairs.ptds_drug.nunique())
    rna["dose_time"] = rna.pert_itime.astype(str) + " / " + rna.pert_idose.astype(str)
    strict_rna = rna[(rna.pert_itime == "24 h") & (rna.pert_idose == "10 uM")]
    s24 = samples[(samples.Pert_Time == 24) & np.isclose(samples.Pert_Does1, 10.0)]
    strict_drugs = sorted(set(strict_rna.ptds_drug) & set(s24.Pert_Name1))
    stages = [("PTDS 单药", n_ptds), ("PubChem 结构解析", n_resolved),
              ("LINCS MCF7 有签名", n_matched), ("24 h / 10 µM\n两边都有", len(strict_drugs))]
    pd.DataFrame(stages, columns=["stage", "n_drugs"]).to_csv(out / "tables/ptds_lincs_funnel.csv",
                                                              index=False)
    fig, ax = plt.subplots(figsize=(2.8, 1.65))
    y = np.arange(len(stages))[::-1]
    ax.barh(y, [v for _, v in stages], height=0.62, color=ORDINAL, edgecolor="white", linewidth=1.0)
    for yi, (_, v) in zip(y, stages):
        ax.text(v + 1.2, yi, str(v), va="center", fontsize=7, color=INK)
    ax.set_yticks(y, [s for s, _ in stages], fontsize=6.6)
    ax.set_xlim(0, 75)
    ax.set_xlabel("药物数", fontsize=6.8)
    clean_axes(ax, "x")
    ax.tick_params(axis="x", labelsize=6)
    save(fig, out, "fig6_ptds_lincs_funnel")

    # condition grid: modality x time, all at 10 uM
    times = [6, 24, 48]
    rna_t = rna.groupby(rna.pert_itime.str.replace(" h", "").astype(int)).size()
    prot_t = samples[np.isclose(samples.Pert_Does1, 10.0)].groupby("Pert_Time").size()
    grid = pd.DataFrame({"RNA 签名（LINCS）": [int(rna_t.get(t, 0)) for t in times],
                         "蛋白样本（PTDS）": [int(prot_t.get(t, 0)) for t in times]}, index=times)
    grid.index.name = "time_h"
    grid.to_csv(out / "tables/condition_grid_10uM.csv")
    fig, ax = plt.subplots(figsize=(2.8, 1.65))
    ax.axvspan(0.55, 1.45, color="#eef4fc", zorder=0)
    ax.text(1, 1.62, "严格条件匹配", ha="center", fontsize=6.6, color=RNA, fontweight="bold")
    for row, (col, color) in enumerate(zip(grid.columns, (RNA, PROT))):
        for j, t in enumerate(times):
            n = grid.loc[t, col]
            if n:
                ax.scatter(j, 1 - row, s=18 + 2.2 * n, color=color, alpha=0.9,
                           edgecolor="white", linewidth=1.2, zorder=3)
            ax.text(j, 1 - row - 0.36, str(n) if n else "无", ha="center", fontsize=6.6,
                    color=INK if n else MUTED)
    ax.set_xticks(range(3), [f"{t} h" for t in times], fontsize=7)
    ax.set_yticks([1, 0], list(grid.columns), fontsize=6.6)
    ax.set_xlim(-0.6, 2.6)
    ax.set_ylim(-0.6, 1.8)
    ax.set_xlabel("处理时间（剂量均为 10 µM）", fontsize=6.8)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    save(fig, out, "fig8_condition_grid")

    # per drug: RNA signatures vs PTDS 24 h samples (two panels, one axis each)
    per = pd.DataFrame({
        "rna_signatures_24h_10uM": strict_rna.groupby("ptds_drug").size(),
        "ptds_samples_6h": samples[samples.Pert_Time == 6].groupby("Pert_Name1").size(),
        "ptds_samples_24h": s24.groupby("Pert_Name1").size(),
        "ptds_samples_48h": samples[samples.Pert_Time == 48].groupby("Pert_Name1").size(),
    }).fillna(0).astype(int).sort_values("rna_signatures_24h_10uM")
    per.index.name = "ptds_drug"
    per.to_csv(out / "tables/ptds_lincs_per_drug.csv")
    labels = [short_drug(d) for d in per.index]
    y = np.arange(len(per))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.65, 2.2), sharey=True,
                                 gridspec_kw={"width_ratios": [3, 2], "wspace": 0.08})
    a1.barh(y, per.rna_signatures_24h_10uM, height=0.66, color=RNA, edgecolor="white", linewidth=0.8)
    for yi, v in zip(y, per.rna_signatures_24h_10uM):
        a1.text(v * 1.12, yi, str(v), va="center", fontsize=5.8, color=INK)
    a1.set_xscale("log")
    a1.set_xlim(0.8, 260)
    plain_log(a1, "x")
    a1.set_title("LINCS MCF7：RNA 签名数（24 h / 10 µM）", fontsize=7, loc="left")
    a2.barh(y, per.ptds_samples_24h, height=0.66, color=PROT, edgecolor="white", linewidth=0.8)
    for yi, v in zip(y, per.ptds_samples_24h):
        a2.text(v + 0.08, yi, str(v), va="center", fontsize=5.8, color=INK)
    a2.set_xlim(0, 4)
    a2.set_xticks([0, 1, 2, 3])
    a2.set_title("PTDS MCF7：24 h 蛋白样本数", fontsize=7, loc="left")
    a1.set_yticks(y, labels, fontsize=6.2)
    for ax in (a1, a2):
        clean_axes(ax, "x")
        ax.tick_params(axis="x", labelsize=6)
    save(fig, out, "fig7_ptds_lincs_per_drug")

    return {
        "ptds_single_drugs": n_ptds, "ptds_drugs_resolved": n_resolved,
        "ptds_drugs_matched_lincs_mcf7": n_matched,
        "ptds_drugs_strict_24h_10uM": len(strict_drugs),
        "rna_signatures_total": int(len(rna)),
        "rna_signatures_24h_10uM": int(len(strict_rna)),
        "rna_dose_time_combinations": rna.dose_time.value_counts().to_dict(),
        "ptds_samples_by_time_10uM": {int(k): int(v) for k, v in prot_t.items()},
        "ptds_samples_24h_10uM_matched_drugs": int(len(s24)),
        "ptds_dose_unit_source": "ProteinTalks Methods: single-drug experiments used a standard 10 µM",
    }


def fig_benchmark(out):
    t = pd.DataFrame(FACTS["ptpc_benchmark"], columns=["model", "omics", "AUPRC", "AUROC"])
    t.to_csv(out / "tables/ptpc_benchmark.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(2.85, 1.8), sharey=True,
                             gridspec_kw={"wspace": 0.3})
    y = np.arange(len(t))[::-1]
    for ax, metric in zip(axes, ("AUPRC", "AUROC")):
        ax.barh(y, t[metric], height=0.62, color=[OMICS_COLOR[o] for o in t.omics],
                edgecolor="white", linewidth=1.0)
        for yi, v in zip(y, t[metric]):
            ax.text(v + 0.015, yi, f"{v:.2f}", va="center", fontsize=6.4, color=INK)
        ax.set_xlim(0, 1)
        ax.set_xticks([0, 0.5, 1], ["0", "0.5", "1"])
        ax.set_title(metric, fontsize=7.2, loc="left")
        clean_axes(ax, "x")
        ax.tick_params(axis="x", labelsize=6)
    axes[0].set_yticks(y, t.model, fontsize=6.8)
    handles = [Patch(color=OMICS_COLOR[k], label=f"{OMICS_LABEL[k]}模型") for k in ("PROT", "RNA")]
    axes[0].legend(handles=handles, loc="upper left", bbox_to_anchor=(0, -0.16), ncol=2,
                   fontsize=6.4, handlelength=1.0)
    save(fig, out, "fig9_ptpc_benchmark")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(ROOT / "reports/weekly-2026-10-16"))
    out = Path(ap.parse_args().out)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    setup_style()

    lincs = load_lincs()
    counts = lincs_counts(lincs)
    summary = {"lincs_counts": counts.to_dict(orient="index")}
    summary["literature"] = fig_literature(out)
    summary["landscape"] = fig_landscape(out, lincs)
    fig_cellline_overlap(out, counts)
    fig_lincs_coverage(out, counts)
    fig_hepg2(out)
    summary["ptds_lincs"] = fig_ptds_alignment(out, *load_alignment())
    fig_benchmark(out)
    summary["facts_from_papers"] = {k: v for k, v in FACTS.items() if k != "membership"}
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=int))
    print(json.dumps(summary["ptds_lincs"], ensure_ascii=False, indent=2))
    print("figures:", sorted(p.name for p in (out / "figures").glob("*.png")))


if __name__ == "__main__":
    main()
