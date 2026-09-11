#!/usr/bin/env python3

from __future__ import annotations

import csv
import argparse
import hashlib
import math
import statistics
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DOWNLOADS = BASE / "metadata/knockdown"

COUNTS_TSV = DOWNLOADS / "idiffir_all_result_event_counts.tsv"
POS_TF = DOWNLOADS / "Pos_TF.tsv"
NEG_TF = DOWNLOADS / "Neg_TF.tsv"
POS_RBP = DOWNLOADS / "Pos_RBP.tsv"
NEG_RBP = DOWNLOADS / "Neg_RBP.tsv"

OUT_DIR = BASE / "outputs" / "event_count_comparison"
CLASSIFIED_TSV = OUT_DIR / "idiffir_event_counts_classified.tsv"
SUMMARY_TSV = OUT_DIR / "idiffir_event_count_group_summary.tsv"
PLOT_SVG = OUT_DIR / "idiffir_event_count_prediction_vs_control.svg"

TF_CONTROL_RUN_IDS = {
    "USF1_K562",
    "SRF_K562",
    "FOXM1_K562",
    "MITF_K562",
    "NFATC1_K562",
    "STAT6_K562",
    "STAT1_K562",
    "NFE2L1_K562",
    "BACH1_K562",
    "RELA_K562",
    "LIN28B_K562",
    "HSF1_K562",
    "GATA2_K562",
    "NFYB_K562",
    "USF2_K562",
}

RBP_CONTROL_RUN_IDS = {
    "ACO1_HepG2",
    "EIF4B_K562",
    "FUS_HepG2",
    "FXR1_K562",
    "G3BP2_HepG2",
    "HNRNPK_HepG2",
    "RBM3_K562",
    "TARDBP_HepG2",
}

RBP_ALIASES = {
    "A2BP1": "RBFOX1",
    "CSDA": "YBX3",
    "YB-1": "YBX1",
    "BRUNOL4": "CELF4",
    "BRUNOL5": "CELF5",
    "BRUNOL6": "CELF6",
    "FUSIP1": "SRSF10",
    "HNRNPDL": "HNRPDL",
}


def norm_tf(name: str) -> str:
    return name.strip().upper()


def norm_rbp(name: str) -> str:
    upper = name.strip().upper()
    return RBP_ALIASES.get(upper, upper)


def read_target_set(path: Path, normalizer) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not reader.fieldnames or "Target_ID" not in reader.fieldnames:
            raise ValueError(f"Missing Target_ID in {path}")
        return {normalizer(row["Target_ID"]) for row in reader if row.get("Target_ID", "").strip()}


def classify(row: dict, tf_pos: set[str], tf_neg: set[str], rbp_pos: set[str], rbp_neg: set[str]) -> tuple[str, str, str, str]:
    target = row["target"]
    run_id = row["run_id"]
    tf_target = norm_tf(target)
    rbp_target = norm_rbp(target)
    notes = []

    in_tf_pos = tf_target in tf_pos
    in_tf_neg = tf_target in tf_neg
    in_rbp_pos = rbp_target in rbp_pos
    in_rbp_neg = rbp_target in rbp_neg

    if in_tf_pos and in_tf_neg:
        notes.append("tf_in_both_pos_neg")
    if in_rbp_pos and in_rbp_neg:
        notes.append("rbp_in_both_pos_neg")

    if run_id in TF_CONTROL_RUN_IDS:
        if in_tf_pos or in_tf_neg:
            notes.append("tf_control_also_in_prediction")
        return "TF", "control", "random_tf_control", ";".join(notes)

    if in_tf_pos or in_tf_neg:
        label = "positive_and_negative" if in_tf_pos and in_tf_neg else ("positive" if in_tf_pos else "negative")
        return "TF", "prediction", label, ";".join(notes)

    if run_id in RBP_CONTROL_RUN_IDS:
        if in_rbp_pos or in_rbp_neg:
            notes.append("rbp_control_also_in_prediction")
        return "RBP", "control", "random_rbp_control", ";".join(notes)

    if in_rbp_pos or in_rbp_neg:
        label = "positive_and_negative" if in_rbp_pos and in_rbp_neg else ("positive" if in_rbp_pos else "negative")
        return "RBP", "prediction", label, ";".join(notes)

    return "", "", "", ""


