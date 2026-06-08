#!/bin/bash
#SBATCH --job-name=13_kan
#SBATCH --partition=gpu_T4
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=logs/13_kan_%j.out
#SBATCH --error=logs/13_kan_%j.err

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

python src/13_train_kan_regression.py
