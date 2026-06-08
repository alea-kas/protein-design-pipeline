#!/bin/bash
#SBATCH --job-name=05_split
#SBATCH --partition=amd_2Tb
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=4G
#SBATCH --output=logs/05_split_%j.out
#SBATCH --error=logs/05_split_%j.err

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
mkdir -p logs results/chai1_split_chains

python src/05_split_chains.py
