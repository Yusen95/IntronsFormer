#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import math
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from scipy.stats import kruskal, mannwhitneyu, spearmanr
except ImportError:  # pragma: no cover - HPCC environment is expected to have scipy.
    kruskal = None
    mannwhitneyu = None
    spearmanr = None


CLASS_ORDER = ["positive_only", "both", "negative_only", "neutral_only", "control"]
CATEGORY_ORDER = ["TF", "RBP"]
CELL_LINE_ORDER = ["HepG2", "K562", "GM12878"]

CLASS_COLORS = {
    "positive_only": "#4C78A8",
    "both": "#59A14F",
    "negative_only": "#E15759",
    "neutral_only": "#B07AA1",
    "control": "#9C755F",
}
CLASS_LABELS = {
    "positive_only": "IR TF/RBP",
    "both": "IR-nonIR TF/RBP",
    "negative_only": "non-IR TF/RBP",
    "neutral_only": "neutral",
    "control": "control",
}
RANK_SOURCE_LABELS = {
    "positive": "IR",
    "negative": "non-IR",
}

METRICS = {
    "event_region": {
        "label": "event region",
        "ir_overlap": "IR_event_region_overlap",
        "nonir_overlap": "NonIR_event_region_overlap",
        "ir_occupancy": "IR_event_region_occupancy_%",
        "nonir_occupancy": "NonIR_event_region_occupancy_%",
        "p_value": "event_region_fisher_p_value",
        "odds_ratio": "event_region_odds_ratio",
    },
    "intron_only": {
        "label": "intron only",
        "ir_overlap": "IR_intron_only_overlap",
        "nonir_overlap": "NonIR_intron_only_overlap",
        "ir_occupancy": "IR_intron_only_occupancy_%",
        "nonir_occupancy": "NonIR_intron_only_occupancy_%",
        "p_value": "intron_only_fisher_p_value",
        "odds_ratio": "intron_only_odds_ratio",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare IR vs nonIR occupancy ratios across candidate classes and "
            "optionally test candidate rank versus occupancy ratio."
        )
    )
    parser.add_argument(
        "--summary",
        action="append",
        required=True,
        help=(
            "baseline_like_overlap_three_class_summary.tsv. Repeat for candidate "
            "and control summaries."
        ),
    )
    parser.add_argument(
        "--out_dir",
        default="ir_nonir_ratio_analysis",
        help="Output directory for tables and plots.",
    )
    parser.add_argument(
        "--metric",
        choices=sorted(METRICS),
        default="event_region",
        help="Occupancy metric to compare.",
    )
    parser.add_argument(
        "--pseudocount",
        type=float,
        default=0.5,
        help=(
            "Haldane-style pseudocount for corrected occupancy rates. "
            "Default 0.5 handles zero-overlap rows."
        ),
    )
    parser.add_argument("--positive_tf", default=None, help="Original positive TF TSV/CSV.")
    parser.add_argument("--negative_tf", default=None, help="Original negative TF TSV/CSV.")
    parser.add_argument("--positive_rbp", default=None, help="Original positive RBP TSV/CSV.")
    parser.add_argument("--negative_rbp", default=None, help="Original negative RBP TSV/CSV.")
    parser.add_argument(
        "--rank_xscale",
        choices=["linear", "log"],
        default="linear",
        help="X-axis scale for rank scatter plots.",
    )
    return parser.parse_args()


def normalize_key(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def class_sort_key(class_name: str) -> tuple[int, str]:
    try:
        return (CLASS_ORDER.index(class_name), class_name)
    except ValueError:
        return (len(CLASS_ORDER), class_name)


def bh_adjust(pvalues: pd.Series) -> pd.Series:
    values = pd.to_numeric(pvalues, errors="coerce")
    adjusted = pd.Series(np.nan, index=values.index, dtype=float)
    valid = values.dropna()
    if valid.empty:
        return adjusted

    order = valid.sort_values().index
    sorted_p = valid.loc[order].to_numpy(dtype=float)
    m = len(sorted_p)
    ranks = np.arange(1, m + 1, dtype=float)
    raw = sorted_p * m / ranks
    monotone = np.minimum.accumulate(raw[::-1])[::-1]
    monotone = np.clip(monotone, 0, 1)
    adjusted.loc[order] = monotone
    return adjusted


def get_pyplot():
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[WARN] matplotlib is not available; skipping plot files.", file=sys.stderr)
        return None
    return plt


def require_columns(df: pd.DataFrame, columns: list[str], path: Path) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"{path} is missing required columns: {', '.join(missing)}")


