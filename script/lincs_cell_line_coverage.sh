#!/usr/bin/env bash
# Count LINCS L1000 signatures per cell line for a given list of cell lines,
# split by perturbation type (compound / CRISPR knockout / shRNA) and phase.
# Reuses the sig_info tables cached by script/audit_lincs_metadata.sh (run that first).
#
# Usage (from the repo root):
#   bash script/lincs_cell_line_coverage.sh A375 MCF7 HCT116
#   bash script/lincs_cell_line_coverage.sh            # default: cell lines named in ProteinTalks
#
# Cell names are compared after upper-casing and removing "-", " ", "." and a leading "NCI",
# so "MDA-MB-231" matches LINCS "MDAMB231" and "NCI-H1975" matches "H1975". LINCS CRISPR
# cell ids carry a batch suffix (e.g. "A375.311"), which is stripped before matching.
set -euo pipefail
export LC_ALL=C

DIR=${LINCS_META_DIR:-data/lincs-l1000/raw/metadata}
P1="$DIR/GSE92742_Broad_LINCS_sig_info.txt.gz"
P2="$DIR/GSE70138_Broad_LINCS_sig_info_2017-03-06.txt.gz"
for f in "$P1" "$P2"; do
    [ -s "$f" ] || { echo "missing $f; run script/audit_lincs_metadata.sh first" >&2; exit 1; }
done

if [ $# -eq 0 ]; then
    # Cell lines named in the ProteinTalks paper (PTDS / mtPTDS / PTPC / PTNC)
    set -- A375 HCT116 NCI-H1975 NCI-H2170 "Panc 10.05" MCF7 T47D BT20 BT549 HS578T \
           MDA-MB-231 MDA-MB-436 MDA-MB-453 MDA-MB-468 HCC38 HCC70 HCC1143 HCC1187 \
           HCC1395 HCC1806 HCC1937
fi
WANT=$(printf '%s\n' "$@" | tr 'a-z' 'A-Z' | sed -E 's/[- .]//g; s/^NCI//' | paste -sd, -)

count() {  # count <file> <phase label>
    zcat "$1" | awk -F'\t' -v want="$WANT" -v phase="$2" '
        BEGIN { n = split(want, w, ","); for (i = 1; i <= n; i++) keep[w[i]] = 1 }
        NR > 1 && ($4 == "trt_cp" || $4 == "trt_xpr" || $4 == "trt_sh") {
            c = toupper($5); sub(/\.[0-9]+$/, "", c); gsub(/[- .]/, "", c); sub(/^NCI/, "", c)
            if (c in keep) cnt[c "\t" phase "\t" $4]++
        }
        END { for (k in cnt) print k "\t" cnt[k] }'
}

{
    printf 'cell\tphase\tpert_type\tsignatures\n'
    { count "$P1" "GSE92742"; count "$P2" "GSE70138"; } | sort -k1,1 -k2,2r -k3,3
} | column -t -s $'\t'

echo
echo "# requested but not found in either phase:"
found=$( { count "$P1" x; count "$P2" x; } | cut -f1 | sort -u)
for c in $(echo "$WANT" | tr ',' ' '); do
    grep -qx "$c" <<< "$found" || printf '%s ' "$c"
done
echo
