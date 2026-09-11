#!/usr/bin/env python3

import argparse
import csv
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np


BASE_MAP = {0: "A", 1: "C", 2: "G", 3: "T"}
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def parse_float_row(row):
    raw = ",".join(row)
    return [float(value) for value in raw.split(",") if value != ""]


def parse_base_row(row):
    raw = ",".join(row)
    bases = [int(round(float(base))) for base in raw.split(",") if base != ""]
    return "".join(BASE_MAP[base] for base in bases)


def find_high_regions(scores, direction, min_len):
    scores = np.asarray(scores).reshape(-1)

    if direction == "pos":
        filtered = scores[scores > 0]
        if len(filtered) == 0:
            return []
        threshold = filtered.mean() + filtered.std()
        mask = scores > threshold
    else:
        filtered = scores[scores < 0]
        if len(filtered) == 0:
            return []
        threshold = filtered.mean() - filtered.std()
        mask = scores < threshold

    regions = []
    start_idx = None
    for idx, is_high in enumerate(mask):
        if is_high and start_idx is None:
            start_idx = idx
        elif (not is_high) and (start_idx is not None):
            if idx - start_idx >= min_len:
                region_scores = scores[start_idx:idx]
                regions.append(
                    {
                        "start": start_idx,
                        "end": idx,
                        "ig_score": float(region_scores.mean()),
                    }
                )
            start_idx = None

    if start_idx is not None and len(mask) - start_idx >= min_len:
        region_scores = scores[start_idx:len(mask)]
        regions.append(
            {
                "start": start_idx,
                "end": len(mask),
                "ig_score": float(region_scores.mean()),
            }
        )

    return regions


def extract_motifs(all_scores, sequences, direction, min_len):
    global_dict = defaultdict(lambda: {"count": 0, "positions": [], "ig_scores": []})
    for seq_index, seq_scores in enumerate(all_scores):
        regions = find_high_regions(seq_scores, direction, min_len)
        sequence = sequences[seq_index]
        intron_length = len(sequence)

        if len(seq_scores) != intron_length:
            raise ValueError(
                f"Length mismatch at row {seq_index}: "
                f"scores={len(seq_scores)}, bases={intron_length}"
            )

        for region in regions:
            start, end = region["start"], region["end"]
            motif_seq = sequence[start:end]
            entry = global_dict[motif_seq]
            entry["count"] += 1
            entry["positions"].append(
                {
                    "seq_index": seq_index,
                    "start": start,
                    "end": end,
                    "intron_length": intron_length,
                }
            )
            entry["ig_scores"].append(region["ig_score"])

    return global_dict


def perform_motif_analysis(score_file, seq_file, output_file, direction, min_motif_len, count_threshold):
    all_scores = []
    with open(score_file, newline="") as file_obj:
        for row in csv.reader(file_obj):
            if row:
                all_scores.append(parse_float_row(row))

    sequences = []
    with open(seq_file, newline="") as file_obj:
        for row in csv.reader(file_obj):
            if row:
                sequences.append(parse_base_row(row))

    if len(all_scores) != len(sequences):
        raise ValueError(
            f"Row count mismatch: scores={len(all_scores)}, sequences={len(sequences)}"
        )

    global_dict = extract_motifs(all_scores, sequences, direction, min_motif_len)

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", newline="") as output_handle:
        writer = csv.writer(output_handle)
        writer.writerow(["Motif_ID", "Motif_Seq", "Occurrences", "Mean_Region_IG", "Positions"])

        for idx, (motif_seq, info) in enumerate(global_dict.items(), start=1):
            if info["count"] < count_threshold:
                continue

            mean_ig = float(np.mean(info["ig_scores"])) if info["ig_scores"] else 0.0
            positions = "; ".join(
                f"({position['start']}-{position['end']}, {position['intron_length']})"
                for position in info["positions"]
            )
            writer.writerow([f"motif_{idx}", motif_seq, info["count"], mean_ig, positions])

    print(f"Motif analysis complete: {output_file} (direction={direction})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--direction",
        choices=["pos", "neg"],
        required=True,
        help="pos extracts high positive IG regions; neg extracts high negative IG regions.",
    )
    parser.add_argument("--seq", required=True, help="Sequence CSV from integrated gradients.")
    parser.add_argument("--score", required=True, help="Score CSV from integrated gradients.")
    parser.add_argument("--out", required=True, help="Output motif CSV.")
    parser.add_argument("--min_len", type=int, default=5, help="Minimum motif length.")
    parser.add_argument("--count", type=int, default=3, help="Minimum motif occurrence count.")
    args = parser.parse_args()

    perform_motif_analysis(
        score_file=args.score,
        seq_file=args.seq,
        output_file=args.out,
        direction=args.direction,
        min_motif_len=args.min_len,
        count_threshold=args.count,
    )