def read_summary(path_text: str, metric: str, pseudocount: float) -> pd.DataFrame:
    path = Path(path_text)
    if not path.exists():
        raise FileNotFoundError(path)

    spec = METRICS[metric]
    df = pd.read_csv(path, sep="\t")
    required = [
        "Class",
        "Category",
        "Cell_line",
        "Original_ID",
        "Target",
        "IR_total_annotated",
        "NonIR_total_annotated",
        spec["ir_overlap"],
        spec["nonir_overlap"],
        spec["ir_occupancy"],
        spec["nonir_occupancy"],
        spec["p_value"],
    ]
    require_columns(df, required, path)

    df = df.copy()
    df["Source_File"] = str(path)
    numeric_columns = [
        "IR_total_annotated",
        "NonIR_total_annotated",
        spec["ir_overlap"],
        spec["nonir_overlap"],
        spec["ir_occupancy"],
        spec["nonir_occupancy"],
        spec["p_value"],
    ]
    if spec["odds_ratio"] in df.columns:
        numeric_columns.append(spec["odds_ratio"])
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    ir_rate = (df[spec["ir_overlap"]] + pseudocount) / (
        df["IR_total_annotated"] + 2 * pseudocount
    )
    nonir_rate = (df[spec["nonir_overlap"]] + pseudocount) / (
        df["NonIR_total_annotated"] + 2 * pseudocount
    )

    df["metric"] = metric
    df["IR_occupancy_rate_corrected"] = ir_rate
    df["NonIR_occupancy_rate_corrected"] = nonir_rate
    df["occupancy_ratio_corrected"] = ir_rate / nonir_rate
    df["log2_IR_vs_nonIR_occupancy_ratio"] = np.log2(df["occupancy_ratio_corrected"])
    df["delta_occupancy_%"] = df[spec["ir_occupancy"]] - df[spec["nonir_occupancy"]]
    df["raw_occupancy_ratio"] = np.where(
        df[spec["nonir_occupancy"]] > 0,
        df[spec["ir_occupancy"]] / df[spec["nonir_occupancy"]],
        np.nan,
    )
    df["minus_log10_fisher_p"] = -np.log10(df[spec["p_value"]].clip(lower=np.nextafter(0, 1)))

    return df


def ordered_values(values: pd.Series, preferred: list[str]) -> list[str]:
    present = [str(value) for value in values.dropna().unique()]
    ordered = [value for value in preferred if value in present]
    ordered.extend(sorted([value for value in present if value not in ordered]))
    return ordered


def svg_escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_text(
    x: float,
    y: float,
    text: object,
    size: int = 10,
    anchor: str = "middle",
    fill: str = "#111111",
    weight: str | None = None,
    rotate: float | None = None,
) -> str:
    attrs = [
        f'x="{x:.1f}"',
        f'y="{y:.1f}"',
        f'font-size="{size}"',
        f'text-anchor="{anchor}"',
        f'fill="{fill}"',
    ]
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if rotate is not None:
        attrs.append(f'transform="rotate({rotate:.1f} {x:.1f} {y:.1f})"')
    return f"<text {' '.join(attrs)}>{svg_escape(text)}</text>"


def finite_values(values: pd.Series | np.ndarray | list[float]) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    return arr[np.isfinite(arr)]


def box_stats(values: np.ndarray) -> dict[str, float] | None:
    values = finite_values(values)
    if len(values) == 0:
        return None
    q1, median, q3 = np.quantile(values, [0.25, 0.5, 0.75])
    iqr = q3 - q1
    low_bound = q1 - 1.5 * iqr
    high_bound = q3 + 1.5 * iqr
    whisker_low = values[values >= low_bound].min() if np.any(values >= low_bound) else values.min()
    whisker_high = values[values <= high_bound].max() if np.any(values <= high_bound) else values.max()
    return {
        "q1": float(q1),
        "median": float(median),
        "q3": float(q3),
        "low": float(whisker_low),
        "high": float(whisker_high),
    }


def nice_ticks(low: float, high: float, count: int = 5) -> list[float]:
    if not np.isfinite(low) or not np.isfinite(high) or low == high:
        return [low]
    span = high - low
    raw_step = span / max(count - 1, 1)
    magnitude = 10 ** math.floor(math.log10(abs(raw_step)))
    residual = raw_step / magnitude
    if residual <= 1:
        step = magnitude
    elif residual <= 2:
        step = 2 * magnitude
    elif residual <= 5:
        step = 5 * magnitude
    else:
        step = 10 * magnitude
    start = math.floor(low / step) * step
    end = math.ceil(high / step) * step
    ticks = []
    value = start
    while value <= end + step * 0.5:
        ticks.append(value)
        value += step
    return ticks


def write_svg(path: Path, width: int, height: int, body: list[str]) -> None:
    content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,DejaVu Sans,sans-serif;} .grid{stroke:#E5E7EB;stroke-width:1;} .axis{stroke:#111827;stroke-width:1;} .zero{stroke:#333333;stroke-width:1;stroke-dasharray:4 3;}</style>',
    ]
    content.extend(body)
    content.append("</svg>")
    path.write_text("\n".join(content) + "\n", encoding="utf-8")


