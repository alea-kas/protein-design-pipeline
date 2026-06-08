#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from Bio.PDB import PDBParser, PDBIO, Select
from Bio.PDB.StructureBuilder import StructureBuilder

def parse_args():
    parser = argparse.ArgumentParser(description="Extract motif and generate config.")
    # Default values reproduce the original diploma pipeline
    parser.add_argument("--pdb", type=str, default="7nl4.pdb", help="Input PDB in data/")
    parser.add_argument("--chain", type=str, default="A", help="Chain ID")
    parser.add_argument("--start", type=int, default=65, help="Segment start residue")
    parser.add_argument("--end", type=int, default=222, help="Segment end residue")
    parser.add_argument("--motif_pos", type=int, nargs="+", default=[65, 88, 207, 216, 222], help="Motif positions")
    parser.add_argument("--motif_aa", type=str, nargs="+", default=["T", "G", "S", "G", "R"], help="Expected amino acids")
    return parser.parse_args()

def load_chain(pdb_path: Path, chain_id: str):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("structure", str(pdb_path))
    model = structure[0]
    if chain_id not in model:
        raise ValueError(f"Chain {chain_id} not found in {pdb_path}")
    return model[chain_id]

def three_letter_to_one(resname: str) -> str:
    from Bio.Data.IUPACData import protein_letters_3to1
    name = resname.capitalize().strip()
    if name not in protein_letters_3to1:
        raise ValueError(f"Unknown residue: {resname}")
    return protein_letters_3to1[name]

def check_key_positions(chain, chain_id: str, key_positions: dict):
    for resid, expected_aa in key_positions.items():
        found_residue = next(
            (res for res in chain if res.id[0] == " " and res.id[1] == resid), 
            None
        )
        if not found_residue:
            raise ValueError(f"Residue {resid} not found in chain {chain_id}")

        actual_aa = three_letter_to_one(found_residue.resname)
        if actual_aa != expected_aa:
            raise ValueError(f"Position {resid}: expected {expected_aa}, got {actual_aa}")

def save_motifs_yaml(output_path: Path, pdb_name: str, chain_id: str,
                     start_resid: int, end_resid: int, key_positions: dict):
    yaml_text = f"""
    motif:
      pdb_id: "{pdb_name}"
      chain_id: "{chain_id}"
      segment:
        start: {start_resid}
        end: {end_resid}
      key_residues:
    """
    for resid, aa in sorted(key_positions.items()):
        yaml_text += f"        - position: {resid}\n"
        yaml_text += f'          aa: "{aa}"\n'

    yaml_text = textwrap.dedent(yaml_text).strip() + "\n"
    output_path.write_text(yaml_text, encoding="utf-8")

def save_mini_motif_pdb(input_pdb: Path, output_pdb: Path,
                        chain_id: str, motif_positions: list[int]):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("full", str(input_pdb))

    builder = StructureBuilder()
    builder.init_structure("mini")
    builder.init_model(0)
    builder.init_chain("M")

    mini_structure = builder.get_structure()
    mini_chain = mini_structure[0]["M"]

    new_resid = 1
    positions_set = set(motif_positions)

    for model in structure:
        for chain in model:
            if chain.id != chain_id:
                continue
            for residue in chain:
                if residue.id[0] != " ":
                    continue
                if residue.id[1] in positions_set:
                    residue_copy = residue.copy()
                    residue_copy.id = (" ", new_resid, " ")
                    mini_chain.add(residue_copy)
                    new_resid += 1

    class MiniChainSelector(Select):
        def accept_chain(self, chain):
            return chain.id == "M"

    io = PDBIO()
    io.set_structure(mini_structure)
    io.save(str(output_pdb), MiniChainSelector())

def main():
    args = parse_args()
    key_positions = dict(zip(args.motif_pos, args.motif_aa))

    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    data_dir = project_root / "data"
    raw_data_dir = data_dir / "raw"
    config_dir = project_root / "config"

    input_pdb_path = data_dir / args.pdb
    mini_motif_pdb_path = raw_data_dir / "mini_motif.pdb"
    motifs_yaml_path = config_dir / "motifs.yaml"

    config_dir.mkdir(parents=True, exist_ok=True)
    raw_data_dir.mkdir(parents=True, exist_ok=True)

    if not input_pdb_path.exists():
        raise FileNotFoundError(f"PDB file not found: {input_pdb_path}")

    chain = load_chain(input_pdb_path, args.chain)
    check_key_positions(chain, args.chain, key_positions)

    save_motifs_yaml(
        motifs_yaml_path,
        pdb_name=args.pdb,
        chain_id=args.chain,
        start_resid=args.start,
        end_resid=args.end,
        key_positions=key_positions,
    )

    save_mini_motif_pdb(
        input_pdb_path,
        mini_motif_pdb_path,
        args.chain,
        args.motif_pos,
    )

if __name__ == "__main__":
    main()
