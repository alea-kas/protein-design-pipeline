#!/usr/bin/env python3
import argparse
import joblib
import sys
import pandas as pd
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Run Random Forest filter on new Chai-1 predictions.")
    parser.add_argument("--cif_dir", type=str, default="results/chai1_split_chains", help="Split chains directory")
    parser.add_argument("--rf_model", type=str, default="results/rf_models/rf_motif.joblib", help="Trained RF model")
    parser.add_argument("--output", type=str, default="results/ml_filtered_candidates.csv", help="Filtered output CSV")
    return parser.parse_args()

def main():
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    cif_dir = project_root / args.cif_dir
    model_path = project_root / args.rf_model
    out_candidates = project_root / args.output

    if not model_path.exists():
        sys.exit(1)

    rf_model = joblib.load(model_path)
    feature_cols = list(rf_model.feature_names_in_)

    features = []
    for cif_path in cif_dir.glob("*.cif"):
        try:
            plddt_values = []
            with open(cif_path, 'r') as f:
                for line in f:
                    if line.startswith("ATOM") or line.startswith("HETATM"):
                        try:
                            plddt_values.append(float(line.split()[-4]))
                        except ValueError: 
                            pass

            if not plddt_values: 
                continue

            features.append({
                "query": cif_path.stem,
                "chai_plddt": sum(plddt_values) / len(plddt_values),
                "seq_length": len(plddt_values) // 8,
                "score_rank": 1.0,
                "filepath": str(cif_path)
            })
        except Exception:
            pass

    df = pd.DataFrame(features)
    if df.empty:
        return

    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0.0

    df["ml_prediction"] = rf_model.predict(df[feature_cols])
    passed_df = df[df["ml_prediction"] == 1]

    out_candidates.parent.mkdir(parents=True, exist_ok=True)
    passed_df.to_csv(out_candidates, index=False)

if __name__ == "__main__":
    main()