def plot_ratio_box_svg(df: pd.DataFrame, out_dir: Path, metric: str) -> None:
    categories = ordered_values(df["Category"], CATEGORY_ORDER)
    cell_lines = ordered_values(df["Cell_line"], CELL_LINE_ORDER)
    classes = ordered_values(df["Class"], CLASS_ORDER)
    if not categories or not cell_lines or not classes:
        return

    value_col = "log2_IR_vs_nonIR_occupancy_ratio"
    all_values = finite_values(df[value_col].replace([np.inf, -np.inf], np.nan).dropna())
    if len(all_values) == 0:
        return

    y_low = min(-1.0, float(np.quantile(all_values, 0.02)) - 0.4)
    y_high = max(1.0, float(np.quantile(all_values, 0.98)) + 0.4)
    if y_low == y_high:
        y_low -= 1
        y_high += 1

    panel_w = 380
    panel_h = 310
    left = 64
    right = 18
    top = 56
    bottom = 76
    width = panel_w * len(cell_lines)
    height = 58 + panel_h * len(categories) + 24
    body: list[str] = []
    body.append(svg_text(width / 2, 24, f"IR vs nonIR occupancy ratio by class ({METRICS[metric]['label']})", 15, weight="bold"))
    body.append(svg_text(width / 2, 44, "Y-axis: log2 corrected IR/nonIR occupancy ratio; 0 = equal occupancy", 11, fill="#4B5563"))

    rng = np.random.default_rng(1)
    ticks = nice_ticks(y_low, y_high)

    def y_map(value: float, y0: float, plot_h: float) -> float:
        return y0 + plot_h - (value - y_low) / (y_high - y_low) * plot_h

    for row_idx, category in enumerate(categories):
        for col_idx, cell_line in enumerate(cell_lines):
            x0 = col_idx * panel_w
            y0 = 58 + row_idx * panel_h
            plot_x = x0 + left
            plot_y = y0 + top
            plot_w = panel_w - left - right
            plot_h = panel_h - top - bottom
            panel = df[(df["Category"] == category) & (df["Cell_line"] == cell_line)].copy()

            body.append(f'<rect x="{x0 + 8}" y="{y0 + 8}" width="{panel_w - 16}" height="{panel_h - 16}" fill="#FFFFFF" stroke="#D1D5DB" stroke-width="1"/>')
            body.append(svg_text(x0 + panel_w / 2, y0 + 30, f"{category} | {cell_line}", 12, weight="bold"))
            if panel.empty:
                body.append(svg_text(x0 + panel_w / 2, y0 + panel_h / 2, "no data", 12, fill="#6B7280"))
                continue

            for tick in ticks:
                if tick < y_low - 1e-9 or tick > y_high + 1e-9:
                    continue
                ty = y_map(tick, plot_y, plot_h)
                body.append(f'<line class="grid" x1="{plot_x:.1f}" y1="{ty:.1f}" x2="{plot_x + plot_w:.1f}" y2="{ty:.1f}"/>')
                body.append(svg_text(plot_x - 8, ty + 3, f"{tick:g}", 9, anchor="end", fill="#4B5563"))

            zero_y = y_map(0, plot_y, plot_h)
            if plot_y <= zero_y <= plot_y + plot_h:
                body.append(f'<line class="zero" x1="{plot_x:.1f}" y1="{zero_y:.1f}" x2="{plot_x + plot_w:.1f}" y2="{zero_y:.1f}"/>')

            body.append(f'<line class="axis" x1="{plot_x:.1f}" y1="{plot_y + plot_h:.1f}" x2="{plot_x + plot_w:.1f}" y2="{plot_y + plot_h:.1f}"/>')
            body.append(f'<line class="axis" x1="{plot_x:.1f}" y1="{plot_y:.1f}" x2="{plot_x:.1f}" y2="{plot_y + plot_h:.1f}"/>')

            step = plot_w / max(len(classes), 1)
            for idx, class_name in enumerate(classes):
                values = finite_values(panel.loc[panel["Class"] == class_name, value_col])
                cx = plot_x + step * (idx + 0.5)
                color = CLASS_COLORS.get(class_name, "#6B7280")
                stats = box_stats(values)
                if stats:
                    q1_y = y_map(stats["q1"], plot_y, plot_h)
                    q3_y = y_map(stats["q3"], plot_y, plot_h)
                    med_y = y_map(stats["median"], plot_y, plot_h)
                    low_y = y_map(stats["low"], plot_y, plot_h)
                    high_y = y_map(stats["high"], plot_y, plot_h)
                    box_w = min(28, step * 0.48)
                    body.append(f'<line x1="{cx:.1f}" y1="{high_y:.1f}" x2="{cx:.1f}" y2="{low_y:.1f}" stroke="{color}" stroke-width="1.3"/>')
                    body.append(f'<line x1="{cx - box_w / 3:.1f}" y1="{high_y:.1f}" x2="{cx + box_w / 3:.1f}" y2="{high_y:.1f}" stroke="{color}" stroke-width="1.3"/>')
                    body.append(f'<line x1="{cx - box_w / 3:.1f}" y1="{low_y:.1f}" x2="{cx + box_w / 3:.1f}" y2="{low_y:.1f}" stroke="{color}" stroke-width="1.3"/>')
                    body.append(f'<rect x="{cx - box_w / 2:.1f}" y="{min(q1_y, q3_y):.1f}" width="{box_w:.1f}" height="{abs(q3_y - q1_y):.1f}" fill="{color}" fill-opacity="0.28" stroke="{color}" stroke-width="1.2"/>')
                    body.append(f'<line x1="{cx - box_w / 2:.1f}" y1="{med_y:.1f}" x2="{cx + box_w / 2:.1f}" y2="{med_y:.1f}" stroke="#111111" stroke-width="1.5"/>')

                for value in values:
                    jitter = float(rng.normal(0, min(7, step * 0.09)))
                    py = y_map(value, plot_y, plot_h)
                    body.append(f'<circle cx="{cx + jitter:.1f}" cy="{py:.1f}" r="3.0" fill="{color}" fill-opacity="0.72" stroke="white" stroke-width="0.5"/>')

                label = CLASS_LABELS.get(class_name, class_name.replace("_", " "))
                body.append(svg_text(cx, plot_y + plot_h + 18, label, 9, rotate=-28, anchor="end"))

            if col_idx == 0:
                body.append(svg_text(x0 + 15, plot_y + plot_h / 2, "log2 ratio", 10, rotate=-90))

    out = out_dir / f"ir_nonir_{metric}_log2_ratio_boxplot.svg"
    write_svg(out, width, height, body)
    print(f"[INFO] Saved {out}")


