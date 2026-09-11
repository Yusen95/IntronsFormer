#!/usr/bin/env python3

import csv
import math
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IN_TSV = ROOT / "outputs" / "encode_current_prediction_perturbation_check" / "encode_prediction_vs_control_event_counts.tsv"
OUT_DIR = ROOT / "outputs" / "encode_current_prediction_perturbation_check"

SUMMARY_TSV = OUT_DIR / "cellline_stratified_prediction_control_summary.tsv"
TEST_TSV = OUT_DIR / "cellline_stratified_prediction_control_wilcoxon.tsv"
EXPANDED_TSV = OUT_DIR / "cellline_stratified_prediction_control_rows.tsv"
TEXT_OUT = OUT_DIR / "cellline_stratified_prediction_control_summary.txt"

METRICS = ["all_events", "up_events", "down_events"]
CELL_LINES = ["K562", "HepG2"]


def read_rows():
    with IN_TSV.open(encoding="utf-8-sig", newline="") as handle:
        return [
            row for row in csv.DictReader(handle, delimiter="\t")
            if row["type"] in {"TF", "RBP"} and row["status"] == "ok"
        ]


def write_tsv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


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


def wilcoxon_rank_sum_approx(x, y):
    n1 = len(x)
    n2 = len(y)
    if n1 == 0 or n2 == 0:
        return "", "", "", ""
    values = list(x) + list(y)
    ranks, tie_sizes = rank_values(values)
    w = sum(ranks[:n1])
    u1 = w - n1 * (n1 + 1) / 2.0
    u2 = n1 * n2 - u1
    u = min(u1, u2)
    n = n1 + n2
    tie_term = sum(t ** 3 - t for t in tie_sizes)
    var_u = n1 * n2 / 12.0 * ((n + 1) - tie_term / (n * (n - 1))) if n > 1 else 0
    if var_u <= 0:
        return "%.3f" % w, "%.3f" % u, "", ""
    z = (u - n1 * n2 / 2.0 + 0.5) / math.sqrt(var_u)
    p = math.erfc(abs(z) / math.sqrt(2.0))
    return "%.3f" % w, "%.3f" % u, "%.4g" % z, "%.4g" % p


def summarize(values):
    if not values:
        return {"n": 0, "mean": "", "median": "", "min": "", "max": ""}
    return {
        "n": len(values),
        "mean": "%.3f" % (sum(values) / len(values)),
        "median": "%.3f" % statistics.median(values),
        "min": min(values),
        "max": max(values),
    }


def expand_rows(rows):
    expanded = []

    for row in rows:
        if row["plot_group"] == "control":
            cell = row["cell_line"] if row["cell_line"] in CELL_LINES else "unlabeled"
            out = dict(row)
            out["stratification"] = "explicit"
            out["assigned_cell_line"] = cell
            out["assignment_note"] = "from_cell_line_column"
            expanded.append(out)

            if cell in CELL_LINES:
                out2 = dict(row)
                out2["stratification"] = "encode_support"
                out2["assigned_cell_line"] = cell
                out2["assignment_note"] = "control_from_cell_line_column"
                expanded.append(out2)
            continue

        explicit_cell = row["cell_line"] if row["cell_line"] in CELL_LINES else "unlabeled"
        out = dict(row)
        out["stratification"] = "explicit"
        out["assigned_cell_line"] = explicit_cell
        out["assignment_note"] = "from_cell_line_column" if explicit_cell != "unlabeled" else "cell_line_column_empty"
        expanded.append(out)

        encode_cells = [x for x in row.get("encode_cell_lines", "").split(";") if x in CELL_LINES]
        for cell in encode_cells:
            out2 = dict(row)
            out2["stratification"] = "encode_support"
            out2["assigned_cell_line"] = cell
            out2["assignment_note"] = "from_encode_cell_lines"
            expanded.append(out2)

    return expanded


