#!/usr/bin/env python3
import argparse
import pandas as pd
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Extract ML features from CIF files.")
    parser.add_argument("--cif_dir", type=str, default="results/chai1_split_chains", help="Split chains directory")
    parser.add_argument("--foldseek", type=str, default="results/foldseek_align.csv", help="Merged Foldseek/RMSD CSV")
    parser.add_argument("--output", type=str, default="results/ml_features_dataset.csv", help="Output dataset CSV")
    return parser.parse_args()

def main():
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    cif_dir = project_root / args.cif_dir
    fs_file = project_root / args.foldseek
    out_file = project_root / args.output

    features = []
    
    # Fast parsing of pLDDT from CIF files
    for cif_path in cif_dir.glob("*.cif"):
        try:
            plddt_values = []
            with open(cif_path, 'r') as f:
                for line in f:
                    if line.startswith("ATOM") or line.startswith("HETATM"):
                        try:
                            # 4th column from the end in mmCIF usually contains B-factor/pLDDT
                            plddt_values.append(float(line.split()[-4]))
                        except ValueError: 
                            pass
            
            avg_plddt = sum(plddt_values) / len(plddt_values) if plddt_values else 0
            features.append({
                "query": cif_path.stem,
                "chai_plddt": avg_plddt,
                # Divide by 8 assuming average atoms per residue
                "seq_length": len(plddt_values) // 8 
            })
        except Exception: 
            pass

    fs_df = pd.read_csv(fs_file)
    features_df = pd.DataFrame(features)
    
    merged_df = pd.merge(fs_df, features_df, on="query", how="inner")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(out_file, index=False)

if __name__ == "__main__":
    main()