def write_group_summary(df: pd.DataFrame, out_dir: Path) -> None:
    rows = []
    columns = [
        "Class",
        "Category",
        "Cell_line",
        "n_rows",
        "n_targets",
        "median_log2_ratio",
        "mean_log2_ratio",
        "q1_log2_ratio",
        "q3_log2_ratio",
        "pct_rows_IR_gt_nonIR",
        "median_delta_occupancy_%",
    ]
    group_cols = ["Class", "Category", "Cell_line"]
    value_col = "log2_IR_vs_nonIR_occupancy_ratio"
    for key, group in df.groupby(group_cols, dropna=False):
        values = group[value_col].dropna()
        if values.empty:
            continue
        rows.append(
            {
                "Class": key[0],
                "Category": key[1],
                "Cell_line": key[2],
                "n_rows": len(group),
                "n_targets": group["Original_ID"].nunique(dropna=True),
                "median_log2_ratio": values.median(),
                "mean_log2_ratio": values.mean(),
                "q1_log2_ratio": values.quantile(0.25),
                "q3_log2_ratio": values.quantile(0.75),
                "pct_rows_IR_gt_nonIR": (values > 0).mean() * 100,
                "median_delta_occupancy_%": group["delta_occupancy_%"].median(),
            }
        )

    summary = pd.DataFrame(rows, columns=columns)
    if not summary.empty:
        summary = summary.sort_values(
            ["Category", "Cell_line", "Class"],
            key=lambda series: series.map(class_sort_key) if series.name == "Class" else series,
        )
    summary.to_csv(out_dir / "ratio_group_summary.tsv", sep="\t", index=False)


def write_class_stats(df: pd.DataFrame, out_dir: Path) -> None:
    value_col = "log2_IR_vs_nonIR_occupancy_ratio"
    kruskal_rows = []
    pairwise_rows = []
    kruskal_columns = ["Category", "Cell_line", "test", "classes", "statistic", "p_value", "q_value_bh"]
    pairwise_columns = [
        "Category",
        "Cell_line",
        "test",
        "class_a",
        "class_b",
        "n_a",
        "n_b",
        "median_a",
        "median_b",
        "delta_median_log2_ratio",
        "statistic",
        "p_value",
        "q_value_bh",
    ]

    for (category, cell_line), group in df.groupby(["Category", "Cell_line"], dropna=False):
        class_values = []
        for class_name, class_group in group.groupby("Class", dropna=False):
            values = class_group[value_col].dropna().to_numpy(dtype=float)
            if len(values):
                class_values.append((class_name, values))

        if kruskal is not None and len(class_values) >= 2:
            try:
                stat, pvalue = kruskal(*[values for _, values in class_values])
            except ValueError:
                stat, pvalue = np.nan, np.nan
            kruskal_rows.append(
                {
                    "Category": category,
                    "Cell_line": cell_line,
                    "test": "Kruskal-Wallis",
                    "classes": ",".join(str(name) for name, _ in class_values),
                    "statistic": stat,
                    "p_value": pvalue,
                }
            )

        control = group[group["Class"] == "control"][value_col].dropna().to_numpy(dtype=float)
        if len(control) == 0:
            pass
        else:
            for class_name, values in class_values:
                if class_name == "control":
                    continue
                if mannwhitneyu is not None:
                    try:
                        stat, pvalue = mannwhitneyu(values, control, alternative="two-sided")
                    except ValueError:
                        stat, pvalue = np.nan, np.nan
                else:
                    stat, pvalue = np.nan, np.nan
                pairwise_rows.append(
                    {
                        "Category": category,
                        "Cell_line": cell_line,
                        "test": "Mann-Whitney U" if mannwhitneyu is not None else "median difference only",
                        "class_a": class_name,
                        "class_b": "control",
                        "n_a": len(values),
                        "n_b": len(control),
                        "median_a": float(np.median(values)),
                        "median_b": float(np.median(control)),
                        "delta_median_log2_ratio": float(np.median(values) - np.median(control)),
                        "statistic": stat,
                        "p_value": pvalue,
                    }
                )

        for (class_a, values_a), (class_b, values_b) in combinations(class_values, 2):
            if "control" in {class_a, class_b}:
                continue
            if mannwhitneyu is not None:
                try:
                    stat, pvalue = mannwhitneyu(values_a, values_b, alternative="two-sided")
                except ValueError:
                    stat, pvalue = np.nan, np.nan
            else:
                stat, pvalue = np.nan, np.nan
            pairwise_rows.append(
                {
                    "Category": category,
                    "Cell_line": cell_line,
                    "test": "Mann-Whitney U" if mannwhitneyu is not None else "median difference only",
                    "class_a": class_a,
                    "class_b": class_b,
                    "n_a": len(values_a),
                    "n_b": len(values_b),
                    "median_a": float(np.median(values_a)),
                    "median_b": float(np.median(values_b)),
                    "delta_median_log2_ratio": float(np.median(values_a) - np.median(values_b)),
                    "statistic": stat,
                    "p_value": pvalue,
                }
            )

    kruskal_df = pd.DataFrame(kruskal_rows)
    if not kruskal_df.empty:
        kruskal_df["q_value_bh"] = bh_adjust(kruskal_df["p_value"])
    kruskal_df = kruskal_df.reindex(columns=kruskal_columns)
    kruskal_df.to_csv(out_dir / "ratio_kruskal_by_category_cellline.tsv", sep="\t", index=False)

    pairwise_df = pd.DataFrame(pairwise_rows)
    if not pairwise_df.empty:
        pairwise_df["q_value_bh"] = bh_adjust(pairwise_df["p_value"])
    pairwise_df = pairwise_df.reindex(columns=pairwise_columns)
    pairwise_df.to_csv(out_dir / "ratio_pairwise_class_tests.tsv", sep="\t", index=False)


