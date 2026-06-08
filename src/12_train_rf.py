#!/usr/bin/env python3
import argparse
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

def parse_args():
    parser = argparse.ArgumentParser(description="Train Random Forest classifier.")
    parser.add_argument("--dataset", type=str, default="results/ml_features_dataset.csv", help="Input dataset")
    parser.add_argument("--out_dir", type=str, default="results/rf_models", help="Output models directory")
    # Soft thresholds matching diploma logic to retain ~6.4k positive examples
    parser.add_argument("--rmsd_thr", type=float, default=6.0, help="RMSD threshold (<=)")
    parser.add_argument("--qtm_thr", type=float, default=0.35, help="QTM score threshold (>=)")
    parser.add_argument("--lddt_thr", type=float, default=0.35, help="lDDT threshold (>=)")
    parser.add_argument("--alnlen_thr", type=int, default=50, help="Alignment length threshold (>=)")
    return parser.parse_args()

def main():
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    infile = project_root / args.dataset
    out_dir = project_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(infile).copy()
    rmsd_col = "motif_rmsd" if "motif_rmsd" in df.columns else "rmsd"

    thresholds = {
        rmsd_col: (args.rmsd_thr, "<="),
        "qtmscore": (args.qtm_thr, ">="),
        "lddt": (args.lddt_thr, ">="),
        "alnlen": (args.alnlen_thr, ">=")
    }

    # Mark positive class based on thresholds
    is_good = np.ones(len(df), dtype=bool)
    for col, (thr, op) in thresholds.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            if op == ">=":
                is_good &= (df[col] >= thr)
            else:
                is_good &= (df[col] <= thr)

    df["is_good"] = is_good.astype(int)

    # Select features
    feature_cols = ["chai_plddt", "seq_length"]
    for pf in ["score_rank", "mpnn_score", "seq_recovery", "chai_score"]:
        if pf in df.columns: 
            feature_cols.append(pf)

    X = df[feature_cols].fillna(0.0)
    y = df["is_good"]
    
    # Train Random Forest
    rf = RandomForestClassifier(
        n_estimators=500, 
        max_depth=10, 
        class_weight="balanced", 
        random_state=42, 
        n_jobs=-1
    )
    rf.fit(X, y)

    # Save model and feature importances
    joblib.dump(rf, out_dir / "rf_motif.joblib")
    
    importances = pd.Series(rf.feature_importances_, index=feature_cols).sort_values(ascending=False)
    importances.to_csv(out_dir / "rf_feature_importances.csv", header=["importance"])

if __name__ == "__main__":
    main()
