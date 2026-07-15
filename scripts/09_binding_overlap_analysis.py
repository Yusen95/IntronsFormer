#!/usr/bin/env python3

import argparse
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact


CELL_LINES = ["HepG2", "K562", "GM12878"]
ATTR_RE = re.compile(r'(\S+) "([^"]+)"')


def parse_args():
    parser = argparse.ArgumentParser(
        description="Baseline-like ChIP/eCLIP overlap using gene-body and pre-exon/intron/post-exon event loci."
    )
    parser.add_argument("--base_dir", default=os.path.expanduser("~/bigdata"))
    parser.add_argument("--gtf", default=None)
    parser.add_argument(
        "--selected_tsv",
        default=None,
        help="encode_selected_peaks_three_class.tsv copied to HPCC",
    )
    parser.add_argument("--out_dir", default=None)
    parser.add_argument(
        "--allow_existing_fallback",
        action="store_true",
        help="Use any existing narrowPeak in the target/cell folder if selected accession is missing.",
    )
    parser.add_argument(
        "--exclude_first_intron",
        action="store_true",
        help="Exclude events whose intron is the first intron of any matching transcript.",
    )
    parser.add_argument(
        "--match_nonir_relative_position",
        action="store_true",
        help="Use a nonIR population matched to IR relative position within genes.",
    )
    parser.add_argument(
        "--relative_position_bins",
        type=int,
        default=20,
        help="Number of relative-position bins for nonIR matching. Default 20 gives 0.05-wide bins.",
    )
    parser.add_argument(
        "--nonir_matches_per_ir",
        type=int,
        default=1,
        help="Number of nonIR events to keep per IR event within each relative-position bin.",
    )
    parser.add_argument(
        "--length_adjust_nonir",
        action="store_true",
        help="Filter nonIR events per cell line to intron length < mean(IR length) + N * sd(IR length).",
    )
    parser.add_argument(
        "--length_adjust_sd_multiplier",
        type=float,
        default=1.0,
        help="Standard-deviation multiplier for --length_adjust_nonir. Baseline code uses 1.0.",
    )
    parser.add_argument(
        "--start_in_gene_filter",
        action="store_true",
        help="Only count overlaps where peak start is in gene for + strand, or peak end is in gene for - strand.",
    )
    return parser.parse_args()


def normalize_chrom(value):
    value = str(value).strip()
    return value[3:] if value.startswith("chr") else value


def parse_attrs(attr_text):
    return dict(ATTR_RE.findall(attr_text))


def load_gtf(gtf_path):
    gene_body = {}
    exons_by_gene = {}

    print(f"[INFO] Loading GTF: {gtf_path}")
    with open(gtf_path, "r") as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 9:
                continue

            chrom, _, feature, start, end, _, strand, _, attrs = cols
            if feature not in {"gene", "exon"}:
                continue

            attr = parse_attrs(attrs)
            gene_id = attr.get("gene_id", "").split(".")[0]
            if not gene_id:
                continue

            chrom = normalize_chrom(chrom)
            start = int(start)
            end = int(end)

            if feature == "gene":
                current = gene_body.get(gene_id)
                if current is None:
                    gene_body[gene_id] = {
                        "chrom": chrom,
                        "start": start,
                        "end": end,
                        "strand": strand,
                        "gene_name": attr.get("gene_name", ""),
                    }
                else:
                    current["start"] = min(current["start"], start)
                    current["end"] = max(current["end"], end)
                continue

            transcript_id = attr.get("transcript_id", "")
            if not transcript_id:
                continue
            exons_by_gene.setdefault(gene_id, {}).setdefault(transcript_id, []).append((start, end))

    for transcripts in exons_by_gene.values():
        for transcript_id, exons in transcripts.items():
            transcripts[transcript_id] = sorted(set(exons))

    print(f"[INFO] Loaded {len(gene_body)} genes and {len(exons_by_gene)} genes with exons")
    return gene_body, exons_by_gene


def extract_gene_id(name):
    parts = str(name).split("/")
    if len(parts) >= 2:
        return parts[1].split(".")[0]
    return ""


def transcript_intron_number(pair_index, exon_count, strand):
    if strand == "-":
        return exon_count - pair_index - 1
    return pair_index + 1


