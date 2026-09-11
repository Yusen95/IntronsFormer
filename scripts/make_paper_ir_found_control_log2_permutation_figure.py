#!/usr/bin/env python3

from __future__ import annotations

import itertools
import math
from pathlib import Path

import numpy as np
import pandas as pd

from make_publication_ir_ratio_figures import (
    CLASS_COLORS,
    FigureCanvas,
    axis_limits,
    box_stats,
    finite,
)


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "outputs/ir_nonir_ratio_analysis/ir_nonir_ratio_combined_rows.tsv"
OUT_DIR = ROOT / "outputs/ir_nonir_ratio_analysis"
POINTS_OUT = OUT_DIR / "paper_ir_found_control_hepg2_k562_log2_points.tsv"
SUMMARY_OUT = OUT_DIR / "paper_ir_found_control_hepg2_k562_log2_summary.tsv"
FIGURE_SVG_OUT = OUT_DIR / "Figure5.svg"
FIGURE_PNG_OUT = OUT_DIR / "Figure5.png"

CATEGORY_ORDER = ["TF", "RBP"]
CLASS_ORDER = ["positive_only", "control"]
INCLUDED_CELL_LINES = ["HepG2", "K562"]
VALUE_COL = "log2_IR_vs_nonIR_occupancy_ratio"
MAX_EXACT = 100_000
N_MONTE_CARLO = 500_000

class Log2Spec:
    value_col = VALUE_COL
    parity = 0.0
    y_scale = "linear"
    y_label = "log2 IR/nonIR occupancy ratio"


def sig3(value: float) -> str:
    if not np.isfinite(value):
        return "NA"
    return f"{value:.3g}"


def box_stats_min_max(values: np.ndarray) -> dict[str, float] | None:
    values = finite(values)
    if len(values) == 0:
        return None
    q1, median, q3 = np.quantile(values, [0.25, 0.5, 0.75])
    return {
        "q1": float(q1),
        "median": float(median),
        "q3": float(q3),
        "low": float(values.min()),
        "high": float(values.max()),
    }


def class_label(category: str, class_name: str) -> str:
    if class_name == "positive_only":
        return "IR TFs" if category == "TF" else "IR RBPs"
    return f"control {category}s"


def permutation_mean_test(x: np.ndarray, y: np.ndarray, seed: int) -> tuple[float, float, str, int]:
    x = finite(x)
    y = finite(y)
    observed = float(np.mean(x) - np.mean(y))
    pooled = np.concatenate([x, y])
    n_x = len(x)
    total = math.comb(len(pooled), n_x)
    threshold = abs(observed) - 1e-12

    if total <= MAX_EXACT:
        extreme = 0
        for combo in itertools.combinations(range(len(pooled)), n_x):
            mask = np.zeros(len(pooled), dtype=bool)
            mask[list(combo)] = True
            diff = float(np.mean(pooled[mask]) - np.mean(pooled[~mask]))
            if abs(diff) >= threshold:
                extreme += 1
        return observed, extreme / total, "exact", total

    rng = np.random.default_rng(seed)
    extreme = 0
    for _ in range(N_MONTE_CARLO):
        idx = rng.permutation(len(pooled))
        diff = float(np.mean(pooled[idx[:n_x]]) - np.mean(pooled[idx[n_x:]]))
        if abs(diff) >= threshold:
            extreme += 1
    return observed, (extreme + 1) / (N_MONTE_CARLO + 1), "monte_carlo", N_MONTE_CARLO


def prepare_points(df: pd.DataFrame) -> pd.DataFrame:
    points = df[
        (df["Category"].isin(CATEGORY_ORDER))
        & (df["Cell_line"].isin(INCLUDED_CELL_LINES))
        & (df["Class"].isin(CLASS_ORDER))
    ].copy()
    points[VALUE_COL] = pd.to_numeric(points[VALUE_COL], errors="coerce")
    points["raw_occupancy_ratio"] = pd.to_numeric(points["raw_occupancy_ratio"], errors="coerce")
    points = points[points[VALUE_COL].replace([np.inf, -np.inf], np.nan).notna()].copy()
    points["Class_label"] = [class_label(row.Category, row.Class) for row in points.itertuples()]
    columns = [
        "Category",
        "Cell_line",
        "Class",
        "Class_label",
        "Original_ID",
        "Target",
        "Experiment",
        "raw_occupancy_ratio",
        VALUE_COL,
    ]
    return points[columns].copy()


