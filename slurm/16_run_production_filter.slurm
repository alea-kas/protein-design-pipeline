#!/bin/bash
#SBATCH --job-name=16_prod
#SBATCH --partition=amd_256M
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --output=logs/16_prod_%j.out
#SBATCH --error=logs/16_prod_%j.err

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

python src/16_run_production_filter.py
