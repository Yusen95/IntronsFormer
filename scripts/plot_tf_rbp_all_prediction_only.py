from itertools import combinations
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

from make_publication_ir_ratio_figures import (
    CLASS_COLORS,
    FigureCanvas,
    finite,
    nice_ticks,
)


ROOT = Path(__file__).resolve().parents[1]
TF_INPUT = (
    ROOT
    / "outputs"
    / "encode_current_prediction_perturbation_check"
    / "encode_prediction_vs_control_event_counts.tsv"
)
RBP_INPUT = ROOT / "outputs" / "event_count_comparison" / "prediction_pos_both_neg_control_event_counts.tsv"
OUT_DIR = ROOT / "outputs" / "direction_specific_original_counts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_PERMUTATIONS = 200000
SEED = 20260701
FIGURE_SVG_OUT = OUT_DIR / "Figure7.svg"
FIGURE_PNG_OUT = OUT_DIR / "Figure7.png"


def exact_permutation(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    pooled = np.concatenate([a, b])
    n_a = len(a)
    observed = a.mean() - b.mean()
    diffs = []
    for combo_idx in combinations(range(len(pooled)), n_a):
        mask = np.zeros(len(pooled), dtype=bool)
        mask[list(combo_idx)] = True
        diffs.append(pooled[mask].mean() - pooled[~mask].mean())
    diffs = np.asarray(diffs)
    return {
        "observed_mean_diff": observed,
        "n_permutations": len(diffs),
        "permutation_mode": "exact",
        "p_two_sided": (np.abs(diffs) >= abs(observed) - 1e-12).mean(),
    }


def monte_carlo_permutation(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    pooled = np.concatenate([a, b])
    n_a = len(a)
    observed = a.mean() - b.mean()
    rng = np.random.default_rng(SEED)
    diffs = np.empty(N_PERMUTATIONS, dtype=float)
    for i in range(N_PERMUTATIONS):
        shuffled = rng.permutation(pooled)
        diffs[i] = shuffled[:n_a].mean() - shuffled[n_a:].mean()
    return {
        "observed_mean_diff": observed,
        "n_permutations": N_PERMUTATIONS,
        "permutation_mode": "monte_carlo",
        "random_seed": SEED,
        "p_two_sided": ((np.abs(diffs) >= abs(observed) - 1e-12).sum() + 1) / (N_PERMUTATIONS + 1),
    }


def permutation_test(a, b):
    total = len(a) + len(b)
    n_choose = min(len(a), len(b))
    if comb(total, n_choose) <= 200000:
        return exact_permutation(a, b)
    return monte_carlo_permutation(a, b)


def build_data(df, factor_type):
    factor = df[(df["type"] == factor_type) & (df["status"] == "ok")].copy()
    rows = []
    for group_name, subset in [
        ("prediction", factor[factor["group"] == "prediction"]),
        ("control", factor[factor["group"] == "control"]),
    ]:
        for _, row in subset.iterrows():
            rows.append(
                {
                    "type": factor_type,
                    "group": group_name,
                    "target": row["target"],
                    "cell_line": row.get("cell_line", ""),
                    "run_id": row["run_id"],
                    "result_dir": row["result_dir"],
                    "all_events": float(row["all_events"]),
                }
            )
    return pd.DataFrame(rows)


def run_stats(data, factor_type):
    pred_vals = data[data["group"] == "prediction"]["all_events"].dropna().to_numpy(dtype=float)
    ctrl_vals = data[data["group"] == "control"]["all_events"].dropna().to_numpy(dtype=float)
    perm = permutation_test(pred_vals, ctrl_vals)
    return {
        "type": factor_type,
        "panel": f"All {factor_type} prediction",
        "metric": "all_events",
        "prediction_n": len(pred_vals),
        "prediction_mean": pred_vals.mean() if len(pred_vals) else np.nan,
        "prediction_median": np.median(pred_vals) if len(pred_vals) else np.nan,
        "control_n": len(ctrl_vals),
        "control_mean": ctrl_vals.mean() if len(ctrl_vals) else np.nan,
        "control_median": np.median(ctrl_vals) if len(ctrl_vals) else np.nan,
        **perm,
    }


def box_stats_min_max(values):
    values = finite(values)
    q1, q3 = np.quantile(values, [0.25, 0.75])
    return {
        "q1": float(q1),
        "q3": float(q3),
        "low": float(values.min()),
        "high": float(values.max()),
    }


def sig3(value):
    return f"{float(value):.3g}"


def group_label(factor_type, group):
    if group == "prediction":
        return f"{factor_type} candidates"
    return f"control {factor_type}s"


def draw_panels(data, stats, factor_types, svg_out, png_out):
    panel_w = 455
    panel_h = 350
    left = 70
    right = 20
    top = 52
    bottom = 82
    legend_w = 60
    width = panel_w * len(factor_types) + (legend_w if len(factor_types) > 1 else 0)
    height = panel_h + 25

    max_value = max(float(data["all_events"].max()), 1.0)
    ticks = nice_ticks(0.0, max_value * 1.16, count=7)
    y_low = 0.0
    y_high = max(ticks)

    def y_map(value, plot_y, plot_h):
        return plot_y + plot_h - (float(value) - y_low) / (y_high - y_low) * plot_h

    canvas = FigureCanvas(width, height)
    rng = np.random.default_rng(67)
    panel_letters = {"TF": "(a)", "RBP": "(b)"}
    colors = {
        "prediction": CLASS_COLORS["positive_only"],
        "control": CLASS_COLORS["control"],
    }

    for panel_i, factor_type in enumerate(factor_types):
        x0 = panel_i * panel_w
        y0 = 18
        plot_x = x0 + left
        plot_y = y0 + top
        plot_w = panel_w - left - right
        plot_h = panel_h - top - bottom
        panel = data[data["type"] == factor_type]

        canvas.rect(
            x0 + 10,
            y0 + 8,
            x0 + panel_w - 10,
            y0 + panel_h - 8,
            "#FFFFFF",
            stroke="#D1D5DB",
        )
        canvas.text(x0 + 20, y0 + 28, panel_letters[factor_type], 11, anchor="start", bold=True)
        canvas.text(x0 + panel_w / 2, y0 + 28, factor_type, 13, bold=True)

        for tick in ticks:
            if y_low <= tick <= y_high:
                ty = y_map(tick, plot_y, plot_h)
                canvas.line(plot_x, ty, plot_x + plot_w, ty, "#E5E7EB", width=0.8)
                canvas.text(plot_x - 8, ty + 3, f"{tick:g}", 9, anchor="end", fill="#4B5563")
        canvas.line(plot_x, plot_y + plot_h, plot_x + plot_w, plot_y + plot_h, "#111827")
        canvas.line(plot_x, plot_y, plot_x, plot_y + plot_h, "#111827")

        group_step = plot_w / 2
        centers = {}
        for group_i, group in enumerate(["prediction", "control"]):
            values = finite(panel.loc[panel["group"] == group, "all_events"])
            cx = plot_x + group_step * (group_i + 0.5)
            centers[group] = cx
            color = colors[group]
            box = box_stats_min_max(values)
            mean_value = float(np.mean(values))
            box_w = min(46, group_step * 0.42)
            q1_y = y_map(box["q1"], plot_y, plot_h)
            q3_y = y_map(box["q3"], plot_y, plot_h)
            mean_y = y_map(mean_value, plot_y, plot_h)
            low_y = y_map(box["low"], plot_y, plot_h)
            high_y = y_map(box["high"], plot_y, plot_h)

            canvas.line(cx, high_y, cx, low_y, color, width=1.5)
            canvas.line(cx - box_w / 3, high_y, cx + box_w / 3, high_y, color, width=1.5)
            canvas.line(cx - box_w / 3, low_y, cx + box_w / 3, low_y, color, width=1.5)
            canvas.rect(
                cx - box_w / 2,
                min(q1_y, q3_y),
                cx + box_w / 2,
                max(q1_y, q3_y),
                color,
                stroke=color,
                opacity=0.28,
                width=1.2,
            )
            canvas.line(cx - box_w / 2, mean_y, cx + box_w / 2, mean_y, "#111111", width=1.8)

            for value in values:
                canvas.circle(
                    cx + float(rng.normal(0, 6.0)),
                    y_map(value, plot_y, plot_h),
                    3.4,
                    color,
                    stroke="#FFFFFF",
                    width=0.9,
                    opacity=0.82,
                )
            canvas.text(cx, mean_y - 6, sig3(mean_value), 8, fill="#111111", bold=True)
            canvas.text(cx, plot_y + plot_h + 20, group_label(factor_type, group), 9)

        stat = stats[stats["type"] == factor_type].iloc[0]
        x1, x2 = centers["prediction"], centers["control"]
        bracket_y = plot_y + 16
        tick_h = 7
        canvas.line(x1, bracket_y + tick_h, x1, bracket_y, "#111111", width=1)
        canvas.line(x1, bracket_y, x2, bracket_y, "#111111", width=1)
        canvas.line(x2, bracket_y, x2, bracket_y + tick_h, "#111111", width=1)
        canvas.text(
            (x1 + x2) / 2,
            bracket_y - 5,
            f"Permutation p={sig3(stat['p_two_sided'])}",
            9,
            bold=True,
        )

        if len(factor_types) == 1 or panel_i == 0:
            canvas.text(
                x0 + 18,
                plot_y + plot_h / 2,
                "Differential IR event count",
                10,
                rotate=-90,
            )

    canvas.save(svg_out, png_out)
    return svg_out, png_out


def main():
    all_data = []
    stats = []
    for factor_type, input_path in [("TF", TF_INPUT), ("RBP", RBP_INPUT)]:
        df = pd.read_csv(input_path, sep="\t").fillna("")
        data = build_data(df, factor_type)
        stat = run_stats(data, factor_type)
        all_data.append(data)
        stats.append(stat)
        data.to_csv(OUT_DIR / f"{factor_type.lower()}_all_prediction_only_event_counts.tsv", sep="\t", index=False)
        pd.DataFrame([stat]).to_csv(OUT_DIR / f"{factor_type.lower()}_all_prediction_only_stats.tsv", sep="\t", index=False)

    combined_data = pd.concat(all_data, ignore_index=True)
    combined_stats = pd.DataFrame(stats)
    combined_data.to_csv(
        OUT_DIR / "tf_rbp_all_prediction_only_event_counts.tsv", sep="\t", index=False
    )
    combined_stats.to_csv(OUT_DIR / "tf_rbp_all_prediction_only_stats.tsv", sep="\t", index=False)
    svg, png = draw_panels(
        combined_data,
        combined_stats,
        ["TF", "RBP"],
        FIGURE_SVG_OUT,
        FIGURE_PNG_OUT,
    )
    print(f"Wrote {svg}")
    print(f"Wrote {png}")
    print(combined_stats[["type", "prediction_n", "prediction_mean", "control_n", "control_mean", "p_two_sided"]].to_string(index=False))


if __name__ == "__main__":
    main()
