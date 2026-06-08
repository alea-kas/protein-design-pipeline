#!/usr/bin/env python3
import argparse
import joblib
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from pathlib import Path
from sklearn.metrics import roc_curve, auc
from kan import KAN

def parse_args():
    parser = argparse.ArgumentParser(description="Generate final figures for diploma.")
    parser.add_argument("--align_csv", type=str, default="results/foldseek_align.csv", help="Foldseek alignments")
    parser.add_argument("--ml_csv", type=str, default="results/ml_features_dataset.csv", help="ML dataset")
    parser.add_argument("--rf_model", type=str, default="results/rf_models/rf_motif.joblib", help="Random Forest model")
    parser.add_argument("--rf_imp", type=str, default="results/rf_models/rf_feature_importances.csv", help="RF importances")
    parser.add_argument("--kan_model", type=str, default="results/kan_models/kan_model_selected.pt", help="KAN model")
    parser.add_argument("--out_dir", type=str, default="results/figures", help="Output directory")
    return parser.parse_args()

def main():
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    fig_dir = project_root / args.out_dir
    fig_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="talk")

    print("=== Part 1: Generating Distribution Plots (Fig 1-3) ===")
    align_path = project_root / args.align_csv
    if align_path.exists():
        df_align = pd.read_csv(align_path).dropna(subset=["motif_rmsd", "qtmscore", "lddt"])

        def plot_dist(df, col, thr, thr_type, title, filename, palette, x_label, bins, xlim, x_step):
            df_plot = df.copy()
            if thr_type == "max":
                df_plot = df_plot[df_plot[col] <= thr + 1.0]
                df_plot["Status"] = np.where(df_plot[col] <= thr, "Accepted", "Rejected")
            else:
                df_plot["Status"] = np.where(df_plot[col] >= thr, "Accepted", "Rejected")

            plt.figure(figsize=(9, 6))
            ax = sns.histplot(data=df_plot, x=col, hue="Status", palette=palette, bins=bins, multiple="stack", edgecolor="white")
            plt.axvline(thr, color="red", linestyle="--", linewidth=3)
            ax.xaxis.set_major_locator(ticker.MultipleLocator(x_step))
            plt.xlim(*xlim)
            plt.xlabel(x_label)
            plt.ylabel("Number of structures")
            plt.title(title)
            plt.savefig(fig_dir / filename, dpi=300, bbox_inches='tight')
            plt.close()

        plot_dist(df_align, "motif_rmsd", 6.0, "max", "Motif RMSD Distribution", "fig1_dist_rmsd.png", {"Accepted": "#1f77b4", "Rejected": "#b0bec5"}, "Motif RMSD (Å)", np.arange(2.0, 7.1, 0.1), (2.0, 7.0), 0.5)
        plot_dist(df_align, "qtmscore", 0.35, "min", "QTM-score Distribution", "fig2_dist_qtmscore.png", {"Accepted": "#ff7f0e", "Rejected": "#b0bec5"}, "Global Structural Similarity (qtmscore)", np.arange(0, 1.01, 0.01), (0, 1.0), 0.1)
        plot_dist(df_align, "lddt", 0.35, "min", "lDDT Distribution", "fig3_dist_lddt.png", {"Accepted": "#2ca02c", "Rejected": "#b0bec5"}, "Local Quality (lDDT)", np.arange(0, 1.01, 0.01), (0, 1.0), 0.1)

    print("=== Part 2: Generating ML Model Plots (Fig 4-6) ===")
    ml_path = project_root / args.ml_csv
    if ml_path.exists() and (project_root / args.rf_imp).exists() and (project_root / args.rf_model).exists():
        df_ml = pd.read_csv(ml_path)
        df_ml["is_good"] = ((df_ml["motif_rmsd"] <= 6.0) & (df_ml["qtmscore"] >= 0.35) & (df_ml["lddt"] >= 0.35) & (df_ml["alnlen"] >= 50)).astype(int)

        # Fig 4: RF Feature Importances
        imp = pd.read_csv(project_root / args.rf_imp, index_col=0).sort_values("importance", ascending=False)
        imp.index = [{'chai_plddt': 'Local Confidence (pLDDT)', 'seq_length': 'Scaffold Length', 'score_rank': 'Internal Rank'}.get(i, i) for i in imp.index]
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x=imp["importance"], y=imp.index, color="#1f77b4")
        plt.xlabel("Feature Importance (Mean Decrease Impurity)")
        plt.savefig(fig_dir / "fig4_rf_feature_importances.png", dpi=300, bbox_inches='tight')
        plt.close()

        # Fig 5: RF ROC Curve
        rf = joblib.load(project_root / args.rf_model)
        rf_features = list(pd.read_csv(project_root / args.rf_imp, index_col=0).index)
        df_clean = df_ml.dropna(subset=rf_features + ["is_good"])
        
        fpr, tpr, _ = roc_curve(df_clean["is_good"], rf.predict_proba(df_clean[rf_features])[:, 1])
        plt.figure(figsize=(8, 8))
        plt.plot(fpr, tpr, color="#d62728", lw=3, label=f"ROC-AUC = {auc(fpr, tpr):.2f}")
        plt.plot([0, 1], [0, 1], color="grey", lw=2, linestyle="--")
        plt.xlabel("False Positive Rate (FPR)")
        plt.ylabel("True Positive Rate (TPR)")
        plt.legend(loc="lower right")
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.savefig(fig_dir / "fig5_roc_curve_rf.png", dpi=300, bbox_inches='tight')
        plt.close()

    # Fig 6: KAN Splines
    kan_path = project_root / args.kan_model
    if kan_path.exists():
        try:
            kan_model = KAN(width=[2, 4, 1], grid=2, k=3)
            kan_model.load_state_dict(torch.load(kan_path, map_location='cpu', weights_only=False))
            kan_model(torch.rand((10, 2)) * 2 - 1)
            kan_model.plot(scale=1.5)
            plt.savefig(fig_dir / "fig6_kan_splines_plot.png", dpi=300, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Could not generate KAN plot: {e}")

    print(f"=== All figures generated successfully in {fig_dir} ===")

if __name__ == "__main__":
    main()
