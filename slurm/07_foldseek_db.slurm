#!/bin/bash
#SBATCH --job-name=07_fs_db
#SBATCH --partition=amd_256M
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --output=logs/07_fs_db_%j.out
#SBATCH --error=logs/07_fs_db_%j.err

set -euo pipefail

# TODO: User must set path to Foldseek binary
FOLDSEEK_BIN="$HOME/foldseek/bin/foldseek"

if [ -d "src" ]; then
    PROJECT_ROOT=$(pwd)
else
    PROJECT_ROOT=$(cd .. && pwd)
fi
cd "$PROJECT_ROOT"
mkdir -p logs tools/db_pdb tmp_pdb

${FOLDSEEK_BIN} databases PDB tools/db_pdb/db_pdb tmp_pdb
${FOLDSEEK_BIN} makepaddedseqdb tools/db_pdb/db_pdb tools/db_pdb/pdb_pad