def relative_gene_position(midpoint0, gene_start0, gene_end0, strand):
    gene_len = max(gene_end0 - gene_start0, 1)
    if strand == "-":
        pos = (gene_end0 - midpoint0) / gene_len
    else:
        pos = (midpoint0 - gene_start0) / gene_len
    return float(np.clip(pos, 0, 1))


def find_flanking_exons(gene_id, intron_start, intron_end, exons_by_gene, strand):
    transcripts = exons_by_gene.get(gene_id)
    if not transcripts:
        return None, None, "no_exons", False, "", 0, 0

    best_fallback = None
    best_distance = None
    exact_candidates = []

    for transcript_id, exons in transcripts.items():
        for i in range(len(exons) - 1):
            left = exons[i]
            right = exons[i + 1]
            expected_start = left[1] + 1
            expected_end = right[0] - 1
            intron_number = transcript_intron_number(i, len(exons), strand)
            intron_count = len(exons) - 1
            is_first_intron = intron_number == 1

            if expected_start == intron_start and expected_end == intron_end:
                exact_candidates.append(
                    (left, right, "exact", is_first_intron, transcript_id, intron_number, intron_count)
                )
                continue

            if left[1] < intron_start and right[0] > intron_end:
                distance = abs(expected_start - intron_start) + abs(expected_end - intron_end)
                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_fallback = (
                        left,
                        right,
                        "nearest",
                        is_first_intron,
                        transcript_id,
                        intron_number,
                        intron_count,
                    )

    if exact_candidates:
        chosen = exact_candidates[0]
        is_first_intron = any(candidate[3] for candidate in exact_candidates)
        return chosen[0], chosen[1], chosen[2], is_first_intron, chosen[4], chosen[5], chosen[6]
    if best_fallback is not None:
        return best_fallback

    return None, None, "no_flanking_exons", False, "", 0, 0


def annotate_events(bed_path, gene_body, exons_by_gene, exclude_first_intron=False):
    raw = pd.read_csv(
        bed_path,
        sep="\t",
        header=None,
        usecols=[0, 1, 2, 3, 4, 5],
        names=["chrom", "start", "end", "name", "score", "strand"],
        low_memory=False,
    )
    raw["chrom"] = raw["chrom"].map(normalize_chrom)
    raw["start"] = pd.to_numeric(raw["start"], errors="coerce")
    raw["end"] = pd.to_numeric(raw["end"], errors="coerce")
    raw = raw.dropna(subset=["chrom", "start", "end"]).copy()
    raw["start"] = raw["start"].astype(int)
    raw["end"] = raw["end"].astype(int)
    raw["gene_id"] = raw["name"].map(extract_gene_id)

    rows = []
    skipped_first_intron = 0
    for row in raw.itertuples(index=False):
        gene = gene_body.get(row.gene_id)
        if gene is None:
            continue
        if normalize_chrom(gene["chrom"]) != row.chrom:
            continue

        pre_exon, post_exon, status, is_first_intron, transcript_id, intron_number, intron_count = find_flanking_exons(
            row.gene_id,
            int(row.start),
            int(row.end),
            exons_by_gene,
            gene["strand"],
        )
        if pre_exon is None or post_exon is None:
            continue
        if exclude_first_intron and is_first_intron:
            skipped_first_intron += 1
            continue

        # IRFinder/GTF coordinates are treated as 1-based inclusive.
        # ENCODE BED peaks are 0-based half-open, so convert event coordinates here.
        intron_start0 = int(row.start) - 1
        intron_end0 = int(row.end)
        pre_start0 = pre_exon[0] - 1
        pre_end0 = pre_exon[1]
        post_start0 = post_exon[0] - 1
        post_end0 = post_exon[1]
        event_start0 = min(pre_start0, intron_start0, post_start0)
        event_end0 = max(pre_end0, intron_end0, post_end0)
        gene_start0 = gene["start"] - 1
        gene_end0 = gene["end"]
        intron_midpoint0 = (intron_start0 + intron_end0) / 2
        event_midpoint0 = (event_start0 + event_end0) / 2
        intron_length = intron_end0 - intron_start0
        event_region_length = event_end0 - event_start0
        intron_relative_position = relative_gene_position(
            intron_midpoint0, gene_start0, gene_end0, gene["strand"]
        )
        event_relative_position = relative_gene_position(
            event_midpoint0, gene_start0, gene_end0, gene["strand"]
        )

        rows.append({
            "chrom": row.chrom,
            "gene_id": row.gene_id,
            "name": row.name,
            "strand": row.strand,
            "gene_start0": gene_start0,
            "gene_end0": gene_end0,
            "pre_start0": pre_start0,
            "pre_end0": pre_end0,
            "intron_start0": intron_start0,
            "intron_end0": intron_end0,
            "post_start0": post_start0,
            "post_end0": post_end0,
            "event_start0": event_start0,
            "event_end0": event_end0,
            "intron_length": intron_length,
            "event_region_length": event_region_length,
            "intron_midpoint0": intron_midpoint0,
            "event_midpoint0": event_midpoint0,
            "intron_relative_position": intron_relative_position,
            "event_relative_position": event_relative_position,
            "annotation_status": status,
            "is_first_intron": is_first_intron,
            "matched_transcript_id": transcript_id,
            "matched_transcript_intron_number": intron_number,
            "matched_transcript_intron_count": intron_count,
        })

    annotated = pd.DataFrame(rows)
    print(
        f"[INFO] Annotated {len(annotated)} / {len(raw)} events from {bed_path}"
    )
    if not annotated.empty:
        counts = annotated["annotation_status"].value_counts().to_dict()
        print(f"[INFO] Annotation status: {counts}")
    if exclude_first_intron:
        print(f"[INFO] Excluded first-intron events: {skipped_first_intron}")
    return annotated


