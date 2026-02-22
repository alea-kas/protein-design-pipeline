from pathlib import Path
from Bio import SeqIO
import csv
import re

VALID_AA = set("ACDEFGHIKLMNPQRSTVWY")  #                                                                   стандартные 20 аминокислот

def check_sequence(seq):
    seq = seq.upper()
    return set(ch for ch in seq if ch not in VALID_AA)

def summarize_fasta_file(path, file_id=None):
    path = Path(path)
    if file_id is None:
        file_id = path.name

    records_info = []
    bad_chars = set()

    for record in SeqIO.parse(str(path), "fasta"):
        seq = str(record.seq).upper()
        length = len(seq)
        bad = check_sequence(seq)
        bad_chars |= bad

        records_info.append({
            "file": file_id,
            "seq_id": record.id,
            "description": record.description,
            "length": length,
            "bad_chars": "".join(sorted(bad))
        })

    return records_info, bad_chars

def get_next_version_path(base_dir, base_name="sequences_summary"):
    """
    Ищет файлы base_name_vX.csv и возвращает путь для следующей версии.
    """
    base_dir = Path(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    pattern = re.compile(rf"{re.escape(base_name)}_v(\d+)\.csv$")
    max_v = 0
    for p in base_dir.glob(f"{base_name}_v*.csv"):
        m = pattern.match(p.name)
        if m:
            v = int(m.group(1))
            if v > max_v:
                max_v = v
    next_v = max_v + 1
    return base_dir / f"{base_name}_v{next_v}.csv"

def summarize_many_fastas(input_paths, output_dir="../data"):
    """
    Читает несколько FASTA-файлов и сохраняет новую версию CSV с авто-нумерацией.
    """
    all_records = []
    all_bad_chars = set()

    for path in input_paths:
        recs, bad = summarize_fasta_file(path)
        all_records.extend(recs)
        all_bad_chars |= bad

    print(f"Total sequences: {len(all_records)}")
    if all_records:
        lengths = [r["length"] for r in all_records]
        print(f"Min length: {min(lengths)}")
        print(f"Max length: {max(lengths)}")
        print(f"Average length: {sum(lengths)/len(lengths):.1f}")
    if all_bad_chars:
        print("Non-standard characters found:", "".join(sorted(all_bad_chars)))
    else:
        print("No non-standard amino acid codes found.")

    out_path = get_next_version_path(output_dir, base_name="sequences_summary")
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["file", "seq_id", "description", "length", "bad_chars"]
        )
        writer.writeheader()
        writer.writerows(all_records)
    print(f"Saved table to {out_path}")

if __name__ == "__main__":
    input_files = [
        "../data/example.fasta",
        #                                                                                    ДОБАВИТЬ FASTA
    ]
    summarize_many_fastas(input_files, "../data")
