#!/bin/bash
#SBATCH --job-name=14_plots
#SBATCH --partition=amd_256M
#SBATCH --time=00:10:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --output=logs/14_plots_%j.out
#SBATCH --error=logs/14_plots_%j.err

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

export MPLCONFIGDIR="${PROJECT_ROOT}/.mplconfig"
mkdir -p "$MPLCONFIGDIR"

python src/14_plot_interpretability.py
