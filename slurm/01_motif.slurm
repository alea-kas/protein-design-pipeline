#!/bin/bash
#SBATCH --job-name=01_motif
#SBATCH --partition=amd_256M
#SBATCH --time=00:10:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --output=logs/motif_%j.out
#SBATCH --error=logs/motif_%j.err

set -euo pipefail

# Setup conda and activate environment
CONDA_BASE=$(conda info --base 2>/dev/null || echo "$HOME/miniconda3")
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate rfdiffusion_env

# Move to project root
if [ -d "src" ]; then
    PROJECT_ROOT=$(pwd)
else
    PROJECT_ROOT=$(cd .. && pwd)
fi
cd "$PROJECT_ROOT"

# Run script with default arguments
# Custom motif example: python src/01_motif.py --pdb "my_prot.pdb" --motif_pos 10 20 --motif_aa "A" "C"
python src/01_motif.py
