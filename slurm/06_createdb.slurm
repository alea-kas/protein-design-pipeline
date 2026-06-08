#!/bin/bash
#SBATCH --job-name=06_db
#SBATCH --partition=amd_2Tb
#SBATCH --time=10:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --output=logs/06_db_%j.out
#SBATCH --error=logs/06_db_%j.err

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

INPUT_DIR="${INPUT_DIR:-results/chai1_split_chains}"
QUERY_DB="${QUERY_DB:-results/queryDB_chai1_chains}"

${FOLDSEEK_BIN} createdb "${INPUT_DIR}" "${QUERY_DB}"
