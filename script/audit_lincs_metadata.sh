#!/usr/bin/env bash
# Audit LINCS L1000 signature metadata for one cell line:
#   - how many compound (trt_cp) signatures exist, by time and dose
#   - whether any CRISPR knockout (trt_xpr) signatures exist, and for which cell lines
# Only the small sig_info tables are downloaded (~13 MB in total), never the expression matrices.
#
# Usage (from the repo root):
#   bash script/audit_lincs_metadata.sh                 # HEPG2, files cached in data/lincs-l1000/raw/metadata
#   CELL=MCF7 bash script/audit_lincs_metadata.sh       # another cell line
#   bash script/audit_lincs_metadata.sh /path/to/cache  # custom cache directory
set -euo pipefail
export LC_ALL=C

OUT=${1:-data/lincs-l1000/raw/metadata}
CELL=${CELL:-HEPG2}
P1=GSE92742_Broad_LINCS_sig_info.txt.gz
P2=GSE70138_Broad_LINCS_sig_info_2017-03-06.txt.gz
mkdir -p "$OUT"

fetch() {  # fetch <base_url> <file>; skip if already cached
    [ -s "$OUT/$2" ] || curl -sfL -o "$OUT/$2" "$1/$2"
}
fetch https://ftp.ncbi.nlm.nih.gov/geo/series/GSE92nnn/GSE92742/suppl "$P1"
fetch https://ftp.ncbi.nlm.nih.gov/geo/series/GSE70nnn/GSE70138/suppl "$P2"
echo "## sha256"
(cd "$OUT" && sha256sum "$P1" "$P2")

# The two phases use different column layouts:
#   GSE92742 (Phase I):  3 pert_iname, 4 pert_type, 5 cell_id, 6 pert_dose, 8 pert_idose ("10 µM"), 11 pert_itime ("24 h")
#   GSE70138 (Phase II): 3 pert_iname, 4 pert_type, 5 cell_id, 6 pert_idose ("10.0 um"), 7 pert_itime ("24 h")
p1() { zcat "$OUT/$P1" | awk -F'\t' -v c="$CELL" "NR>1 && \$5==c $1"; }
p2() { zcat "$OUT/$P2" | awk -F'\t' -v c="$CELL" "NR>1 && \$5==c $1"; }

echo
echo "## Phase I (GSE92742), cell_id == $CELL"
echo "# signatures by pert_type"
p1 '{print $4}' | sort | uniq -c | sort -rn
echo "# trt_cp signatures by pert_itime"
p1 '&& $4=="trt_cp" {print $11}' | sort | uniq -c | sort -rn
echo "# trt_cp at 24 h and pert_dose == 10: signatures / unique compounds"
p1 '&& $4=="trt_cp" && $11=="24 h" && $6+0==10' | wc -l
p1 '&& $4=="trt_cp" && $11=="24 h" && $6+0==10 {print $3}' | sort -u | wc -l

echo
echo "## Phase II (GSE70138), cell_id == $CELL"
echo "# signatures by pert_type"
p2 '{print $4}' | sort | uniq -c | sort -rn
echo "# trt_cp signatures by pert_itime | pert_idose (top 6)"
p2 '&& $4=="trt_cp" {print $7" | "$6}' | sort | uniq -c | sort -rn | head -6
echo "# trt_cp at 24 h and pert_idose 10 um: signatures / unique compounds"
p2 '&& $4=="trt_cp" && $7 ~ /^24/ && $6 ~ /^10(\.0)? /' | wc -l
p2 '&& $4=="trt_cp" && $7 ~ /^24/ && $6 ~ /^10(\.0)? / {print $3}' | sort -u | wc -l

echo
echo "## Cell lines with CRISPR knockout (trt_xpr) signatures"
echo "# Phase I"
zcat "$OUT/$P1" | awk -F'\t' '$4=="trt_xpr"{print $5}' | sort | uniq -c
echo "# Phase II"
zcat "$OUT/$P2" | awk -F'\t' '$4=="trt_xpr"{print $5}' | sort | uniq -c
