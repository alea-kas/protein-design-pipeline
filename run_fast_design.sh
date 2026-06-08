#!/bin/bash
set -e

# 1. Generation and Folding
J1=$(sbatch --parsable slurm/01_motif.slurm)
J2=$(sbatch --parsable --dependency=afterok:$J1 slurm/02_rfdif.slurm)
J3=$(sbatch --parsable --dependency=afterok:$J2 slurm/03_mpnn.slurm)
J4=$(sbatch --parsable --dependency=afterok:$J3 slurm/04_1_chai1_t4.slurm)
J5=$(sbatch --parsable --dependency=afterok:$J4 slurm/04_2_run_all_chai_a100.slurm)

# 2. Split CIFs
J6=$(sbatch --parsable --dependency=afterok:$J5 slurm/05_split_chains.slurm)

# 3. ML Filter and Prepare Directory
J16=$(sbatch --parsable --dependency=afterok:$J6 slurm/16_run_production_filter.slurm)
J17=$(sbatch --parsable --dependency=afterok:$J16 slurm/17_prepare_filtered_cifs.slurm)

# 4. Foldseek and RMSD for filtered candidates
export INPUT_DIR="results/chai1_filtered_chains"
export QUERY_DB="results/queryDB_filtered_chains"
export OUT_TSV="results/foldseek_hits_filtered.tsv"

J7=$(sbatch --parsable --dependency=afterok:$J17 \
    --export=ALL,INPUT_DIR="$INPUT_DIR",QUERY_DB="$QUERY_DB" slurm/06_createdb.slurm)
J8=$(sbatch --parsable slurm/07_foldseek_db.slurm)
J9=$(sbatch --parsable --dependency=afterok:$J7:$J8 \
    --export=ALL,QUERY_DB="$QUERY_DB",OUT_TSV="$OUT_TSV" slurm/08_foldseek_search.slurm)


J10=$(sbatch --parsable --dependency=afterok:$J17 \
    --export=ALL,CHAINS_DIR="$INPUT_DIR" slurm/09_compute_motif_rmsd.slurm)

# Merge results
J11=$(sbatch --parsable --dependency=afterok:$J9:$J10 \
    --export=ALL,FOLDSEEK_TSV="$OUT_TSV" slurm/10_merge_foldseek_rmsd.slurm)

echo "Done"
