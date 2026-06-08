#!/usr/bin/env python3
import argparse
from pathlib import Path
from Bio.PDB import MMCIFParser, MMCIFIO, Select

def parse_args():
    parser = argparse.ArgumentParser(description="Split CIF files by chain.")
    parser.add_argument("--input_dir", type=str, default="results/chai1_fold_all", help="Input directory with CIF files")
    parser.add_argument("--output_dir", type=str, default="results/chai1_split_chains", help="Output directory for split chains")
    return parser.parse_args()

class ChainSelect(Select):
    def __init__(self, chain_id):
        self.chain_id = chain_id
    def accept_chain(self, chain):
        return chain.id == self.chain_id

def main():
    args = parse_args()
    
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    
    input_root = project_root / args.input_dir
    output_dir = project_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    parser = MMCIFParser(QUIET=True)
    failed = []

    for cif_path in sorted(input_root.rglob("pred.model_idx_*.cif")):
        try:
            structure = parser.get_structure(cif_path.stem, str(cif_path))
            model = next(structure.get_models())
            for chain in model:
                chain_id = chain.id.strip() if chain.id.strip() else "X"
                out_name = f"{cif_path.parent.name}__{cif_path.stem}__chain_{chain_id}.cif"
                out_path = output_dir / out_name
                
                io = MMCIFIO()
                io.set_structure(structure)
                io.save(str(out_path), select=ChainSelect(chain_id))
        except Exception as e:
            failed.append((str(cif_path), str(e)))

    if failed:
        print(f"Failed to process {len(failed)} files.")

if __name__ == "__main__":
    main()
