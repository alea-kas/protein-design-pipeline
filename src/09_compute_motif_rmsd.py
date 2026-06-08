#!/usr/bin/env python3
import argparse
import math
import pandas as pd
from pathlib import Path
from Bio.PDB import MMCIFParser, PDBParser, Superimposer

def parse_args():
    parser = argparse.ArgumentParser(description="Compute motif RMSD against reference.")
    parser.add_argument("--ref_pdb", type=str, default="data/raw/mini_motif.pdb", help="Reference PDB/CIF")
    parser.add_argument("--ref_chain", type=str, default="M", help="Reference chain ID")
    parser.add_argument("--ref_start", type=int, default=1, help="Reference start residue")
    parser.add_argument("--ref_end", type=int, default=5, help="Reference end residue")
    parser.add_argument("--motif_start", type=int, default=73, help="Motif start residue in query")
    parser.add_argument("--motif_end", type=int, default=77, help="Motif end residue in query")
    parser.add_argument("--chains_dir", type=str, default="results/chai1_split_chains", help="Split chains dir")
    parser.add_argument("--output", type=str, default="results/motif_rmsd.csv", help="Output CSV")
    return parser.parse_args()

def main():
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    ref_path = project_root / args.ref_pdb
    chains_dir = project_root / args.chains_dir
    out_path = project_root / args.output
    
    ref_parser = MMCIFParser(QUIET=True) if ref_path.suffix.lower() in [".cif", ".mmcif"] else PDBParser(QUIET=True)
    ref_structure = ref_parser.get_structure("ref", str(ref_path))
    ref_chain = next(ref_structure.get_models())[args.ref_chain]

    ref_atoms = [
        res["CA"] for res in ref_chain 
        if args.ref_start <= res.id[1] <= args.ref_end and res.has_id("CA")
    ]

    results = []
    chains_parser = MMCIFParser(QUIET=True)

    for cif_path in sorted(chains_dir.glob("*.cif")):
        query_name = cif_path.stem
        try:
            structure = chains_parser.get_structure(query_name, str(cif_path))
            chains = list(next(structure.get_models()).get_chains())
            mob_atoms = [
                res["CA"] for res in chains[0] 
                if args.motif_start <= res.id[1] <= args.motif_end and res.has_id("CA")
            ]

            if len(mob_atoms) == len(ref_atoms) and len(mob_atoms) > 0:
                sup = Superimposer()
                sup.set_atoms(ref_atoms, mob_atoms)
                results.append({"query": query_name, "motif_rmsd": float(sup.rms)})
            else:
                results.append({"query": query_name, "motif_rmsd": math.nan})
        except Exception:
            results.append({"query": query_name, "motif_rmsd": math.nan})

    df = pd.DataFrame(results)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

if __name__ == "__main__":
    main()
