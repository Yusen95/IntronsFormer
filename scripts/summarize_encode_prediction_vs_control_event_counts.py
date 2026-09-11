#!/usr/bin/env python3

import csv
import argparse
import hashlib
import math
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COUNTS_TSV = ROOT / "outputs" / "event_count_comparison" / "idiffir_event_counts_classified.tsv"
ENCODE_SUPPORTED_TSV = (
    ROOT
    / "outputs"
    / "encode_current_prediction_perturbation_check"
    / "current_prediction_results_with_encode_perturbation_K562_or_HepG2.tsv"
)
OUT_DIR = ROOT / "outputs" / "encode_current_prediction_perturbation_check"

ROW_TSV = OUT_DIR / "encode_prediction_vs_control_event_counts.tsv"
SUMMARY_TSV = OUT_DIR / "encode_prediction_vs_control_event_count_summary.tsv"
TEST_TSV = OUT_DIR / "encode_prediction_vs_control_mannwhitney.tsv"
TEXT_OUT = OUT_DIR / "encode_prediction_vs_control_event_count_summary.txt"
PLOT_SVG = OUT_DIR / "encode_prediction_vs_control_all_up_down_boxplot.svg"

METRICS = ["all_events", "up_events", "down_events"]
METRIC_LABEL = {
    "all_events": "total events",
    "up_events": "up events",
    "down_events": "down events",
}


def read_tsv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def summarize(values):
    if not values:
        return {"n": 0, "median": "", "mean": "", "min": "", "max": ""}
    return {
        "n": len(values),
        "median": "%.3f" % statistics.median(values),
        "mean": "%.3f" % (sum(values) / len(values)),
        "min": min(values),
        "max": max(values),
    }


def rank_values(values):
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * len(values)
    tie_sizes = []
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        tie_sizes.append(j - i)
        i = j
    return ranks, tie_sizes


def mann_whitney_approx(x, y):
    n1 = len(x)
    n2 = len(y)
    if n1 == 0 or n2 == 0:
        return "", "", ""
    values = list(x) + list(y)
    ranks, tie_sizes = rank_values(values)
    rank_sum_x = sum(ranks[:n1])
    u1 = rank_sum_x - n1 * (n1 + 1) / 2.0
    u2 = n1 * n2 - u1
    u = min(u1, u2)
    mean_u = n1 * n2 / 2.0
    n = n1 + n2
    tie_term = sum(t ** 3 - t for t in tie_sizes)
    var_u = n1 * n2 / 12.0 * ((n + 1) - tie_term / (n * (n - 1))) if n > 1 else 0
    if var_u <= 0:
        return "%.3f" % u, "", ""
    z = (u - mean_u + 0.5) / math.sqrt(var_u)
    p = math.erfc(abs(z) / math.sqrt(2.0))
    return "%.3f" % u, "%.4g" % z, "%.4g" % p


def percentile(values, p):
    xs = sorted(values)
    k = (len(xs) - 1) * p
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return float(xs[int(k)])
    return xs[lo] * (hi - k) + xs[hi] * (k - lo)


def stable_jitter(key, width):
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    value = int(digest[:8], 16) / 0xFFFFFFFF
    return (value - 0.5) * width


