#!/usr/bin/env python3

import csv
import hashlib
import math
import statistics
from pathlib import Path


BASE = Path(r"C:\Users\Yusen Zhang\Documents\eCLIP data finding")
IN_TSV = BASE / "outputs" / "event_count_comparison" / "idiffir_event_counts_classified.tsv"
OUT_DIR = BASE / "outputs" / "event_count_comparison"

ROW_TSV = OUT_DIR / "prediction_pos_both_neg_control_event_counts.tsv"
SUMMARY_TSV = OUT_DIR / "prediction_pos_both_neg_control_event_count_summary.tsv"
PAIRWISE_TSV = OUT_DIR / "prediction_pos_both_neg_vs_control_mannwhitney.tsv"
TEXT_OUT = OUT_DIR / "prediction_pos_both_neg_control_event_count_summary.txt"
PLOT_SVG = OUT_DIR / "prediction_pos_both_neg_control_all_up_down_boxplot.svg"

GROUP_ORDER = ["positive", "positive_and_negative", "negative", "control"]
GROUP_LABEL = {
    "positive": "IR TF/RBP",
    "positive_and_negative": "IR-nonIR TF/RBP",
    "negative": "non-IR TF/RBP",
    "control": "control",
}
PLOT_GROUP_LABEL = {
    "positive": "IR TF/RBP",
    "positive_and_negative": "IR-nonIR TF/RBP",
    "negative": "non-IR TF/RBP",
    "control": "Control",
}
METRICS = ["all_events", "up_events", "down_events"]
METRIC_LABEL = {
    "all_events": "total events",
    "up_events": "up events",
    "down_events": "down events",
}


def read_rows():
    with IN_TSV.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def row_group(row):
    if row["group"] == "control":
        return "control"
    if row["group"] == "prediction" and row["class"] in {"positive", "positive_and_negative", "negative"}:
        return row["class"]
    return ""


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