def summarize(points: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for category_i, category in enumerate(CATEGORY_ORDER):
        panel = points[points["Category"] == category]
        positive = finite(panel.loc[panel["Class"] == "positive_only", VALUE_COL])
        control = finite(panel.loc[panel["Class"] == "control", VALUE_COL])
        diff, p_value, method, n_perm = permutation_mean_test(positive, control, 20260625 + category_i)

        for class_name in CLASS_ORDER:
            values = finite(panel.loc[panel["Class"] == class_name, VALUE_COL])
            box = box_stats_min_max(values)
            rows.append(
                {
                    "Category": category,
                    "Class": class_name,
                    "Class_label": class_label(category, class_name),
                    "n": len(values),
                    "mean_log2_ratio": float(np.mean(values)) if len(values) else np.nan,
                    "sd_log2_ratio": float(np.std(values, ddof=1)) if len(values) > 1 else np.nan,
                    "sem_log2_ratio": float(np.std(values, ddof=1) / math.sqrt(len(values))) if len(values) > 1 else np.nan,
                    "q1_log2_ratio": box["q1"] if box else np.nan,
                    "median_log2_ratio": box["median"] if box else np.nan,
                    "q3_log2_ratio": box["q3"] if box else np.nan,
                    "whisker_low_log2_ratio": box["low"] if box else np.nan,
                    "whisker_high_log2_ratio": box["high"] if box else np.nan,
                    "mean_difference_ir_found_minus_control": diff,
                    "permutation_p_value_mean_difference_two_sided": p_value,
                    "permutation_method": method,
                    "permutations": n_perm,
                }
            )
    return pd.DataFrame(rows)


def render(
    points: pd.DataFrame,
    summary: pd.DataFrame,
    categories: list[str],
    svg_out: Path,
    png_out: Path,
) -> tuple[Path, Path]:
    spec = Log2Spec()
    panel_w = 455
    panel_h = 350
    left = 70
    right = 20
    top = 52
    bottom = 82
    legend_w = 60
    width = panel_w * len(categories) + (legend_w if len(categories) > 1 else 0)
    height = panel_h + 25

    values = finite(points[VALUE_COL])
    y_low, y_high, y_ticks = axis_limits(values, spec)
    y_high += (y_high - y_low) * 0.16

    def y_map(value: float, plot_y: float, plot_h: float) -> float:
        return plot_y + plot_h - (value - y_low) / (y_high - y_low) * plot_h

    canvas = FigureCanvas(width, height)
    rng = np.random.default_rng(67)

    panel_letters = {"TF": "(a)", "RBP": "(b)"}
    for panel_i, category in enumerate(categories):
        x0 = panel_i * panel_w
        y0 = 18
        plot_x = x0 + left
        plot_y = y0 + top
        plot_w = panel_w - left - right
        plot_h = panel_h - top - bottom
        panel = points[points["Category"] == category].copy()

        canvas.rect(x0 + 10, y0 + 8, x0 + panel_w - 10, y0 + panel_h - 8, "#FFFFFF", stroke="#D1D5DB")
        canvas.text(x0 + 20, y0 + 28, panel_letters[category], 11, anchor="start", bold=True)
        canvas.text(x0 + panel_w / 2, y0 + 28, category, 13, bold=True)

        for tick in y_ticks:
            if y_low <= tick <= y_high:
                ty = y_map(tick, plot_y, plot_h)
                canvas.line(plot_x, ty, plot_x + plot_w, ty, "#E5E7EB", width=0.8)
                canvas.text(plot_x - 8, ty + 3, f"{tick:g}", 9, anchor="end", fill="#4B5563")
        parity_y = y_map(0.0, plot_y, plot_h)
        canvas.line(plot_x, parity_y, plot_x + plot_w, parity_y, "#111111", width=1, dash=(4, 3))
        canvas.line(plot_x, plot_y + plot_h, plot_x + plot_w, plot_y + plot_h, "#111827")
        canvas.line(plot_x, plot_y, plot_x, plot_y + plot_h, "#111827")

        group_step = plot_w / len(CLASS_ORDER)
        centers: dict[str, float] = {}
        for group_i, class_name in enumerate(CLASS_ORDER):
            group = panel[panel["Class"] == class_name]
            group_values = finite(group[VALUE_COL])
            cx = plot_x + group_step * (group_i + 0.5)
            centers[class_name] = cx
            color = CLASS_COLORS[class_name]
            label = class_label(category, class_name)
            if len(group_values) == 0:
                canvas.text(cx, plot_y + plot_h / 2, "NA", 10, fill="#9CA3AF")
                continue

            box = box_stats_min_max(group_values)
            assert box is not None
            mean_value = float(np.mean(group_values))
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

            for _, point in group.iterrows():
                value = float(point[VALUE_COL])
                if not np.isfinite(value):
                    continue
                jitter = float(rng.normal(0, 6.0))
                canvas.circle(
                    cx + jitter,
                    y_map(value, plot_y, plot_h),
                    3.4,
                    color,
                    stroke="#FFFFFF",
                    width=0.9,
                    opacity=0.82,
                )
            canvas.text(cx, mean_y - 6, sig3(mean_value), 8, fill="#111111", bold=True)
            canvas.text(cx, plot_y + plot_h + 20, label, 9, anchor="middle")

        test_row = summary[(summary["Category"] == category) & (summary["Class"] == "positive_only")]
        if not test_row.empty:
            x1, x2 = centers["positive_only"], centers["control"]
            bracket_y = plot_y + 16
            tick_h = 7
            p_value = float(test_row.iloc[0]["permutation_p_value_mean_difference_two_sided"])
            canvas.line(x1, bracket_y + tick_h, x1, bracket_y, "#111111", width=1)
            canvas.line(x1, bracket_y, x2, bracket_y, "#111111", width=1)
            canvas.line(x2, bracket_y, x2, bracket_y + tick_h, "#111111", width=1)
            canvas.text(
                (x1 + x2) / 2,
                bracket_y - 5,
                f"Permutation p={sig3(p_value)}",
                9,
                anchor="middle",
                bold=True,
            )

        if len(categories) == 1 or panel_i == 0:
            canvas.text(x0 + 18, plot_y + plot_h / 2, spec.y_label, 10, rotate=-90)

    canvas.save(svg_out, png_out)
    return svg_out, png_out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT, sep="\t")
    points = prepare_points(df)
    summary = summarize(points)
    points.to_csv(POINTS_OUT, sep="\t", index=False)
    summary.to_csv(SUMMARY_OUT, sep="\t", index=False)
    svg, png = render(points, summary, CATEGORY_ORDER, FIGURE_SVG_OUT, FIGURE_PNG_OUT)
    print(svg)
    print(png)
    print(POINTS_OUT)
    print(SUMMARY_OUT)


if __name__ == "__main__":
    main()
