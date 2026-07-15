#!/usr/bin/env python3

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import pyBigWig
from Bio import SeqIO


BED_COLUMNS = ["chrom", "start", "end", "name", "score", "strand"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build raw sequence/signal matrices for filtered IR/nonIR BED intervals."
    )
    parser.add_argument("--bed", required=True, help="Input BED file.")
    parser.add_argument("--fasta", required=True, help="Genome FASTA file.")
    parser.add_argument("--chip", required=True, help="H3K36me3 BigWig file.")
    parser.add_argument("--dnase", required=True, help="DNase/DHS BigWig file.")
    parser.add_argument("--cpg-plus", required=True, help="CpG plus-strand BigWig file.")
    parser.add_argument("--cpg-minus", required=True, help="CpG minus-strand BigWig file.")
    parser.add_argument("--output", required=True, help="Output .npz file.")
    return parser.parse_args()


def require_file(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Missing file: {path}")
    return path


def integer_encode(seq):
    mapping = {"A": 0, "C": 1, "G": 2, "T": 3, "a": 0, "c": 1, "g": 2, "t": 3}
    return np.array([mapping[nucleotide] for nucleotide in seq if nucleotide in mapping])


def resolve_fasta_chrom(chrom, fasta_index):
    if chrom in fasta_index:
        return chrom
    if chrom.startswith("chr") and chrom[3:] in fasta_index:
        return chrom[3:]
    prefixed = "chr" + chrom
    if prefixed in fasta_index:
        return prefixed
    raise KeyError(f"Chromosome {chrom} not found in FASTA")


def interval_chrom(interval):
    return interval.chrom if str(interval.chrom).startswith("chr") else "chr" + str(interval.chrom)


def clip_interval(start, end, chrom_size):
    start = max(0, int(start))
    end = min(int(end), chrom_size)
    return start, end


def extract_sequences(bed_df, fasta_file):
    fasta_index = SeqIO.index(str(fasta_file), "fasta")
    sequences = []
    try:
        for row in bed_df.itertuples(index=False):
            chrom = resolve_fasta_chrom(str(row.chrom), fasta_index)
            record = fasta_index[chrom]
            start, end = clip_interval(row.start, row.end, len(record))
            seq = record.seq[start:end]
            if str(row.strand) == "-":
                seq = seq.reverse_complement()
            sequences.append(str(seq))
    finally:
        fasta_index.close()
    return sequences


def extract_signal(bigwig_file, bed_df):
    bw = pyBigWig.open(str(bigwig_file))
    signals = []
    chrom_sizes = bw.chroms()
    try:
        for row in bed_df.itertuples(index=False):
            chrom = interval_chrom(row)
            if chrom not in chrom_sizes:
                signals.append(None)
                continue

            start, end = clip_interval(row.start, row.end, chrom_sizes[chrom])
            signal = bw.values(chrom, start, end, numpy=True)
            if str(row.strand) == "-":
                signal = signal[::-1]
            signals.append(signal)
    finally:
        bw.close()
    return signals


def extract_strand_specific_methylation(bw_plus_path, bw_minus_path, bed_df):
    bw_plus = pyBigWig.open(str(bw_plus_path))
    bw_minus = pyBigWig.open(str(bw_minus_path))
    signals = []
    chrom_sizes = bw_plus.chroms()
    try:
        for row in bed_df.itertuples(index=False):
            chrom = interval_chrom(row)
            if chrom not in chrom_sizes:
                signals.append(None)
                continue

            start, end = clip_interval(row.start, row.end, chrom_sizes[chrom])
            if str(row.strand) == "-":
                signal = np.array(bw_minus.values(chrom, start, end, numpy=True))[::-1]
            elif str(row.strand) == "+":
                signal = np.array(bw_plus.values(chrom, start, end, numpy=True))
            else:
                signal = np.array([0.0] * (end - start))
            signals.append(signal)
    finally:
        bw_plus.close()
        bw_minus.close()
    return signals


def safe_resize(arr, target_len):
    if arr is None:
        return np.zeros(target_len)

    arr = np.nan_to_num(arr, nan=0.0)
    arr = arr[:target_len]
    if len(arr) < target_len:
        arr = np.pad(arr, (0, target_len - len(arr)), mode="constant", constant_values=0)
    return arr


def main():
    args = parse_args()
    bed_file = require_file(args.bed)
    fasta_file = require_file(args.fasta)
    chip_file = require_file(args.chip)
    dnase_file = require_file(args.dnase)
    cpg_plus_file = require_file(args.cpg_plus)
    cpg_minus_file = require_file(args.cpg_minus)
    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    bed_df = pd.read_csv(
        bed_file,
        sep="\t",
        header=None,
        names=BED_COLUMNS,
        dtype={"chrom": str, "name": str, "score": str, "strand": str},
        low_memory=False,
    )
    sequences = extract_sequences(bed_df, fasta_file)
    chip_seq_signals = extract_signal(chip_file, bed_df)
    dnase_seq_signals = extract_signal(dnase_file, bed_df)
    cpg_signals = extract_strand_specific_methylation(
        cpg_plus_file, cpg_minus_file, bed_df
    )

    data = []
    bed_info_list = []

    for i, sequence in enumerate(sequences):
        integer_encoded_sequence = integer_encode(sequence)
        target_len = len(integer_encoded_sequence)
        chip_seq_signal = safe_resize(chip_seq_signals[i], target_len)
        dnase_seq_signal = safe_resize(dnase_seq_signals[i], target_len)
        cpg_signal = safe_resize(cpg_signals[i], target_len)

        combined_features = np.vstack(
            [
                integer_encoded_sequence,
                chip_seq_signal,
                dnase_seq_signal,
                cpg_signal,
            ]
        )
        data.append(combined_features)

        row = bed_df.iloc[i]
        bed_info_list.append([row["chrom"], row["start"], row["end"], row["strand"]])

    npz_dict = {f"arr_{idx}": arr for idx, arr in enumerate(data)}
    npz_dict["bed_info"] = np.array(bed_info_list, dtype=object)
    np.savez(output_file, **npz_dict)
    print(f"Saved {len(data)} intervals to {output_file}")


if __name__ == "__main__":
    main()
