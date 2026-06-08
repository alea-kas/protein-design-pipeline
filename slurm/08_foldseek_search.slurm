#!/bin/bash
#SBATCH --job-name=08_fs
#SBATCH --partition=gpu_T4
#SBATCH --time=48:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:1
#SBATCH --output=logs/08_fs_%j.out
#SBATCH --error=logs/08_fs_%j.err

set -euo pipefail

# TODO: User must set path to Foldseek binary
FOLDSEEK_BIN="$HOME/foldseek/bin/foldseek"

if [ -d "src" ]; then
    PROJECT_ROOT=$(pwd)
else
    PROJECT_ROOT=$(cd .. && pwd)
fi
cd "$PROJECT_ROOT"
mkdir -p logs

QUERY_DB="${QUERY_DB:-results/queryDB_chai1_chains}"
TARGET_DB_PAD="tools/db_pdb/pdb_pad"
OUT_TSV="${OUT_TSV:-results/foldseek_hits_best.tsv}"
TMP_DIR="tmp_fs_${SLURM_JOB_ID}"

mkdir -p "$(dirname "${OUT_TSV}")" "${TMP_DIR}"

${FOLDSEEK_BIN} easy-search "${QUERY_DB}" "${TARGET_DB_PAD}" \
    "${OUT_TSV}" "${TMP_DIR}" \
    --gpu 1 \
    --threads "${SLURM_CPUS_PER_TASK}" \
    --max-seqs 1 \
    --format-output "query,target,lddt,alntmscore,qtmscore,ttmscore,prob,evalue,alnlen,pident"

rm -rf "${TMP_DIR}"
