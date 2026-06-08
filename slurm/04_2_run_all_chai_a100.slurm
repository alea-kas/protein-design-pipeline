#!/bin/bash
#SBATCH --job-name=04_2_all
#SBATCH --partition=amd_256M
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --output=logs/04_2_all_%j.out
#SBATCH --error=logs/04_2_all_%j.err

set -euo pipefail

# Move to project root
if [ -d "src" ]; then
    PROJECT_ROOT=$(pwd)
else
    PROJECT_ROOT=$(cd .. && pwd)
fi
cd "$PROJECT_ROOT"
mkdir -p logs

# Limit to 9000 batches (~45,000 structures) to match diploma results
N_BATCHES=9000
STEP=1000

start=1
while [ "$start" -le "$N_BATCHES" ]; do
    end=$((start + STEP - 1))
    if [ "$end" -gt "$N_BATCHES" ]; then
        end=$N_BATCHES
    fi

    sbatch slurm/04_chai1_a100.slurm "$start" "$end"
    start=$((end + 1))
done