def length_adjust_nonir(ir_events, nonir_events, sd_multiplier, label):
    if ir_events.empty or nonir_events.empty:
        return nonir_events.copy(), np.nan

    ir_lengths = ir_events["intron_length"].to_numpy(dtype=float)
    max_len = float(np.mean(ir_lengths) + sd_multiplier * np.std(ir_lengths))
    adjusted = nonir_events[nonir_events["intron_length"] < max_len].copy()
    print(
        f"[INFO] {label}: length-adjusted nonIR events "
        f"{len(adjusted)} / {len(nonir_events)} "
        f"max_intron_length={max_len:.2f} "
        f"(mean_IR + {sd_multiplier}*sd_IR)"
    )
    return adjusted.reset_index(drop=True), max_len


def position_bins(events, bins):
    values = events["intron_relative_position"].to_numpy(dtype=float)
    values = np.clip(values, 0, np.nextafter(1, 0))
    return np.floor(values * bins).astype(int)


def match_nonir_by_relative_position(ir_events, nonir_events, bins, matches_per_ir, label):
    if bins <= 0:
        raise ValueError("--relative_position_bins must be positive")
    if matches_per_ir <= 0:
        raise ValueError("--nonir_matches_per_ir must be positive")
    if ir_events.empty or nonir_events.empty:
        return nonir_events.copy()

    ir_bins = position_bins(ir_events, bins)
    nonir = nonir_events.copy()
    nonir["_relative_position_bin"] = position_bins(nonir, bins)

    selected = []
    requested = 0
    for bin_id in range(bins):
        ir_count = int((ir_bins == bin_id).sum())
        keep_count = ir_count * matches_per_ir
        if keep_count == 0:
            continue

        candidates = nonir[nonir["_relative_position_bin"] == bin_id].sort_values(
            ["intron_relative_position", "gene_id", "intron_start0", "intron_end0"]
        )
        requested += keep_count
        if candidates.empty:
            continue
        if len(candidates) <= keep_count:
            selected.append(candidates)
            continue

        # Deterministic downsampling across the bin keeps the nonIR distribution spread out.
        take = np.linspace(0, len(candidates) - 1, keep_count, dtype=int)
        selected.append(candidates.iloc[take])

    if not selected:
        print(f"[WARN] {label}: no matched nonIR events found; using all nonIR events")
        return nonir_events.copy()

    matched = pd.concat(selected, ignore_index=True)
    matched = matched.drop(columns=["_relative_position_bin"])
    print(
        f"[INFO] {label}: relative-position matched nonIR events "
        f"{len(matched)} / {len(nonir_events)} requested={requested} "
        f"bins={bins} matches_per_ir={matches_per_ir}"
    )
    return matched.reset_index(drop=True)


