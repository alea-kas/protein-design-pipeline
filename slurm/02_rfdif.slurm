#!/bin/bash
#SBATCH --job-name=02_rfdif
#SBATCH --partition=amd_256M
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --output=logs/rfdif_%j.out
#SBATCH --error=logs/rfdif_%j.err

set -euo pipefail

# TODO: User must set paths to DGL, conda, and RFdiffusion directory
export DGL_HOME="$HOME/.dgl"
export DGLBACKEND="pytorch"
export DGLDEFAULTDIR="$DGL_HOME"
export DGL_DOWNLOAD_DIR="$DGL_HOME"
mkdir -p "$DGL_HOME"

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

# Pipeline parameters (default values reproduce diploma results)
NUM_DESIGNS=50
OUT_PREFIX="outputs/protein"
CONTIGMAP="[72/M1-5/73]"

# Set path to local RFdiffusion installation
RFDIFFUSION_DIR="$HOME/RFdiffusion"

python "$RFDIFFUSION_DIR/scripts/run_inference.py" \
  inference.input_pdb=data/raw/mini_motif.pdb \
  inference.output_prefix="${OUT_PREFIX}" \
  inference.num_designs=${NUM_DESIGNS} \
  "contigmap.contigs=${CONTIGMAP}" \
  inference.deterministic=False \
  ppi.hotspot_res=null \
  potentials.guiding_potentials=null \
  inference.ckpt_override_path="$RFDIFFUSION_DIR/models/ActiveSite_ckpt.pt" \
  inference.model_directory_path="$RFDIFFUSION_DIR/models"

mkdir -p data/design
mv outputs/*.pdb data/design/ 2>/dev/null || true
rm -rf outputs
