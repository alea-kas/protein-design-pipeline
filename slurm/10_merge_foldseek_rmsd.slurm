#!/bin/bash
#SBATCH --job-name=10_merge
#SBATCH --partition=amd_256M
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --output=logs/10_merge_%j.out
#SBATCH --error=logs/10_merge_%j.err

set -euo pipefail

CONDA_BASE=$(conda info --base 2>/dev/null || echo "$HOME/miniconda3")
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate chai1_env

if [ -d "src" ]; then
    PROJECT_ROOT=$(pwd)
else
    PROJECT_ROOT=$(cd .. && pwd)
fi
cd "$PROJECT_ROOT"
mkdir -p logs

FOLDSEEK_TSV="${FOLDSEEK_TSV:-results/foldseek_hits_best.tsv}"

python src/10_merge_foldseek_rmsd.py \
    --foldseek "${FOLDSEEK_TSV}"
