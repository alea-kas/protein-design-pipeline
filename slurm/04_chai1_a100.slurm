#!/bin/bash
#SBATCH --job-name=04_chai
#SBATCH --partition=gpu_A100
#SBATCH --gres=gpu:1
#SBATCH --time=55:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/04_chai_%j.out
#SBATCH --error=logs/04_chai_%j.err

set -euo pipefail

START=${1:-1}
END=${2:-999999}

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
mkdir -p logs results/chai1_fold_all

BATCH_DIR="data/chai1_batches"
OUT_ROOT="results/chai1_fold_all"

i=0
for bf in $(ls ${BATCH_DIR}/batch_*.fa 2>/dev/null | sort); do
    i=$((i+1))
    if [ "$i" -lt "$START" ] || [ "$i" -gt "$END" ]; then
        continue
    fi
    
    bname=$(basename "$bf" .fa)
    out_dir="${OUT_ROOT}/${bname}"
    mkdir -p "$out_dir"

    # Skip if already processed
    if ls "${out_dir}"/pred.model_idx_*.cif >/dev/null 2>&1; then
        continue
    fi

    # Run folding
    chai-lab fold "$bf" "$out_dir" \
      --num-trunk-recycles 4 \
      --num-diffn-samples 5
done