def plot_ratio_box(df: pd.DataFrame, out_dir: Path, metric: str) -> None:
    plt = get_pyplot()
    if plt is None:
        plot_ratio_box_svg(df, out_dir, metric)
        return

    categories = ordered_values(df["Category"], CATEGORY_ORDER)
    cell_lines = ordered_values(df["Cell_line"], CELL_LINE_ORDER)
    classes = ordered_values(df["Class"], CLASS_ORDER)
    if not categories or not cell_lines or not classes:
        return

    value_col = "log2_IR_vs_nonIR_occupancy_ratio"
    all_values = df[value_col].replace([np.inf, -np.inf], np.nan).dropna()
    if all_values.empty:
        return
    y_low = min(-1.0, all_values.quantile(0.02) - 0.4)
    y_high = max(1.0, all_values.quantile(0.98) + 0.4)

    fig, axes = plt.subplots(
        len(categories),
        len(cell_lines),
        figsize=(4.2 * len(cell_lines), 3.4 * len(categories)),
        sharey=True,
        squeeze=False,
    )
    rng = np.random.default_rng(1)

    for row_idx, category in enumerate(categories):
        for col_idx, cell_line in enumerate(cell_lines):
            ax = axes[row_idx][col_idx]
            panel = df[(df["Category"] == category) & (df["Cell_line"] == cell_line)].copy()
            if panel.empty:
                ax.axis("off")
                ax.set_title(f"{category} {cell_line}\nno data")
                continue

            data = [
                panel.loc[panel["Class"] == class_name, value_col].dropna().to_numpy(dtype=float)
                for class_name in classes
            ]
            positions = np.arange(1, len(classes) + 1)
            non_empty = [values for values in data if len(values)]
            if non_empty:
                box = ax.boxplot(
                    data,
                    positions=positions,
                    widths=0.55,
                    patch_artist=True,
                    showfliers=False,
                    medianprops={"color": "#111111", "linewidth": 1.2},
                    boxprops={"linewidth": 0.9},
                    whiskerprops={"linewidth": 0.9},
                    capprops={"linewidth": 0.9},
                )
                for patch, class_name in zip(box["boxes"], classes):
                    patch.set_facecolor(CLASS_COLORS.get(class_name, "#BAB0AC"))
                    patch.set_alpha(0.35)

            for pos, class_name, values in zip(positions, classes, data):
                if len(values) == 0:
                    continue
                jitter = rng.normal(0, 0.055, size=len(values))
                ax.scatter(
                    np.full(len(values), pos) + jitter,
                    values,
                    s=18,
                    alpha=0.72,
                    color=CLASS_COLORS.get(class_name, "#6B7280"),
                    edgecolor="white",
                    linewidth=0.35,
                    zorder=3,
                )

            ax.axhline(0, color="#333333", linestyle="--", linewidth=0.8)
            ax.set_ylim(y_low, y_high)
            ax.set_xticks(positions)
            ax.set_xticklabels([CLASS_LABELS.get(label, label.replace("_", " ")) for label in classes], rotation=30, ha="right")
            ax.set_title(f"{category} | {cell_line}")
            if col_idx == 0:
                ax.set_ylabel("log2 corrected IR/nonIR occupancy ratio")
            ax.grid(axis="y", color="#E5E7EB", linewidth=0.7)
            ax.set_axisbelow(True)

    fig.suptitle(
        f"IR vs nonIR occupancy ratio by class ({METRICS[metric]['label']})",
        fontsize=13,
        y=1.01,
    )
    fig.tight_layout()
    for ext in ["png", "pdf"]:
        out = out_dir / f"ir_nonir_{metric}_log2_ratio_boxplot.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=400 if ext == "png" else None)
    plt.close(fig)


def infer_sep(path: Path) -> str:
    return "\t" if path.suffix.lower() in {".tsv", ".txt"} else ","


def find_target_column(df: pd.DataFrame, path: Path) -> str:
    for column in ["Target_ID", "Original_ID", "Target", "ENCODE_Target", "Gene", "gene"]:
        if column in df.columns:
            return column
    raise ValueError(f"{path} has no recognizable target column")


def find_rank_column(df: pd.DataFrame) -> str | None:
    for column in ["Rank", "rank", "Ranking", "ranking", "candidate_rank"]:
        if column in df.columns:
            return column
    return None


def read_rank_file(path_text: str | None, category: str, rank_source: str) -> pd.DataFrame:
    if not path_text:
        return pd.DataFrame()
    path = Path(path_text)
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path, sep=infer_sep(path), encoding="utf-8-sig")
    target_col = find_target_column(df, path)
    rank_col = find_rank_column(df)
    ranks = pd.to_numeric(df[rank_col], errors="coerce") if rank_col else pd.Series(np.arange(1, len(df) + 1))

    out = pd.DataFrame(
        {
            "Category": category,
            "rank_source": rank_source,
            "rank_target": df[target_col].astype(str).str.strip(),
            "rank_target_key": df[target_col].map(normalize_key),
            "rank": ranks,
        }
    )
    out = out[(out["rank_target_key"] != "") & out["rank"].notna()].copy()
    out = out.sort_values("rank").drop_duplicates(["Category", "rank_source", "rank_target_key"], keep="first")
    return out


