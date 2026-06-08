#!/bin/bash
#SBATCH --job-name=15_figs
#SBATCH --partition=amd_256M
#SBATCH --time=00:15:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --output=logs/15_figs_%j.out
#SBATCH --error=logs/15_figs_%j.err

set -euo pipefail

# Setup conda and activate environment
CONDA_BASE=$(conda info --base 2>/dev/null || echo "$HOME/miniconda3")
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate chai1_env

# Move to project root
if [ -d "src" ]; then
    PROJECT_ROOT=$(pwd)
else
    PROJECT_ROOT=$(cd .. && pwd)
fi
cd "$PROJECT_ROOT"
mkdir -p logs

export MPLCONFIGDIR="${PROJECT_ROOT}/.mplconfig"
mkdir -p "$MPLCONFIGDIR"

python src/15_generate_figures.py
