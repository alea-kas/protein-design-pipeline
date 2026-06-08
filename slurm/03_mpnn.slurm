#!/bin/bash
#SBATCH --job-name=03_mpnn
#SBATCH --partition=gpu_T4
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=40G
#SBATCH --output=logs/mpnn_%j.out
#SBATCH --error=logs/mpnn_%j.err

set -euo pipefail
module purge

# Setup conda
CONDA_BASE=$(conda info --base 2>/dev/null || echo "$HOME/miniconda3")
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate mpnn_env

# Move to project root
if [ -d "src" ]; then
    PROJECT_ROOT=$(pwd)
else
    PROJECT_ROOT=$(cd .. && pwd)
fi
cd "$PROJECT_ROOT"

# TODO: User must set path to ProteinMPNN installation
MPNN_DIR="$HOME/proteinmpnn"

INPUT_DIR="${PROJECT_ROOT}/data/design"
OUT_ROOT="${PROJECT_ROOT}/mpnn_tmp"
MPNN_FASTA_DIR="${PROJECT_ROOT}/data/mpnn"

mkdir -p "${OUT_ROOT}" "${MPNN_FASTA_DIR}"

# Parameters matching diploma results
N_STRUCTS=50
NUM_SEQ_PER_TARGET=2269

# Fixed positions configuration for binding site
# Adjust these for different motifs
FIXED_CHAIN="M"
FIXED_RESIDUES="73, 74, 75, 76, 77"

for i in $(seq 0 $((N_STRUCTS-1))); do
  PDB_NAME="protein_${i}"
  PDB_FILE="${INPUT_DIR}/${PDB_NAME}.pdb"
  FIXED_JSON="${OUT_ROOT}/fixed_positions_${i}.jsonl"

  if [ ! -f "${PDB_FILE}" ]; then
    continue
  fi

  # Create jsonl to fix motif residues
  cat > "${FIXED_JSON}" <<EOF
{"${PDB_NAME}": {"${FIXED_CHAIN}": [${FIXED_RESIDUES}]}}
EOF

  cd "${MPNN_DIR}"
  python protein_mpnn_run.py \
    --pdb_path "${PDB_FILE}" \
    --out_folder "${OUT_ROOT}/${PDB_NAME}" \
    --num_seq_per_target ${NUM_SEQ_PER_TARGET} \
    --batch_size 4 \
    --sampling_temp "0.2" \
    --omit_AAs C \
    --use_soluble_model \
    --fixed_positions_jsonl "${FIXED_JSON}" \
    --suppress_print 1
  cd "$PROJECT_ROOT"

  # Move generated fasta to final directory
  SEQ_DIR="${OUT_ROOT}/${PDB_NAME}/seqs"
  FA_FILE="${SEQ_DIR}/${PDB_NAME}.fa"

  if [ -f "${FA_FILE}" ]; then
    cp "${FA_FILE}" "${MPNN_FASTA_DIR}/${PDB_NAME}.fa"
  fi
done

rm -rf "${OUT_ROOT}"