def svg_escape(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_plot(rows):
    width, height = 1320, 900
    margin_left, margin_top = 82, 140
    panel_w, panel_h = 370, 265
    col_gap, row_gap = 48, 125
    colors = {
        ("TF", "prediction"): "#2563eb",
        ("TF", "control"): "#64748b",
        ("RBP", "prediction"): "#dc2626",
        ("RBP", "control"): "#f59e0b",
    }

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (width, height, width, height),
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111827}.sub{fill:#4b5563}.axis{stroke:#111827;stroke-width:1.1}.grid{stroke:#e5e7eb;stroke-width:1}</style>',
        '<text x="42" y="42" font-size="24" font-weight="700">ENCODE-filtered prediction vs control</text>',
        '<text x="42" y="72" font-size="14" class="sub">Prediction targets require ENCODE perturbation RNA-seq support in K562/HepG2; controls are K562/HepG2 rows.</text>',
    ]

    for row_i, typ in enumerate(["TF", "RBP"]):
        for col_i, metric in enumerate(METRICS):
            x0 = margin_left + col_i * (panel_w + col_gap)
            y0 = margin_top + row_i * (panel_h + row_gap)
            vals_all = [
                int(row[metric])
                for row in rows
                if row["type"] == typ and row[metric]
            ]
            ymax = int(math.ceil((max(vals_all) if vals_all else 1) / 100.0) * 100)
            ymax = max(ymax, 100)

            def y_pos(value):
                return y0 + panel_h * (1 - value / ymax)

            parts.append('<text x="%d" y="%d" font-size="16" font-weight="700">%s: %s</text>' % (x0, y0 - 26, typ, METRIC_LABEL[metric]))
            tick_step = max(50, int(ymax / 4))
            tick = 0
            while tick <= ymax:
                y = y_pos(tick)
                parts.append('<line class="grid" x1="%d" x2="%d" y1="%.1f" y2="%.1f"/>' % (x0, x0 + panel_w, y, y))
                parts.append('<text x="%d" y="%.1f" text-anchor="end" font-size="10" class="sub">%d</text>' % (x0 - 8, y + 3, tick))
                tick += tick_step
            parts.append('<line class="axis" x1="%d" x2="%d" y1="%d" y2="%d"/>' % (x0, x0, y0, y0 + panel_h))
            parts.append('<line class="axis" x1="%d" x2="%d" y1="%d" y2="%d"/>' % (x0, x0 + panel_w, y0 + panel_h, y0 + panel_h))

            for group_i, group in enumerate(["prediction", "control"]):
                subset = [row for row in rows if row["type"] == typ and row["plot_group"] == group and row[metric]]
                vals = sorted(int(row[metric]) for row in subset)
                x = x0 + panel_w * (group_i + 0.5) / 2
                color = colors[(typ, group)]
                if vals:
                    q1 = percentile(vals, 0.25)
                    med = percentile(vals, 0.5)
                    q3 = percentile(vals, 0.75)
                    vmin = min(vals)
                    vmax = max(vals)
                    box_w = 52
                    parts.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#111827" stroke-width="1.2"/>' % (x, x, y_pos(vmin), y_pos(vmax)))
                    parts.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#111827" stroke-width="1.2"/>' % (x - 16, x + 16, y_pos(vmin), y_pos(vmin)))
                    parts.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#111827" stroke-width="1.2"/>' % (x - 16, x + 16, y_pos(vmax), y_pos(vmax)))
                    parts.append('<rect x="%.1f" y="%.1f" width="%d" height="%.1f" fill="%s" fill-opacity="0.20" stroke="#111827" stroke-width="1.2"/>' % (x - box_w / 2, y_pos(q3), box_w, max(1, y_pos(q1) - y_pos(q3)), color))
                    parts.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#111827" stroke-width="2"/>' % (x - box_w / 2, x + box_w / 2, y_pos(med), y_pos(med)))
                    for row in subset:
                        value = int(row[metric])
                        px = x + stable_jitter(row["result_dir"] + metric, 36)
                        py = y_pos(value)
                        title = "%s %s: %s" % (row["result_dir"], metric, value)
                        parts.append('<circle cx="%.1f" cy="%.1f" r="3.8" fill="%s" fill-opacity="0.78"><title>%s</title></circle>' % (px, py, color, svg_escape(title)))
                else:
                    parts.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="11" class="sub">no rows</text>' % (x, y0 + panel_h / 2))
                label = "Prediction" if group == "prediction" else "Control"
                parts.append('<text x="%.1f" y="%d" text-anchor="middle" font-size="11">%s</text>' % (x, y0 + panel_h + 25, label))
                parts.append('<text x="%.1f" y="%d" text-anchor="middle" font-size="10" class="sub">n=%d</text>' % (x, y0 + panel_h + 43, len(vals)))

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    global COUNTS_TSV, ENCODE_SUPPORTED_TSV, OUT_DIR, ROW_TSV, SUMMARY_TSV, TEST_TSV, TEXT_OUT, PLOT_SVG
    parser = argparse.ArgumentParser(description="Filter classified counts using an ENCODE-support TSV.")
    parser.add_argument("--counts", type=Path, default=COUNTS_TSV)
    parser.add_argument("--support", type=Path, default=ENCODE_SUPPORTED_TSV)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()
    COUNTS_TSV, ENCODE_SUPPORTED_TSV, OUT_DIR = args.counts, args.support, args.out_dir
    for path in (COUNTS_TSV, ENCODE_SUPPORTED_TSV):
        if not path.is_file():
            parser.error(f"Missing input table: {path}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ROW_TSV = OUT_DIR / ROW_TSV.name
    SUMMARY_TSV = OUT_DIR / SUMMARY_TSV.name
    TEST_TSV = OUT_DIR / TEST_TSV.name
    TEXT_OUT = OUT_DIR / TEXT_OUT.name
    PLOT_SVG = OUT_DIR / PLOT_SVG.name
    counts = read_tsv(COUNTS_TSV)
    support_by_result_dir = {
        row["result_dir"]: row
        for row in read_tsv(ENCODE_SUPPORTED_TSV)
        if row["has_encode_perturbation_K562_or_HepG2"] == "yes"
    }
    supported_result_dirs = set(support_by_result_dir)

    rows = []
    for row in counts:
        if row["status"] != "ok":
            continue
        if row["group"] == "prediction":
            if row["result_dir"] not in supported_result_dirs:
                continue
            out = dict(row)
            out["plot_group"] = "prediction"
            support = support_by_result_dir[row["result_dir"]]
            out["encode_cell_lines"] = support.get("encode_cell_lines", "")
            out["encode_assays"] = support.get("encode_assays", "")
            out["encode_accessions"] = support.get("encode_accessions", "")
            rows.append(out)
        elif row["group"] == "control" and row["cell_line"] in {"K562", "HepG2"}:
            out = dict(row)
            out["plot_group"] = "control"
            out["encode_cell_lines"] = ""
            out["encode_assays"] = ""
            out["encode_accessions"] = ""
            rows.append(out)

    write_tsv(ROW_TSV, rows, list(rows[0].keys()) if rows else [])

    summary_rows = []
    test_rows = []
    text_lines = [
        "ENCODE-filtered prediction vs control event counts",
        "Prediction targets require ENCODE shRNA/siRNA/CRISPR/CRISPRi RNA-seq support in K562 or HepG2.",
        "Controls are K562/HepG2 rows. Mann-Whitney p-values are normal-approximate.",
        "",
    ]

    for typ in ["TF", "RBP"]:
        text_lines.append("%s:" % typ)
        for group in ["prediction", "control"]:
            subset = [row for row in rows if row["type"] == typ and row["plot_group"] == group]
            text_lines.append("  %s:" % ("prediction" if group == "prediction" else "control"))
            for metric in METRICS:
                values = [int(row[metric]) for row in subset if row[metric]]
                stats = summarize(values)
                summary_rows.append({
                    "type": typ,
                    "group": group,
                    "metric": metric,
                    "n": stats["n"],
                    "median": stats["median"],
                    "mean": stats["mean"],
                    "min": stats["min"],
                    "max": stats["max"],
                })
                text_lines.append(
                    "    %s: n=%s median=%s mean=%s min=%s max=%s"
                    % (metric, stats["n"], stats["median"], stats["mean"], stats["min"], stats["max"])
                )

        for metric in METRICS:
            pred = [int(row[metric]) for row in rows if row["type"] == typ and row["plot_group"] == "prediction" and row[metric]]
            ctrl = [int(row[metric]) for row in rows if row["type"] == typ and row["plot_group"] == "control" and row[metric]]
            u, z, p = mann_whitney_approx(pred, ctrl)
            test_rows.append({
                "type": typ,
                "metric": metric,
                "prediction_n": len(pred),
                "prediction_median": "%.3f" % statistics.median(pred) if pred else "",
                "control_n": len(ctrl),
                "control_median": "%.3f" % statistics.median(ctrl) if ctrl else "",
                "prediction_minus_control_median": "%.3f" % (statistics.median(pred) - statistics.median(ctrl)) if pred and ctrl else "",
                "mann_whitney_u": u,
                "mann_whitney_z_approx": z,
                "mann_whitney_p_approx": p,
            })
        text_lines.append("")

    write_tsv(SUMMARY_TSV, summary_rows, ["type", "group", "metric", "n", "median", "mean", "min", "max"])
    write_tsv(TEST_TSV, test_rows, [
        "type",
        "metric",
        "prediction_n",
        "prediction_median",
        "control_n",
        "control_median",
        "prediction_minus_control_median",
        "mann_whitney_u",
        "mann_whitney_z_approx",
        "mann_whitney_p_approx",
    ])
    TEXT_OUT.write_text("\n".join(text_lines), encoding="utf-8")
    PLOT_SVG.write_text(make_plot(rows), encoding="utf-8")

    print("Wrote %s" % ROW_TSV)
    print("Wrote %s" % SUMMARY_TSV)
    print("Wrote %s" % TEST_TSV)
    print("Wrote %s" % TEXT_OUT)
    print("Wrote %s" % PLOT_SVG)


if __name__ == "__main__":
    main()
