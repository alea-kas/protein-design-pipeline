#!/usr/bin/env python3
import argparse
import pandas as pd
from pathlib import Path
import os

def parse_args():
    parser = argparse.ArgumentParser(description="Prepare CIF directory for filtered candidates.")
    parser.add_argument("--csv", type=str, default="results/ml_filtered_candidates.csv", help="Filtered candidates CSV")
    parser.add_argument("--out_dir", type=str, default="results/chai1_filtered_chains", help="Output directory for symlinks")
    return parser.parse_args()

def main():
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    csv_path = project_root / args.csv
    out_dir = project_root / args.out_dir

    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    if "filepath" not in df.columns or df.empty:
        print("No valid candidates or missing 'filepath' column.")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for idx, row in df.iterrows():
        src_path = Path(row["filepath"])
        if src_path.exists():
            dest_path = out_dir / src_path.name
            if not dest_path.exists():
                os.symlink(src_path, dest_path)
            count += 1

    print(f"Created {count} symlinks in {out_dir}")

if __name__ == "__main__":
    main()
