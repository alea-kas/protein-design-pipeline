from pathlib import Path
from Bio import SeqIO

BASE = Path("protein-design-pipeline")
PDB_FILE = BASE / "data" / "motif.pdb"
FASTA_FILE = BASE / "data" / "motif.fasta"

records = SeqIO.parse(str(PDB_FILE), "pdb-seqres")
count = SeqIO.write(records, str(FASTA_FILE), "fasta")
print(f"Converted {count} record(s) to {FASTA_FILE}")