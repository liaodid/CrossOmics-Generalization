#!/bin/bash
# Regenerate the weekly-report figures on Vulcan (CPU only, about 1 minute).
# Usage, from the repo root:  mkdir -p logs && sbatch script/slurm/make_weekly_figures.sbatch
#SBATCH --job-name=weekly-figures
#SBATCH --account=aip-zhouyang
#SBATCH --time=00:20:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --output=logs/%x_%j.out
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
export MPLCONFIGDIR=$SLURM_TMPDIR/mpl XDG_CACHE_HOME=$SLURM_TMPDIR/cache
module --force purge
module load StdEnv/2026 python/3.14.7 scipy-stack/2026b
[ -s data/lincs-l1000/raw/metadata/GSE92742_Broad_LINCS_sig_info.txt.gz ] || bash script/audit_lincs_metadata.sh
python script/make_weekly_figures.py