def read_peak_bed(path):
    peaks = pd.read_csv(
        path,
        sep="\t",
        header=None,
        usecols=[0, 1, 2],
        names=["chrom", "start", "end"],
        low_memory=False,
    )
    peaks["chrom"] = peaks["chrom"].map(normalize_chrom)
    peaks["start"] = pd.to_numeric(peaks["start"], errors="coerce")
    peaks["end"] = pd.to_numeric(peaks["end"], errors="coerce")
    peaks = peaks.dropna(subset=["chrom", "start", "end"]).copy()
    peaks["start"] = peaks["start"].astype(int)
    peaks["end"] = peaks["end"].astype(int)
    peaks = peaks[peaks["end"] > peaks["start"]]

    index = {}
    for chrom, sub in peaks.groupby("chrom", sort=False):
        starts_raw = sub["start"].to_numpy(dtype=np.int64)
        ends_raw = sub["end"].to_numpy(dtype=np.int64)
        start_order = np.argsort(starts_raw, kind="mergesort")
        end_order = np.argsort(ends_raw, kind="mergesort")
        index[chrom] = {
            "starts_sorted": starts_raw[start_order],
            "ends_sorted": np.sort(ends_raw),
            "ends_by_start": ends_raw[start_order],
            "ends_by_end": ends_raw[end_order],
            "starts_by_end": starts_raw[end_order],
        }
    return index


def count_interval_overlaps(starts, ends, interval_starts, interval_ends):
    # Half-open overlap: peak_start < interval_end and peak_end > interval_start.
    starts_before_end = np.searchsorted(starts, interval_ends, side="left")
    ends_before_or_at_start = np.searchsorted(ends, interval_starts, side="right")
    counts = starts_before_end - ends_before_or_at_start
    counts[counts < 0] = 0
    return counts


def add_overlap_counts(events, peak_index, start_col, end_col, out_col):
    counts = np.zeros(len(events), dtype=np.int64)
    if events.empty:
        return counts

    for chrom, idx in events.groupby("chrom", sort=False).groups.items():
        if chrom not in peak_index:
            continue
        starts = peak_index[chrom]["starts_sorted"]
        ends = peak_index[chrom]["ends_sorted"]
        idx_arr = np.asarray(list(idx), dtype=np.int64)
        interval_starts = events.loc[idx_arr, start_col].to_numpy(dtype=np.int64)
        interval_ends = events.loc[idx_arr, end_col].to_numpy(dtype=np.int64)
        counts[idx_arr] = count_interval_overlaps(starts, ends, interval_starts, interval_ends)

    return counts


def add_start_in_gene_overlap_counts(events, peak_index, start_col, end_col, out_col):
    counts = np.zeros(len(events), dtype=np.int64)
    if events.empty:
        return counts

    for chrom, idx in events.groupby("chrom", sort=False).groups.items():
        if chrom not in peak_index:
            continue

        peak_data = peak_index[chrom]
        starts_sorted = peak_data["starts_sorted"]
        ends_by_start = peak_data["ends_by_start"]
        ends_by_end = peak_data["ends_by_end"]
        starts_by_end = peak_data["starts_by_end"]

        for event_idx in idx:
            event = events.loc[event_idx]
            event_start = int(event[start_col])
            event_end = int(event[end_col])
            gene_start = int(event["gene_start0"])
            gene_end = int(event["gene_end0"])

            if event["strand"] == "-":
                lower = max(event_start, gene_start)
                lo = np.searchsorted(ends_by_end, lower, side="right")
                hi = np.searchsorted(ends_by_end, gene_end, side="right")
                if hi > lo:
                    counts[event_idx] = int((starts_by_end[lo:hi] < event_end).sum())
            else:
                upper = min(event_end, gene_end)
                lo = np.searchsorted(starts_sorted, gene_start, side="left")
                hi = np.searchsorted(starts_sorted, upper, side="left")
                if hi > lo:
                    counts[event_idx] = int((ends_by_start[lo:hi] > event_start).sum())

    return counts


def assay_prefix(category):
    return "ChIP-seq" if category == "TF" else "eCLIP"


