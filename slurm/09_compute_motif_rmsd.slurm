#!/bin/bash
#SBATCH --job-name=09_rmsd
#SBATCH --partition=amd_256M
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --output=logs/09_rmsd_%j.out
#SBATCH --error=logs/09_rmsd_%j.err

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

CHAINS_DIR="${CHAINS_DIR:-results/chai1_split_chains}"

python src/09_compute_motif_rmsd.py \
    --chains_dir "${CHAINS_DIR}"
