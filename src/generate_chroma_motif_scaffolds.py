"""
generate_chroma_motif_scaffolds.py

Генерирует последовательности белков длиной L с заданным мотивом:
- читает мотив из data/motif.fasta
- генерирует много последовательностей в Chroma
- оставляет только те, где мотив реально встречается
- сохраняет первые N подходящих в FASTA

Запускать в среде chromaenv.
"""

from pathlib import Path
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

from chroma import Chroma


DATA_DIR = Path("data")          # общий для ноутбука и кластера
MOTIF_FASTA = DATA_DIR / "motif.fasta"


def load_motif(fasta_path: Path) -> str:
    records = list(SeqIO.parse(str(fasta_path), "fasta"))
    if not records:
        raise ValueError(f"No sequences found in {fasta_path}")
    return str(records[0].seq).upper()


def generate_with_motif(
    motif: str,
    chain_length: int = 60,
    n_wanted: int = 10,
    batch_size: int = 20,
    out_fasta: Path = DATA_DIR / "chroma_scaffolds_motif.fasta",
):
    """
    Генерирует белки длиной chain_length и отбирает те, где есть мотив.
    batch_size — сколько цепей просим за один вызов Chroma.
    """
    chroma = Chroma()

    motif = motif.upper()
    if len(motif) > chain_length:
        raise ValueError("Motif is longer than desired chain length")

    records = []
    attempt = 0

    while len(records) < n_wanted:
        attempt += 1
        print(f"Sampling batch {attempt}...")

        protein = chroma.sample(chain_lengths=[chain_length] * batch_size,
                                design_t=0.5,
                                langevin_factor=8,
                                inverse_temperature=8)

        # Сохраняем во временный FASTA и читаем обратно, чтобы не гадать API
        tmp_fasta = DATA_DIR / "_tmp_chroma_batch.fasta"
        protein.to_fasta(str(tmp_fasta))

        for rec in SeqIO.parse(str(tmp_fasta), "fasta"):
            seq = str(rec.seq).upper()
            if motif in seq:
                idx = len(records) + 1
                new_rec = SeqRecord(
                    Seq(seq),
                    id=f"chroma_motif_{idx}",
                    description=f"len={len(seq)}; motif_present",
                )
                records.append(new_rec)
                if len(records) >= n_wanted:
                    break

        tmp_fasta.unlink(missing_ok=True)
        print(f"Collected {len(records)} / {n_wanted} sequences with motif.")

    out_fasta.parent.mkdir(parents=True, exist_ok=True)
    SeqIO.write(records, str(out_fasta), "fasta")
    print(f"Saved {len(records)} sequences with motif to {out_fasta}")


if __name__ == "__main__":
    motif = load_motif(MOTIF_FASTA)
    generate_with_motif(
        motif=motif,
        chain_length=60,      # можно менять 50–80
        n_wanted=10,
        batch_size=20,
        out_fasta=DATA_DIR / "chroma_scaffolds_motif_10.fasta",
    )