def find_peak_file(base_dir, row, allow_existing_fallback=False):
    dirs = [base_dir / f"{assay_prefix(row['Category'])}_{row['Cell_Line']}" / row["ENCODE_Target"]]
    if row["Category"] == "RBP":
        dirs.append(base_dir / f"ChIP-seq_{row['Cell_Line']}" / row["ENCODE_Target"])

    for target_dir in dirs:
        matches = sorted(target_dir.glob(f"*_{row['Selected_File']}_*.narrowPeak.bed"))
        if matches:
            return matches[0]

    if allow_existing_fallback:
        for target_dir in dirs:
            matches = sorted(target_dir.glob("*.narrowPeak.bed"))
            if matches:
                print(
                    f"[WARN] Using existing non-selected file for {row['Category']} "
                    f"{row['ENCODE_Target']} {row['Cell_Line']}: {matches[0]}"
                )
                return matches[0]

    raise FileNotFoundError(
        f"Missing selected peak {row['Selected_File']} in: {', '.join(str(d) for d in dirs)}"
    )


def fisher_summary(ir_yes, ir_total, nonir_yes, nonir_total):
    table = [[ir_yes, ir_total - ir_yes], [nonir_yes, nonir_total - nonir_yes]]
    odds, pvalue = fisher_exact(table)
    return odds, pvalue


def summarize_pair(row, peak_file, ir_events, nonir_events, start_in_gene_filter=False):
    peak_index = read_peak_bed(peak_file)

    overlap_counter = add_start_in_gene_overlap_counts if start_in_gene_filter else add_overlap_counts

    ir_event_counts = overlap_counter(ir_events, peak_index, "event_start0", "event_end0", "event_peak_count")
    nonir_event_counts = overlap_counter(nonir_events, peak_index, "event_start0", "event_end0", "event_peak_count")
    ir_intron_counts = overlap_counter(ir_events, peak_index, "intron_start0", "intron_end0", "intron_peak_count")
    nonir_intron_counts = overlap_counter(nonir_events, peak_index, "intron_start0", "intron_end0", "intron_peak_count")

    ir_event_yes = int((ir_event_counts > 0).sum())
    nonir_event_yes = int((nonir_event_counts > 0).sum())
    ir_intron_yes = int((ir_intron_counts > 0).sum())
    nonir_intron_yes = int((nonir_intron_counts > 0).sum())
    ir_total = len(ir_events)
    nonir_total = len(nonir_events)

    event_odds, event_p = fisher_summary(ir_event_yes, ir_total, nonir_event_yes, nonir_total)
    intron_odds, intron_p = fisher_summary(ir_intron_yes, ir_total, nonir_intron_yes, nonir_total)

    return {
        "Class": row["Class"],
        "Category": row["Category"],
        "Assay": row["Assay"],
        "Cell_line": row["Cell_Line"],
        "Original_ID": row["Original_ID"],
        "Target": row["ENCODE_Target"],
        "Experiment": row["Experiment"],
        "Peak_accession": row["Selected_File"],
        "Peak_file": str(peak_file),
        "start_in_gene_filter": "yes" if start_in_gene_filter else "no",
        "IR_total_annotated": ir_total,
        "NonIR_total_annotated": nonir_total,
        "IR_event_region_overlap": ir_event_yes,
        "NonIR_event_region_overlap": nonir_event_yes,
        "IR_event_region_occupancy_%": ir_event_yes / ir_total * 100 if ir_total else 0,
        "NonIR_event_region_occupancy_%": nonir_event_yes / nonir_total * 100 if nonir_total else 0,
        "event_region_peak_event_count_IR": int(ir_event_counts.sum()),
        "event_region_peak_event_count_NonIR": int(nonir_event_counts.sum()),
        "event_region_odds_ratio": event_odds,
        "event_region_fisher_p_value": event_p,
        "IR_intron_only_overlap": ir_intron_yes,
        "NonIR_intron_only_overlap": nonir_intron_yes,
        "IR_intron_only_occupancy_%": ir_intron_yes / ir_total * 100 if ir_total else 0,
        "NonIR_intron_only_occupancy_%": nonir_intron_yes / nonir_total * 100 if nonir_total else 0,
        "intron_only_peak_event_count_IR": int(ir_intron_counts.sum()),
        "intron_only_peak_event_count_NonIR": int(nonir_intron_counts.sum()),
        "intron_only_odds_ratio": intron_odds,
        "intron_only_fisher_p_value": intron_p,
    }


def event_paths(base_dir, cell_line):
    return (
        base_dir / "Project1" / "IRevent" / f"{cell_line}IR_results.bed",
        base_dir / "Project1" / "nonIRevent" / f"{cell_line}nonIR_results.bed",
    )


def main():
    args = parse_args()
    base_dir = Path(args.base_dir)
    gtf = Path(args.gtf) if args.gtf else base_dir / "Homo_sapiens.GRCh38.111.gtf"
    selected_tsv = Path(args.selected_tsv) if args.selected_tsv else base_dir / "encode_selected_peaks_three_class.tsv"
    out_dir = Path(args.out_dir) if args.out_dir else base_dir / "baseline_like_overlap_three_class"
    out_dir.mkdir(parents=True, exist_ok=True)

    selected = pd.read_csv(selected_tsv, sep="\t")
    selected = selected[selected["Cell_Line"].isin(CELL_LINES)].copy()

    gene_body, exons_by_gene = load_gtf(gtf)

    events_by_cell = {}
    for cell_line in CELL_LINES:
        ir_bed, nonir_bed = event_paths(base_dir, cell_line)
        if not ir_bed.exists() or not nonir_bed.exists():
            raise FileNotFoundError(f"Missing event BED for {cell_line}: {ir_bed}, {nonir_bed}")

        ir_events = annotate_events(ir_bed, gene_body, exons_by_gene, args.exclude_first_intron)
        nonir_events_all = annotate_events(nonir_bed, gene_body, exons_by_gene, args.exclude_first_intron)
        nonir_events_all.to_csv(
            out_dir / f"{cell_line}_nonIR_baseline_like_annotated_events_all.tsv",
            sep="\t",
            index=False,
        )

        nonir_events = nonir_events_all
        if args.length_adjust_nonir:
            nonir_events, max_len = length_adjust_nonir(
                ir_events,
                nonir_events,
                args.length_adjust_sd_multiplier,
                cell_line,
            )
            nonir_events["length_adjust_max_intron_length"] = max_len
            nonir_active_name = f"{cell_line}_nonIR_baseline_like_annotated_events_length_adjusted.tsv"
        else:
            nonir_active_name = f"{cell_line}_nonIR_baseline_like_annotated_events.tsv"

        if args.match_nonir_relative_position:
            nonir_events = match_nonir_by_relative_position(
                ir_events,
                nonir_events,
                args.relative_position_bins,
                args.nonir_matches_per_ir,
                cell_line,
            )
            nonir_active_name = f"{cell_line}_nonIR_baseline_like_annotated_events_matched.tsv"

        ir_events.to_csv(out_dir / f"{cell_line}_IR_baseline_like_annotated_events.tsv", sep="\t", index=False)
        nonir_events.to_csv(out_dir / nonir_active_name, sep="\t", index=False)
        events_by_cell[cell_line] = (ir_events, nonir_events)

    results = []
    skipped = []
    for row in selected.to_dict("records"):
        cell_line = row["Cell_Line"]
        print(f"[INFO] {row['Class']} {row['Category']} {row['ENCODE_Target']} {cell_line} {row['Selected_File']}")
        try:
            peak_file = find_peak_file(base_dir, row, args.allow_existing_fallback)
            ir_events, nonir_events = events_by_cell[cell_line]
            results.append(summarize_pair(row, peak_file, ir_events, nonir_events, args.start_in_gene_filter))
        except FileNotFoundError as exc:
            print(f"[WARN] skipped: {exc}")
            skipped.append({**row, "Reason": str(exc)})

    if not results:
        raise SystemExit("No overlap results generated.")

    summary = pd.DataFrame(results)
    summary_out = out_dir / "baseline_like_overlap_three_class_summary.tsv"
    summary.to_csv(summary_out, sep="\t", index=False)
    print(f"[INFO] Saved {summary_out}")

    if skipped:
        skipped_out = out_dir / "baseline_like_overlap_skipped.tsv"
        pd.DataFrame(skipped).to_csv(skipped_out, sep="\t", index=False)
        print(f"[INFO] Saved {skipped_out}")


if __name__ == "__main__":
    main()
