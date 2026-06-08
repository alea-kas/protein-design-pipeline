#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as plt_sns
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Generate interpretability plots.")
    parser.add_argument("--dataset", type=str, default="results/ml_features_dataset.csv", help="Input dataset")
    parser.add_argument("--out_dir", type=str, default="results/figures", help="Output directory for figures")
    return parser.parse_args()

def main():
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    infile = project_root / args.dataset
    out_dir = project_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(infile).dropna(subset=["motif_rmsd", "chai_plddt", "seq_length", "score_rank"])
    df = df[df["motif_rmsd"] < 15.0]

    plt_sns.set_theme(style="whitegrid")

    plt.figure(figsize=(8, 6))
    plt_sns.regplot(x="chai_plddt", y="motif_rmsd", data=df, scatter_kws={'alpha':0.1, 's':10}, line_kws={'color': 'red'})
    plt.savefig(out_dir / "plot_plddt_vs_rmsd.png", dpi=300, bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(8, 6))
    plt_sns.regplot(x="seq_length", y="motif_rmsd", data=df, order=2, scatter_kws={'alpha':0.1, 's':10}, line_kws={'color': 'red'})
    plt.savefig(out_dir / "plot_length_vs_rmsd.png", dpi=300, bbox_inches='tight')
    plt.close()

    if df["score_rank"].nunique() < 20:
        plt.figure(figsize=(8, 6))
        plt_sns.boxplot(x="score_rank", y="motif_rmsd", data=df, palette="viridis")
        plt.savefig(out_dir / "plot_rank_vs_rmsd.png", dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    main()
