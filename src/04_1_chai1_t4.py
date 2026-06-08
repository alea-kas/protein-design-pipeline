#!/usr/bin/env python3
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Combine FASTA files and split into batches for Chai-1.")
    parser.add_argument("--fa_dir", type=str, default="data/mpnn", help="Input directory with FASTA files")
    parser.add_argument("--out_fa", type=str, default="data/mpnn/chai1_input_all.fa", help="Path for combined FASTA output")
    parser.add_argument("--batch_dir", type=str, default="data/chai1_batches", help="Output directory for FASTA batches")
    parser.add_argument("--max_tokens", type=int, default=800, help="Maximum tokens per batch")
    return parser.parse_args()

def combine_fastas(fa_dir: Path, out_fa: Path):
    out_fa.parent.mkdir(parents=True, exist_ok=True)
    per_base_counts = {}
    seen = set()

    with out_fa.open("w") as fout:
        # Search for files starting with 'protein_'
        for fa_path in sorted(fa_dir.glob("protein_*")):
            base = fa_path.stem
            if base not in per_base_counts:
                per_base_counts[base] = 0

            seq_lines = []
            with fa_path.open() as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    if line.startswith(">"):
                        if seq_lines:
                            seq = "".join(seq_lines)
                            per_base_counts[base] += 1
                            var_idx = per_base_counts[base]
                            name = f"{base}_var{var_idx:03d}"
                            while name in seen:
                                var_idx += 1
                                name = f"{base}_var{var_idx:03d}"
                            seen.add(name)
                            fout.write(f">protein|name={name}\n{seq}\n")
                            seq_lines = []
                    else:
                        seq_lines.append(line)
            
            # Process last sequence in file
            if seq_lines:
                seq = "".join(seq_lines)
                per_base_counts[base] += 1
                var_idx = per_base_counts[base]
                name = f"{base}_var{var_idx:03d}"
                while name in seen:
                    var_idx += 1
                    name = f"{base}_var{var_idx:03d}"
                seen.add(name)
                fout.write(f">protein|name={name}\n{seq}\n")

def split_into_batches(fasta_path: Path, batch_dir: Path, max_tokens: int):
    batch_dir.mkdir(parents=True, exist_ok=True)
    records = []
    name = None
    seq_lines = []

    with fasta_path.open() as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith(">"):
                if name is not None and seq_lines:
                    records.append((name, "".join(seq_lines)))
                desc = line[1:]
                parts = desc.split("|")
                fields = {k: v for p in parts[1:] if "=" in p for k, v in [p.split("=", 1)]}
                name = fields.get("name", parts[0])
                seq_lines = []
            else:
                seq_lines.append(line)

    if name is not None and seq_lines:
        records.append((name, "".join(seq_lines)))

    current, current_tokens, batch_idx = [], 0, 0

    for name, seq in records:
        length = len(seq)
        if length > max_tokens:
            batch_idx += 1
            with (batch_dir / f"batch_{batch_idx:04d}.fa").open("w") as bf:
                bf.write(f">protein|name={name}\n{seq}\n")
            continue
        
        if current_tokens + length > max_tokens and current:
            batch_idx += 1
            with (batch_dir / f"batch_{batch_idx:04d}.fa").open("w") as bf:
                for n, s in current: bf.write(f">protein|name={n}\n{s}\n")
            current, current_tokens = [], 0
            
        current.append((name, seq))
        current_tokens += length

    if current:
        batch_idx += 1
        with (batch_dir / f"batch_{batch_idx:04d}.fa").open("w") as bf:
            for n, s in current: bf.write(f">protein|name={n}\n{s}\n")

def main():
    args = parse_args()
    
    # Resolve relative paths relative to project root
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    
    fa_dir = project_root / args.fa_dir
    out_fa = project_root / args.out_fa
    batch_dir = project_root / args.batch_dir

    if not out_fa.exists():
        combine_fastas(fa_dir, out_fa)
    
    if not batch_dir.exists() or not list(batch_dir.glob("batch_*.fa")):
        split_into_batches(out_fa, batch_dir, args.max_tokens)

if __name__ == "__main__":
    main()
