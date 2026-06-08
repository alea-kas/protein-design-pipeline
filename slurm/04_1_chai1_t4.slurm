#!/bin/bash
#SBATCH --job-name=04_1_chai1
#SBATCH --partition=gpu_T4
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --output=logs/04_1_chai1_%j.out
#SBATCH --error=logs/04_1_chai1_%j.err

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

export CHAI_DOWNLOADS_DIR="${PROJECT_ROOT}/chai1_downloads"
mkdir -p logs data/mpnn data/chai1_batches

# Generate FASTA batches for Chai-1
python src/04_1_chai1_t4.py