def main():
    rows = read_rows()
    expanded = expand_rows(rows)

    expanded_fields = list(expanded[0].keys()) if expanded else []
    write_tsv(EXPANDED_TSV, expanded, expanded_fields)

    summary_rows = []
    test_rows = []
    lines = [
        "Cell-line stratified prediction vs control results",
        "explicit = split by local cell_line column; empty cell_line stays unlabeled.",
        "encode_support = prediction split by ENCODE K562/HepG2 support; rows with both supports are counted in both cell lines.",
        "Wilcoxon p-values are unpaired rank-sum normal approximations.",
        "",
    ]

    for mode in ["explicit", "encode_support"]:
        lines.append(mode + ":")
        mode_cells = ["K562", "HepG2", "unlabeled"] if mode == "explicit" else CELL_LINES
        for typ in ["TF", "RBP"]:
            lines.append("  " + typ + ":")
            for cell in mode_cells:
                subset = [
                    row for row in expanded
                    if row["stratification"] == mode
                    and row["type"] == typ
                    and row["assigned_cell_line"] == cell
                ]
                if not subset:
                    continue
                lines.append("    " + cell + ":")
                for group in ["prediction", "control"]:
                    group_rows = [row for row in subset if row["plot_group"] == group]
                    for metric in METRICS:
                        values = [int(row[metric]) for row in group_rows if row[metric]]
                        stats = summarize(values)
                        summary_rows.append({
                            "stratification": mode,
                            "type": typ,
                            "cell_line": cell,
                            "group": group,
                            "metric": metric,
                            "n": stats["n"],
                            "mean": stats["mean"],
                            "median": stats["median"],
                            "min": stats["min"],
                            "max": stats["max"],
                        })
                    if group_rows:
                        total_values = [int(row["all_events"]) for row in group_rows if row["all_events"]]
                        lines.append(
                            "      %s total: n=%d mean=%s median=%s"
                            % (
                                group,
                                len(total_values),
                                "%.3f" % (sum(total_values) / len(total_values)) if total_values else "",
                                "%.3f" % statistics.median(total_values) if total_values else "",
                            )
                        )

                for metric in METRICS:
                    pred = [
                        int(row[metric]) for row in subset
                        if row["plot_group"] == "prediction" and row[metric]
                    ]
                    ctrl = [
                        int(row[metric]) for row in subset
                        if row["plot_group"] == "control" and row[metric]
                    ]
                    w, u, z, p = wilcoxon_rank_sum_approx(pred, ctrl)
                    test_rows.append({
                        "stratification": mode,
                        "type": typ,
                        "cell_line": cell,
                        "metric": metric,
                        "prediction_n": len(pred),
                        "prediction_mean": "%.3f" % (sum(pred) / len(pred)) if pred else "",
                        "prediction_median": "%.3f" % statistics.median(pred) if pred else "",
                        "control_n": len(ctrl),
                        "control_mean": "%.3f" % (sum(ctrl) / len(ctrl)) if ctrl else "",
                        "control_median": "%.3f" % statistics.median(ctrl) if ctrl else "",
                        "wilcoxon_rank_sum_W": w,
                        "mann_whitney_U_min": u,
                        "z_approx": z,
                        "p_value_two_sided_approx": p,
                    })
        lines.append("")

    write_tsv(SUMMARY_TSV, summary_rows, [
        "stratification",
        "type",
        "cell_line",
        "group",
        "metric",
        "n",
        "mean",
        "median",
        "min",
        "max",
    ])
    write_tsv(TEST_TSV, test_rows, [
        "stratification",
        "type",
        "cell_line",
        "metric",
        "prediction_n",
        "prediction_mean",
        "prediction_median",
        "control_n",
        "control_mean",
        "control_median",
        "wilcoxon_rank_sum_W",
        "mann_whitney_U_min",
        "z_approx",
        "p_value_two_sided_approx",
    ])
    TEXT_OUT.write_text("\n".join(lines), encoding="utf-8")

    print("Wrote %s" % EXPANDED_TSV)
    print("Wrote %s" % SUMMARY_TSV)
    print("Wrote %s" % TEST_TSV)
    print("Wrote %s" % TEXT_OUT)


if __name__ == "__main__":
    main()