def load_rank_tables(args: argparse.Namespace) -> pd.DataFrame:
    frames = [
        read_rank_file(args.positive_tf, "TF", "positive"),
        read_rank_file(args.negative_tf, "TF", "negative"),
        read_rank_file(args.positive_rbp, "RBP", "positive"),
        read_rank_file(args.negative_rbp, "RBP", "negative"),
    ]
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def rank_map(ranks: pd.DataFrame, category: str, source: str) -> dict[str, float]:
    sub = ranks[(ranks["Category"] == category) & (ranks["rank_source"] == source)]
    return dict(zip(sub["rank_target_key"], sub["rank"]))


def attach_ranks(df: pd.DataFrame, ranks: pd.DataFrame) -> pd.DataFrame:
    if ranks.empty:
        return df

    out = df.copy()
    out["Original_ID_key"] = out["Original_ID"].map(normalize_key)
    out["Target_key"] = out["Target"].map(normalize_key)

    for source in ["positive", "negative"]:
        rank_values = []
        for row in out.itertuples(index=False):
            mapping = rank_map(ranks, row.Category, source)
            value = mapping.get(row.Original_ID_key, mapping.get(row.Target_key, np.nan))
            rank_values.append(value)
        out[f"{source}_rank"] = rank_values

    return out.drop(columns=["Original_ID_key", "Target_key"])


def aggregate_candidate_rank(df: pd.DataFrame) -> pd.DataFrame:
    value_col = "log2_IR_vs_nonIR_occupancy_ratio"
    rows = []
    has_positive_rank = "positive_rank" in df.columns
    has_negative_rank = "negative_rank" in df.columns

    for key, group in df.groupby(["Class", "Category", "Original_ID"], dropna=False):
        values = group[value_col].dropna()
        if values.empty:
            continue
        row = {
            "Class": key[0],
            "Category": key[1],
            "Original_ID": key[2],
            "Target": ";".join(sorted(set(group["Target"].dropna().astype(str)))),
            "n_rows": len(group),
            "n_cell_lines": group["Cell_line"].nunique(dropna=True),
            "median_log2_ratio": values.median(),
            "mean_log2_ratio": values.mean(),
            "q1_log2_ratio": values.quantile(0.25),
            "q3_log2_ratio": values.quantile(0.75),
            "median_delta_occupancy_%": group["delta_occupancy_%"].median(),
        }
        if has_positive_rank:
            positive = group["positive_rank"].dropna()
            row["positive_rank"] = positive.iloc[0] if not positive.empty else np.nan
        if has_negative_rank:
            negative = group["negative_rank"].dropna()
            row["negative_rank"] = negative.iloc[0] if not negative.empty else np.nan
        rows.append(row)

    return pd.DataFrame(rows)


def write_rank_stats(candidate_df: pd.DataFrame, out_dir: Path) -> None:
    columns = [
        "rank_source",
        "Category",
        "Class",
        "n_targets",
        "spearman_rho",
        "p_value",
        "q_value_bh",
    ]
    if candidate_df.empty:
        pd.DataFrame(columns=columns).to_csv(
            out_dir / "rank_spearman_correlations.tsv",
            sep="\t",
            index=False,
        )
        return

    def calc_spearman(x: pd.Series, y: pd.Series) -> tuple[float, float]:
        if spearmanr is not None:
            rho, pvalue = spearmanr(x, y)
            return float(rho), float(pvalue)
        rho = x.rank(method="average").corr(y.rank(method="average"), method="pearson")
        return float(rho), np.nan

    rows = []
    for source in ["positive", "negative"]:
        rank_col = f"{source}_rank"
        if rank_col not in candidate_df.columns:
            continue
        ranked = candidate_df[candidate_df[rank_col].notna()].copy()
        for (category, class_name), group in ranked.groupby(["Category", "Class"], dropna=False):
            if len(group) < 3:
                continue
            rho, pvalue = calc_spearman(group[rank_col], group["median_log2_ratio"])
            rows.append(
                {
                    "rank_source": source,
                    "Category": category,
                    "Class": class_name,
                    "n_targets": len(group),
                    "spearman_rho": rho,
                    "p_value": pvalue,
                }
            )
        for category, group in ranked.groupby("Category", dropna=False):
            if len(group) < 3:
                continue
            rho, pvalue = calc_spearman(group[rank_col], group["median_log2_ratio"])
            rows.append(
                {
                    "rank_source": source,
                    "Category": category,
                    "Class": "all_ranked",
                    "n_targets": len(group),
                    "spearman_rho": rho,
                    "p_value": pvalue,
                }
            )

    stats = pd.DataFrame(rows)
    if not stats.empty:
        stats["q_value_bh"] = bh_adjust(stats["p_value"])
    stats = stats.reindex(columns=columns)
    stats.to_csv(out_dir / "rank_spearman_correlations.tsv", sep="\t", index=False)