def to_int(value: str) -> int | None:
    value = str(value).strip()
    return int(value) if value else None


def median(values: list[int]) -> float:
    return float(statistics.median(values)) if values else float("nan")


def summarize(rows: list[dict]) -> list[dict]:
    summaries = []
    groups = sorted({(row["type"], row["group"]) for row in rows if row["status"] == "ok"})
    for typ, group in groups:
        subset = [row for row in rows if row["type"] == typ and row["group"] == group and row["status"] == "ok"]
        for metric in ["all_events", "up_events", "down_events"]:
            vals = [int(row[metric]) for row in subset]
            summaries.append({
                "type": typ,
                "group": group,
                "metric": metric,
                "n": len(vals),
                "median": f"{median(vals):.3f}" if vals else "",
                "mean": f"{sum(vals) / len(vals):.3f}" if vals else "",
                "min": min(vals) if vals else "",
                "max": max(vals) if vals else "",
            })
    return summaries


def stable_jitter(key: str, width: float = 42.0) -> float:
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    value = int(digest[:8], 16) / 0xFFFFFFFF
    return (value - 0.5) * width


def svg_plot(rows: list[dict]) -> str:
    plot_rows = [
        row for row in rows
        if row["status"] == "ok" and row["type"] in {"TF", "RBP"} and row["group"] in {"prediction", "control"}
    ]
    categories = [
        ("TF", "prediction", "TF prediction"),
        ("TF", "control", "TF control"),
        ("RBP", "prediction", "RBP prediction"),
        ("RBP", "control", "RBP control"),
    ]

    vals = [math.log10(int(row["all_events"]) + 1) for row in plot_rows]
    y_min = 0
    y_max = max(vals) if vals else 1
    y_max = math.ceil(y_max * 10) / 10

    width = 980
    height = 620
    left = 90
    right = 40
    top = 50
    bottom = 120
    plot_w = width - left - right
    plot_h = height - top - bottom
    x_positions = [left + plot_w * (i + 0.5) / len(categories) for i in range(len(categories))]

    def y_pos(log_value: float) -> float:
        return top + plot_h * (1 - (log_value - y_min) / (y_max - y_min if y_max > y_min else 1))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111827} .axis{stroke:#111827;stroke-width:1.2} .grid{stroke:#e5e7eb;stroke-width:1}</style>',
        f'<text x="{left}" y="28" font-size="18" font-weight="700">Significant differential IR events after knockdown</text>',
    ]

    tick = 0.0
    while tick <= y_max + 1e-9:
        y = y_pos(tick)
        parts.append(f'<line class="grid" x1="{left}" x2="{width - right}" y1="{y:.1f}" y2="{y:.1f}"/>')
        parts.append(f'<text x="{left - 12}" y="{y + 4:.1f}" text-anchor="end" font-size="12">{tick:.1f}</text>')
        tick += 0.5

    parts.append(f'<line class="axis" x1="{left}" x2="{left}" y1="{top}" y2="{height - bottom}"/>')
    parts.append(f'<line class="axis" x1="{left}" x2="{width - right}" y1="{height - bottom}" y2="{height - bottom}"/>')
    parts.append(f'<text transform="translate(24 {top + plot_h / 2}) rotate(-90)" font-size="13" text-anchor="middle">log10(total events + 1)</text>')

    colors = {
        ("TF", "prediction"): "#2563eb",
        ("TF", "control"): "#94a3b8",
        ("RBP", "prediction"): "#dc2626",
        ("RBP", "control"): "#f59e0b",
    }

    for i, (typ, group, label) in enumerate(categories):
        x = x_positions[i]
        subset = [row for row in plot_rows if row["type"] == typ and row["group"] == group]
        values = [int(row["all_events"]) for row in subset]
        for row in subset:
            lx = x + stable_jitter(row["result_dir"])
            ly = y_pos(math.log10(int(row["all_events"]) + 1))
            title = f'{row["result_dir"]}: {row["all_events"]} events'
            parts.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="5.2" fill="{colors[(typ, group)]}" fill-opacity="0.78"><title>{title}</title></circle>')
        if values:
            med = median(values)
            my = y_pos(math.log10(med + 1))
            parts.append(f'<line x1="{x - 45:.1f}" x2="{x + 45:.1f}" y1="{my:.1f}" y2="{my:.1f}" stroke="#111827" stroke-width="3"/>')
            parts.append(f'<text x="{x:.1f}" y="{my - 10:.1f}" text-anchor="middle" font-size="12" font-weight="700">median {med:.0f}</text>')
        parts.append(f'<text x="{x:.1f}" y="{height - bottom + 30}" text-anchor="middle" font-size="13">{label}</text>')
        parts.append(f'<text x="{x:.1f}" y="{height - bottom + 49}" text-anchor="middle" font-size="12" fill="#4b5563">n={len(values)}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    global POS_TF, NEG_TF, POS_RBP, NEG_RBP, COUNTS_TSV
    global OUT_DIR, CLASSIFIED_TSV, SUMMARY_TSV, PLOT_SVG
    parser = argparse.ArgumentParser(description="Classify counts using explicitly selected historical candidate lists.")
    parser.add_argument("--candidate-dir", type=Path, required=True,
                        help="Directory with Pos_TF.tsv, Neg_TF.tsv, Pos_RBP.tsv, Neg_RBP.tsv (Target_ID column).")
    parser.add_argument("--counts", type=Path, default=COUNTS_TSV)
    parser.add_argument("--out-dir", type=Path, default=BASE / "outputs/classification_rebuild")
    args = parser.parse_args()
    POS_TF, NEG_TF, POS_RBP, NEG_RBP = [args.candidate_dir / name for name in
        ("Pos_TF.tsv", "Neg_TF.tsv", "Pos_RBP.tsv", "Neg_RBP.tsv")]
    COUNTS_TSV, OUT_DIR = args.counts, args.out_dir
    CLASSIFIED_TSV = OUT_DIR / "idiffir_event_counts_classified.tsv"
    SUMMARY_TSV = OUT_DIR / "idiffir_event_count_group_summary.tsv"
    PLOT_SVG = OUT_DIR / "idiffir_event_count_prediction_vs_control.svg"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    tf_pos = read_target_set(POS_TF, norm_tf)
    tf_neg = read_target_set(NEG_TF, norm_tf)
    rbp_pos = read_target_set(POS_RBP, norm_rbp)
    rbp_neg = read_target_set(NEG_RBP, norm_rbp)

    output_rows = []
    with COUNTS_TSV.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            typ, group, klass, note = classify(row, tf_pos, tf_neg, rbp_pos, rbp_neg)
            if not group:
                continue
            output_rows.append({
                "type": typ,
                "group": group,
                "class": klass,
                "target": row["target"],
                "cell_line": row["cell_line"],
                "run_id": row["run_id"],
                "result_dir": row["result_dir"],
                "all_events": row["all_events"],
                "up_events": row["up_events"],
                "down_events": row["down_events"],
                "status": row["status"],
                "note": note,
            })

    fields = ["type", "group", "class", "target", "cell_line", "run_id", "result_dir", "all_events", "up_events", "down_events", "status", "note"]
    with CLASSIFIED_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)

    summary_rows = summarize(output_rows)
    with SUMMARY_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=["type", "group", "metric", "n", "median", "mean", "min", "max"])
        writer.writeheader()
        writer.writerows(summary_rows)

    PLOT_SVG.write_text(svg_plot(output_rows), encoding="utf-8")

    print(f"Wrote {CLASSIFIED_TSV}")
    print(f"Wrote {SUMMARY_TSV}")
    print(f"Wrote {PLOT_SVG}")
    for key in [("TF", "prediction"), ("TF", "control"), ("RBP", "prediction"), ("RBP", "control")]:
        n = sum(1 for row in output_rows if row["type"] == key[0] and row["group"] == key[1] and row["status"] == "ok")
        print(f"{key[0]} {key[1]} ok rows: {n}")
    missing = [row for row in output_rows if row["status"] != "ok"]
    if missing:
        print("Rows needing check:")
        for row in missing:
            print(f"  {row['run_id']} {row['status']}")


if __name__ == "__main__":
    main()
