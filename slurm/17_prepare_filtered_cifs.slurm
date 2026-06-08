#!/bin/bash
#SBATCH --job-name=17_prep_fs
#SBATCH --partition=amd_256M
#SBATCH --time=00:10:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --output=logs/17_prep_fs_%j.out
#SBATCH --error=logs/17_prep_fs_%j.err

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

python src/17_prepare_filtered_cifs.py