def make_plot(
    rows,
    title="IR/nonIR TF/RBP classes vs control event counts",
    subtitle="All current prediction and control results are included; ENCODE availability is not used as a filter.",
):
    width, height = 1450, 900
    margin_left, margin_top = 86, 140
    panel_w, panel_h = 405, 265
    col_gap, row_gap = 34, 125
    colors = {
        "positive": "#2563eb",
        "positive_and_negative": "#7c3aed",
        "negative": "#dc2626",
        "control": "#64748b",
    }

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (width, height, width, height),
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111827}.sub{fill:#4b5563}.axis{stroke:#111827;stroke-width:1.1}.grid{stroke:#e5e7eb;stroke-width:1}</style>',
        '<text x="42" y="42" font-size="24" font-weight="700">%s</text>' % svg_escape(title),
        '<text x="42" y="72" font-size="14" class="sub">%s</text>' % svg_escape(subtitle),
    ]

    for row_i, typ in enumerate(["TF", "RBP"]):
        for col_i, metric in enumerate(METRICS):
            x0 = margin_left + col_i * (panel_w + col_gap)
            y0 = margin_top + row_i * (panel_h + row_gap)
            vals_all = [
                int(row[metric])
                for row in rows
                if row["type"] == typ and row["plot_group"] in GROUP_ORDER and row[metric]
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

            for group_i, group in enumerate(GROUP_ORDER):
                subset = [row for row in rows if row["type"] == typ and row["plot_group"] == group and row[metric]]
                vals = sorted(int(row[metric]) for row in subset)
                x = x0 + panel_w * (group_i + 0.5) / len(GROUP_ORDER)
                color = colors[group]
                if vals:
                    q1 = percentile(vals, 0.25)
                    med = percentile(vals, 0.5)
                    q3 = percentile(vals, 0.75)
                    vmin = min(vals)
                    vmax = max(vals)
                    box_w = 40
                    parts.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#111827" stroke-width="1.2"/>' % (x, x, y_pos(vmin), y_pos(vmax)))
                    parts.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#111827" stroke-width="1.2"/>' % (x - 14, x + 14, y_pos(vmin), y_pos(vmin)))
                    parts.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#111827" stroke-width="1.2"/>' % (x - 14, x + 14, y_pos(vmax), y_pos(vmax)))
                    parts.append('<rect x="%.1f" y="%.1f" width="%d" height="%.1f" fill="%s" fill-opacity="0.20" stroke="#111827" stroke-width="1.2"/>' % (x - box_w / 2, y_pos(q3), box_w, max(1, y_pos(q1) - y_pos(q3)), color))
                    parts.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#111827" stroke-width="2"/>' % (x - box_w / 2, x + box_w / 2, y_pos(med), y_pos(med)))
                    for row in subset:
                        value = int(row[metric])
                        px = x + stable_jitter(row["result_dir"] + metric, 30)
                        py = y_pos(value)
                        title = "%s %s: %s" % (row["result_dir"], metric, value)
                        parts.append('<circle cx="%.1f" cy="%.1f" r="3.4" fill="%s" fill-opacity="0.78"><title>%s</title></circle>' % (px, py, color, svg_escape(title)))
                else:
                    parts.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="11" class="sub">no rows</text>' % (x, y0 + panel_h / 2))
                parts.append('<text x="%.1f" y="%d" text-anchor="middle" font-size="11">%s</text>' % (x, y0 + panel_h + 25, PLOT_GROUP_LABEL[group]))
                parts.append('<text x="%.1f" y="%d" text-anchor="middle" font-size="10" class="sub">n=%d</text>' % (x, y0 + panel_h + 43, len(vals)))

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    rows = []
    for row in read_rows():
        group = row_group(row)
        if not group or row["status"] != "ok":
            continue
        out = dict(row)
        out["plot_group"] = group
        out["plot_group_label"] = GROUP_LABEL[group]
        rows.append(out)

    fields = list(rows[0].keys()) if rows else []
    write_tsv(ROW_TSV, rows, fields)

    summary_rows = []
    text_lines = [
        "Prediction classes vs control event counts",
        "All current prediction and control results are included; ENCODE availability is not used as a filter.",
        "Mann-Whitney p-values are normal-approximate.",
        "",
    ]

    for typ in ["TF", "RBP"]:
        text_lines.append("%s:" % typ)
        for group in GROUP_ORDER:
            subset = [row for row in rows if row["type"] == typ and row["plot_group"] == group]
            text_lines.append("  %s:" % GROUP_LABEL[group])
            for metric in METRICS:
                values = [int(row[metric]) for row in subset if row[metric]]
                stats = summarize(values)
                summary_rows.append({
                    "type": typ,
                    "group": group,
                    "group_label": GROUP_LABEL[group],
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
        text_lines.append("")

    pairwise_rows = []
    for typ in ["TF", "RBP"]:
        for metric in METRICS:
            control_vals = [
                int(row[metric])
                for row in rows
                if row["type"] == typ and row["plot_group"] == "control" and row[metric]
            ]
            for group in ["positive", "positive_and_negative", "negative"]:
                group_vals = [
                    int(row[metric])
                    for row in rows
                    if row["type"] == typ and row["plot_group"] == group and row[metric]
                ]
                u, z, p = mann_whitney_approx(group_vals, control_vals)
                pairwise_rows.append({
                    "type": typ,
                    "metric": metric,
                    "prediction_group": group,
                    "prediction_group_label": GROUP_LABEL[group],
                    "prediction_n": len(group_vals),
                    "prediction_median": "%.3f" % statistics.median(group_vals) if group_vals else "",
                    "control_n": len(control_vals),
                    "control_median": "%.3f" % statistics.median(control_vals) if control_vals else "",
                    "prediction_minus_control_median": "%.3f" % (statistics.median(group_vals) - statistics.median(control_vals)) if group_vals and control_vals else "",
                    "mann_whitney_u": u,
                    "mann_whitney_z_approx": z,
                    "mann_whitney_p_approx": p,
                })

    write_tsv(SUMMARY_TSV, summary_rows, ["type", "group", "group_label", "metric", "n", "median", "mean", "min", "max"])
    write_tsv(PAIRWISE_TSV, pairwise_rows, [
        "type",
        "metric",
        "prediction_group",
        "prediction_group_label",
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
    print("Wrote %s" % PAIRWISE_TSV)
    print("Wrote %s" % TEXT_OUT)
    print("Wrote %s" % PLOT_SVG)


if __name__ == "__main__":
    main()