def plot_rank_source_svg(candidate_df: pd.DataFrame, out_dir: Path, source: str, xscale: str) -> None:
    rank_col = f"{source}_rank"
    if rank_col not in candidate_df.columns:
        return

    ranked = candidate_df[candidate_df[rank_col].notna()].copy()
    if ranked.empty:
        return

    categories = ordered_values(ranked["Category"], CATEGORY_ORDER)
    classes = ordered_values(ranked["Class"], CLASS_ORDER)
    if not categories:
        return

    panel_w = 470
    panel_h = 350
    left = 62
    right = 22
    top = 56
    bottom = 58
    width = panel_w * len(categories)
    height = panel_h + 72
    body: list[str] = []
    source_label = RANK_SOURCE_LABELS.get(source, source)
    body.append(svg_text(width / 2, 24, f"{source_label} candidate rank vs IR/nonIR occupancy ratio", 15, weight="bold"))
    body.append(svg_text(width / 2, 44, "Each point is a target median across available cell-line/peak rows", 11, fill="#4B5563"))

    all_y = finite_values(ranked["median_log2_ratio"])
    if len(all_y) == 0:
        return
    y_low = min(-1.0, float(np.quantile(all_y, 0.02)) - 0.4)
    y_high = max(1.0, float(np.quantile(all_y, 0.98)) + 0.4)
    y_ticks = nice_ticks(y_low, y_high)

    def scale_x(values: np.ndarray) -> np.ndarray:
        if xscale == "log":
            return np.log10(np.clip(values, 1, None))
        return values

    for col_idx, category in enumerate(categories):
        x0 = col_idx * panel_w
        y0 = 62
        plot_x = x0 + left
        plot_y = y0 + top
        plot_w = panel_w - left - right
        plot_h = panel_h - top - bottom
        panel = ranked[ranked["Category"] == category].copy()

        body.append(f'<rect x="{x0 + 8}" y="{y0 + 8}" width="{panel_w - 16}" height="{panel_h - 16}" fill="#FFFFFF" stroke="#D1D5DB" stroke-width="1"/>')
        body.append(svg_text(x0 + panel_w / 2, y0 + 30, category, 12, weight="bold"))
        if panel.empty:
            body.append(svg_text(x0 + panel_w / 2, y0 + panel_h / 2, "no ranked candidates", 12, fill="#6B7280"))
            continue

        raw_x = finite_values(panel[rank_col])
        if len(raw_x) == 0:
            continue
        scaled_x = scale_x(raw_x)
        x_low = float(np.min(scaled_x))
        x_high = float(np.max(scaled_x))
        if x_low == x_high:
            x_low -= 1
            x_high += 1
        x_pad = (x_high - x_low) * 0.06
        x_low -= x_pad
        x_high += x_pad

        def x_map(value: float) -> float:
            scaled = math.log10(max(value, 1)) if xscale == "log" else value
            return plot_x + (scaled - x_low) / (x_high - x_low) * plot_w

        def y_map(value: float) -> float:
            return plot_y + plot_h - (value - y_low) / (y_high - y_low) * plot_h

        for tick in y_ticks:
            if tick < y_low - 1e-9 or tick > y_high + 1e-9:
                continue
            ty = y_map(tick)
            body.append(f'<line class="grid" x1="{plot_x:.1f}" y1="{ty:.1f}" x2="{plot_x + plot_w:.1f}" y2="{ty:.1f}"/>')
            body.append(svg_text(plot_x - 8, ty + 3, f"{tick:g}", 9, anchor="end", fill="#4B5563"))

        zero_y = y_map(0)
        if plot_y <= zero_y <= plot_y + plot_h:
            body.append(f'<line class="zero" x1="{plot_x:.1f}" y1="{zero_y:.1f}" x2="{plot_x + plot_w:.1f}" y2="{zero_y:.1f}"/>')
        body.append(f'<line class="axis" x1="{plot_x:.1f}" y1="{plot_y + plot_h:.1f}" x2="{plot_x + plot_w:.1f}" y2="{plot_y + plot_h:.1f}"/>')
        body.append(f'<line class="axis" x1="{plot_x:.1f}" y1="{plot_y:.1f}" x2="{plot_x:.1f}" y2="{plot_y + plot_h:.1f}"/>')

        if xscale == "log":
            raw_ticks = [1, 2, 5, 10, 20, 50, 100, 200]
            x_ticks = [tick for tick in raw_ticks if panel[rank_col].min() <= tick <= panel[rank_col].max()]
            if not x_ticks:
                x_ticks = [float(panel[rank_col].min()), float(panel[rank_col].max())]
        else:
            x_ticks = nice_ticks(float(panel[rank_col].min()), float(panel[rank_col].max()))
        for tick in x_ticks:
            tx = x_map(float(tick))
            if plot_x <= tx <= plot_x + plot_w:
                body.append(f'<line class="grid" x1="{tx:.1f}" y1="{plot_y:.1f}" x2="{tx:.1f}" y2="{plot_y + plot_h:.1f}"/>')
                body.append(svg_text(tx, plot_y + plot_h + 16, f"{tick:g}", 9, fill="#4B5563"))

        for class_name in classes:
            sub = panel[panel["Class"] == class_name]
            if sub.empty:
                continue
            color = CLASS_COLORS.get(class_name, "#6B7280")
            xs = sub[rank_col].to_numpy(dtype=float)
            ys = sub["median_log2_ratio"].to_numpy(dtype=float)
            finite = np.isfinite(xs) & np.isfinite(ys)
            if finite.sum() >= 3 and np.unique(xs[finite]).size >= 2:
                fit_x = scale_x(xs[finite])
                slope, intercept = np.polyfit(fit_x, ys[finite], deg=1)
                line_xs = np.linspace(fit_x.min(), fit_x.max(), 40)
                points = []
                for sx in line_xs:
                    raw_value = 10 ** sx if xscale == "log" else sx
                    points.append(f"{x_map(raw_value):.1f},{y_map(slope * sx + intercept):.1f}")
                body.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="1.2" stroke-opacity="0.75"/>')

            for x_val, y_val in zip(xs[finite], ys[finite]):
                body.append(f'<circle cx="{x_map(x_val):.1f}" cy="{y_map(y_val):.1f}" r="4.0" fill="{color}" fill-opacity="0.78" stroke="white" stroke-width="0.6"/>')

        body.append(svg_text(plot_x + plot_w / 2, y0 + panel_h - 12, f"{source_label} list rank (lower = higher)", 10))
        if col_idx == 0:
            body.append(svg_text(x0 + 16, plot_y + plot_h / 2, "median log2 ratio", 10, rotate=-90))

    legend_y = height - 20
    legend_x = 20
    for class_name in classes:
        color = CLASS_COLORS.get(class_name, "#6B7280")
        body.append(f'<circle cx="{legend_x:.1f}" cy="{legend_y - 4:.1f}" r="4" fill="{color}" fill-opacity="0.78"/>')
        body.append(svg_text(legend_x + 9, legend_y, CLASS_LABELS.get(class_name, class_name.replace("_", " ")), 10, anchor="start"))
        legend_x += 112

    out = out_dir / f"rank_{source}_vs_log2_ratio.svg"
    write_svg(out, width, height, body)
    print(f"[INFO] Saved {out}")


