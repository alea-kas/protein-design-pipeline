#!/usr/bin/env python3
import argparse
import pandas as pd
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Merge Foldseek and RMSD metrics.")
    parser.add_argument("--foldseek", type=str, default="results/foldseek_hits_best.tsv", help="Foldseek TSV")
    parser.add_argument("--rmsd", type=str, default="results/motif_rmsd.csv", help="RMSD CSV")
    parser.add_argument("--output", type=str, default="results/foldseek_align.csv", help="Output CSV")
    return parser.parse_args()

def main():
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    fold_path = project_root / args.foldseek
    rmsd_path = project_root / args.rmsd
    out_path = project_root / args.output

    fold_cols = ["query", "target", "lddt", "alntmscore", "qtmscore", "ttmscore", "prob", "evalue", "alnlen", "pident"]
    fold_df = pd.read_csv(fold_path, sep="\t", names=fold_cols)
    rmsd_df = pd.read_csv(rmsd_path)

    full_df = fold_df.merge(rmsd_df, on="query", how="left")
    
    # Calculate score_rank based on diploma weights
    full_df["score_rank"] = (
        full_df["qtmscore"].fillna(0) * 0.45 +
        full_df["lddt"].fillna(0) * 0.45 -
        full_df["motif_rmsd"].fillna(999) * 0.10
    )

    full_df = full_df.sort_values(
        by=["score_rank", "qtmscore", "lddt", "motif_rmsd"],
        ascending=[False, False, False, True]
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    full_df.to_csv(out_path, index=False)

if __name__ == "__main__":
    main()
