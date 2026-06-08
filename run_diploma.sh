#!/bin/bash
set -e

# 1. Generation and Folding
J1=$(sbatch --parsable slurm/01_motif.slurm)
J2=$(sbatch --parsable --dependency=afterok:$J1 slurm/02_rfdif.slurm)
J3=$(sbatch --parsable --dependency=afterok:$J2 slurm/03_mpnn.slurm)
J4=$(sbatch --parsable --dependency=afterok:$J3 slurm/04_1_chai1_t4.slurm)
J5=$(sbatch --parsable --dependency=afterok:$J4 slurm/04_2_run_all_chai_a100.slurm)

# 2. Structural Alignment (Foldseek and RMSD) for all data
J6=$(sbatch --parsable --dependency=afterok:$J5 slurm/05_split_chains.slurm)
J7=$(sbatch --parsable --dependency=afterok:$J6 slurm/06_createdb.slurm)
J8=$(sbatch --parsable slurm/07_foldseek_db.slurm)
J9=$(sbatch --parsable --dependency=afterok:$J7:$J8 slurm/08_foldseek_search.slurm)
J10=$(sbatch --parsable --dependency=afterok:$J6 slurm/09_compute_motif_rmsd.slurm)
J11=$(sbatch --parsable --dependency=afterok:$J9:$J10 slurm/10_merge_foldseek_rmsd.slurm)

# 3. Machine Learning (RF and KAN)
J12=$(sbatch --parsable --dependency=afterok:$J11 slurm/11_prepare_ml.slurm)
J13=$(sbatch --parsable --dependency=afterok:$J12 slurm/12_train_rf.slurm)
J14=$(sbatch --parsable --dependency=afterok:$J12 slurm/13_train_kan_regression.slurm)

# 4. Interpretability and Figures
J15=$(sbatch --parsable --dependency=afterok:$J14 slurm/14_plot_interpretability.slurm)
J16=$(sbatch --parsable --dependency=afterok:$J13:$J14 slurm/15_generate_figures.slurm)

# 5. Test Production Filter
J17=$(sbatch --parsable --dependency=afterok:$J13 slurm/16_run_production_filter.slurm)

echo "Done"