def plot_rank_source(candidate_df: pd.DataFrame, out_dir: Path, source: str, xscale: str) -> None:
    plt = get_pyplot()
    if plt is None:
        plot_rank_source_svg(candidate_df, out_dir, source, xscale)
        return

    rank_col = f"{source}_rank"
    if rank_col not in candidate_df.columns:
        return

    ranked = candidate_df[candidate_df[rank_col].notna()].copy()
    if ranked.empty:
        return

    categories = ordered_values(ranked["Category"], CATEGORY_ORDER)
    classes = ordered_values(ranked["Class"], CLASS_ORDER)
    fig, axes = plt.subplots(1, len(categories), figsize=(5.2 * len(categories), 4.2), squeeze=False)

    for ax, category in zip(axes[0], categories):
        panel = ranked[ranked["Category"] == category].copy()
        if panel.empty:
            ax.axis("off")
            ax.set_title(f"{category}\nno ranked candidates")
            continue

        for class_name in classes:
            sub = panel[panel["Class"] == class_name]
            if sub.empty:
                continue
            ax.scatter(
                sub[rank_col],
                sub["median_log2_ratio"],
                s=32,
                alpha=0.78,
                label=CLASS_LABELS.get(class_name, class_name.replace("_", " ")),
                color=CLASS_COLORS.get(class_name, "#6B7280"),
                edgecolor="white",
                linewidth=0.4,
            )
            if len(sub) >= 3:
                x = sub[rank_col].to_numpy(dtype=float)
                y = sub["median_log2_ratio"].to_numpy(dtype=float)
                finite = np.isfinite(x) & np.isfinite(y)
                if finite.sum() >= 3 and np.unique(x[finite]).size >= 2:
                    slope, intercept = np.polyfit(x[finite], y[finite], deg=1)
                    xs = np.linspace(x[finite].min(), x[finite].max(), 50)
                    ax.plot(xs, slope * xs + intercept, color=CLASS_COLORS.get(class_name, "#6B7280"), linewidth=1)

        ax.axhline(0, color="#333333", linestyle="--", linewidth=0.8)
        ax.set_xscale(xscale)
        ax.set_title(category)
        source_label = RANK_SOURCE_LABELS.get(source, source)
        ax.set_xlabel(f"{source_label} list rank (lower = higher)")
        ax.set_ylabel("target median log2 corrected IR/nonIR ratio")
        ax.grid(color="#E5E7EB", linewidth=0.7)
        ax.set_axisbelow(True)

    handles, labels = axes[0][0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="lower center", ncol=min(4, len(handles)), bbox_to_anchor=(0.5, -0.03))
    source_label = RANK_SOURCE_LABELS.get(source, source)
    fig.suptitle(f"{source_label} candidate rank vs IR/nonIR occupancy ratio", fontsize=13, y=1.02)
    fig.tight_layout()

    for ext in ["png", "pdf"]:
        out = out_dir / f"rank_{source}_vs_log2_ratio.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=400 if ext == "png" else None)
    plt.close(fig)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summaries = [read_summary(path, args.metric, args.pseudocount) for path in args.summary]
    df = pd.concat(summaries, ignore_index=True)

    df.to_csv(out_dir / "ir_nonir_ratio_combined_rows.tsv", sep="\t", index=False)
    write_group_summary(df, out_dir)
    write_class_stats(df, out_dir)
    plot_ratio_box(df, out_dir, args.metric)

    ranks = load_rank_tables(args)
    if ranks.empty:
        (out_dir / "rank_analysis_skipped.txt").write_text(
            "Rank analysis was skipped because no --positive_tf/--negative_tf/"
            "--positive_rbp/--negative_rbp files were provided.\n",
            encoding="utf-8",
        )
    else:
        ranks.to_csv(out_dir / "candidate_rank_inputs.tsv", sep="\t", index=False)
        ranked_rows = attach_ranks(df, ranks)
        ranked_rows.to_csv(out_dir / "ir_nonir_ratio_combined_rows_with_ranks.tsv", sep="\t", index=False)
        candidate_df = aggregate_candidate_rank(ranked_rows)
        candidate_df.to_csv(out_dir / "candidate_rank_ratio_summary.tsv", sep="\t", index=False)
        write_rank_stats(candidate_df, out_dir)
        plot_rank_source(candidate_df, out_dir, "positive", args.rank_xscale)
        plot_rank_source(candidate_df, out_dir, "negative", args.rank_xscale)

    print(f"[INFO] Wrote ratio analysis outputs to {out_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise
