from itertools import combinations
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

from plot_tf_only_prediction_vs_control import (
    COLORS,
    draw_centered_text,
    draw_mean_box,
    draw_rotated_ylabel,
    font,
    p_label,
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


def draw_single_panel(data, stat, factor_type, out_png):
    width, height = 850, 820
    margin_left, margin_right = 120, 50
    margin_top, margin_bottom = 130, 125
    plot_left = margin_left
    plot_right = width - margin_right
    plot_top = margin_top
    plot_bottom = height - margin_bottom
    plot_height = plot_bottom - plot_top

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    label_font = font(25)
    small_font = font(21)
    tick_font = font(22)
    legend_font = font(22)

    ymax = max(data["all_events"].astype(float).max(), 1) * 1.22

    def y_to_px(value):
        return plot_bottom - (float(value) / ymax) * plot_height

    axis = (17, 24, 39)
    grid = (229, 231, 235)
    for tick in np.linspace(0, ymax / 1.22, 6):
        y = y_to_px(tick)
        draw.line([plot_left, y, plot_right, y], fill=grid, width=2)
        draw.text((plot_left - 16, y), f"{int(round(tick))}", fill=(55, 65, 81), font=tick_font, anchor="rm")
    draw.line([plot_left, plot_bottom, plot_right, plot_bottom], fill=axis, width=2)
    draw.line([plot_left, plot_top, plot_left, plot_bottom], fill=axis, width=2)

    center = (plot_left + plot_right) / 2
    box_width = 76
    offsets = {"prediction": -52, "control": 52}
    for group in ["prediction", "control"]:
        vals = data.loc[data["group"] == group, "all_events"].dropna().astype(float).values
        label_side = "left" if group == "prediction" else "right"
        draw_mean_box(
            draw,
            vals,
            center + offsets[group],
            box_width,
            y_to_px,
            COLORS[group],
            small_font,
            label_side,
            center_stat="mean",
        )

    panel_label = "All predicted TFs" if factor_type == "TF" else factor_type
    draw_centered_text(draw, (center, plot_bottom + 42), panel_label, (17, 24, 39), label_font)
    data_max = data["all_events"].astype(float).max()
    p_y = y_to_px(data_max * 1.08)
    draw_centered_text(draw, (center, p_y - 12), p_label(stat["p_two_sided"], "Permutation p"), (55, 65, 81), small_font)
    draw_rotated_ylabel(image, "Event count", (16, int(height / 2 - 145)), label_font)

    legend_y = 95
    legend_x = 80
    for i, (name, color) in enumerate([("Prediction", COLORS["prediction"]), ("Control", COLORS["control"])]):
        x = legend_x + i * 172
        draw.ellipse([x, legend_y - 9, x + 18, legend_y + 9], fill=color)
        draw.text((x + 30, legend_y), name, fill=(17, 24, 39), font=legend_font, anchor="lm")
    mean_x = legend_x + 345
    draw.line([mean_x, legend_y, mean_x + 34, legend_y], fill=(17, 24, 39), width=4)
    draw.text((mean_x + 46, legend_y), "Mean", fill=(17, 24, 39), font=legend_font, anchor="lm")
    image.save(out_png)


def combine_images(tf_png, rbp_png, out_png):
    tf = Image.open(tf_png).convert("RGB")
    rbp = Image.open(rbp_png).convert("RGB")
    gap = 70
    left_pad = 40
    right_pad = 40
    width = left_pad + tf.width + gap + rbp.width + right_pad
    height = max(tf.height, rbp.height) + 80
    canvas = Image.new("RGB", (width, height), "white")
    canvas.paste(tf, (left_pad, 40))
    canvas.paste(rbp, (left_pad + tf.width + gap, 40))
    canvas.save(out_png)


def draw_combined_panel(data, stats, out_png):
    width, height = 1300, 820
    margin_left, margin_right = 130, 60
    margin_top, margin_bottom = 130, 125
    plot_left = margin_left
    plot_right = width - margin_right
    plot_top = margin_top
    plot_bottom = height - margin_bottom
    plot_width = plot_right - plot_left
    plot_height = plot_bottom - plot_top

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    label_font = font(25)
    small_font = font(21)
    tick_font = font(22)
    legend_font = font(22)

    ymax = max(data["all_events"].astype(float).max(), 1) * 1.22

    def y_to_px(value):
        return plot_bottom - (float(value) / ymax) * plot_height

    axis = (17, 24, 39)
    grid = (229, 231, 235)
    for tick in np.linspace(0, ymax / 1.22, 6):
        y = y_to_px(tick)
        draw.line([plot_left, y, plot_right, y], fill=grid, width=2)
        draw.text((plot_left - 16, y), f"{int(round(tick))}", fill=(55, 65, 81), font=tick_font, anchor="rm")
    draw.line([plot_left, plot_bottom, plot_right, plot_bottom], fill=axis, width=2)
    draw.line([plot_left, plot_top, plot_left, plot_bottom], fill=axis, width=2)

    centers = {
        "TF": plot_left + plot_width * 0.32,
        "RBP": plot_right - plot_width * 0.32,
    }
    labels = {
        "TF": "All predicted TFs",
        "RBP": "All predicted RBPs",
    }
    box_width = 76
    offsets = {"prediction": -52, "control": 52}

    for factor_type in ["TF", "RBP"]:
        sub = data[data["type"] == factor_type]
        stat = stats[stats["type"] == factor_type].iloc[0]
        center = centers[factor_type]
        for group in ["prediction", "control"]:
            vals = sub.loc[sub["group"] == group, "all_events"].dropna().astype(float).values
            label_side = "left" if group == "prediction" else "right"
            draw_mean_box(
                draw,
                vals,
                center + offsets[group],
                box_width,
                y_to_px,
                COLORS[group],
                small_font,
                label_side,
                center_stat="mean",
            )
        draw_centered_text(draw, (center, plot_bottom + 42), labels[factor_type], (17, 24, 39), label_font)
        data_max = sub["all_events"].astype(float).max()
        p_y = y_to_px(data_max * 1.08)
        draw_centered_text(
            draw,
            (center, p_y - 12),
            p_label(stat["p_two_sided"], "Permutation p"),
            (55, 65, 81),
            small_font,
        )

    draw_rotated_ylabel(image, "Event count", (16, int(height / 2 - 145)), label_font)

    legend_y = 95
    legend_x = 85
    for i, (name, color) in enumerate([("Prediction", COLORS["prediction"]), ("Control", COLORS["control"])]):
        x = legend_x + i * 172
        draw.ellipse([x, legend_y - 9, x + 18, legend_y + 9], fill=color)
        draw.text((x + 30, legend_y), name, fill=(17, 24, 39), font=legend_font, anchor="lm")
    mean_x = legend_x + 345
    draw.line([mean_x, legend_y, mean_x + 34, legend_y], fill=(17, 24, 39), width=4)
    draw.text((mean_x + 46, legend_y), "Mean", fill=(17, 24, 39), font=legend_font, anchor="lm")
    image.save(out_png)


def main():
    all_data = []
    stats = []
    pngs = {}
    for factor_type, input_path in [("TF", TF_INPUT), ("RBP", RBP_INPUT)]:
        df = pd.read_csv(input_path, sep="\t").fillna("")
        data = build_data(df, factor_type)
        stat = run_stats(data, factor_type)
        all_data.append(data)
        stats.append(stat)
        data.to_csv(OUT_DIR / f"{factor_type.lower()}_all_prediction_only_event_counts.tsv", sep="\t", index=False)
        pd.DataFrame([stat]).to_csv(OUT_DIR / f"{factor_type.lower()}_all_prediction_only_stats.tsv", sep="\t", index=False)
        png = OUT_DIR / f"{factor_type.lower()}_all_prediction_only.png"
        draw_single_panel(data, stat, factor_type, png)
        pngs[factor_type] = png

    combined_data = pd.concat(all_data, ignore_index=True)
    combined_stats = pd.DataFrame(stats)
    combined_data.to_csv(
        OUT_DIR / "tf_rbp_all_prediction_only_event_counts.tsv", sep="\t", index=False
    )
    combined_stats.to_csv(OUT_DIR / "tf_rbp_all_prediction_only_stats.tsv", sep="\t", index=False)
    combined = OUT_DIR / "tf_rbp_all_prediction_only.png"
    draw_combined_panel(combined_data, combined_stats, combined)
    print(f"Wrote {combined}")
    print(combined_stats[["type", "prediction_n", "prediction_mean", "control_n", "control_mean", "p_two_sided"]].to_string(index=False))


if __name__ == "__main__":
    main()
