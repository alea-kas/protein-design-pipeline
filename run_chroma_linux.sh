#!/bin/bash
set -e

# если conda не инициализирована автоматически, раскомментировать:
# source ~/miniconda3/etc/profile.d/conda.sh

cd "$(dirname "$0")"

echo "=== Chroma motif generation ==="
conda activate chromaenv
python src/generate_chroma_motif_scaffolds.py
echo "=== Done ==="
