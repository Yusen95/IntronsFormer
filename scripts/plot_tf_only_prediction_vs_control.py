from pathlib import Path
import argparse

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs" / "encode_current_prediction_perturbation_check"
INPUT = OUT_DIR / "encode_prediction_vs_control_event_counts.tsv"
WILCOXON = OUT_DIR / "tf_rbp_encode_prediction_vs_control_wilcoxon_rank_sum.tsv"
CELLLINE_ROWS = OUT_DIR / "cellline_stratified_prediction_control_rows.tsv"
CELLLINE_WILCOXON = OUT_DIR / "cellline_stratified_prediction_control_wilcoxon.tsv"

METRICS = [
    ("all_events", "All events"),
    ("up_events", "Up-regulated"),
    ("down_events", "Down-regulated"),
]

COLORS = {
    "prediction": (59, 130, 246),
    "control": (249, 115, 22),
}


def font(size, bold=False):
    names = ["arialbd.ttf", "arial.ttf"] if bold else ["arial.ttf", "calibri.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def load_wilcoxon_pvalues(factor_type, cell_line=None, stratification="encode_support"):
    if cell_line:
        if not CELLLINE_WILCOXON.exists():
            return {}
        df = pd.read_csv(CELLLINE_WILCOXON, sep="\t")
        df = df[
            (df["stratification"] == stratification)
            & (df["type"] == factor_type)
            & (df["cell_line"] == cell_line)
        ]
    elif not WILCOXON.exists():
        return {}
    else:
        df = pd.read_csv(WILCOXON, sep="\t")
        df = df[df["type"] == factor_type]
    return {
        row["metric"]: row["p_value_two_sided_approx"]
        for _, row in df.iterrows()
    }


def blend(color, alpha, bg=(255, 255, 255)):
    return tuple(int(color[i] * alpha + bg[i] * (1 - alpha)) for i in range(3))


def draw_centered_text(draw, xy, text, fill, font_obj, anchor="mm"):
    draw.text(xy, str(text), fill=fill, font=font_obj, anchor=anchor)


def format_sig(value, digits=3):
    return f"{float(value):.{digits}g}"


def draw_mean_box(
    draw,
    values,
    x,
    width,
    y_to_px,
    color,
    label_font=None,
    label_side="right",
    center_stat="mean",
):
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return

    q1, q3 = np.percentile(values, [25, 75])
    vmin, vmax = values.min(), values.max()
    if center_stat == "median":
        center_value = float(np.median(values))
    else:
        center_value = float(values.mean())

    x0 = x - width / 2
    x1 = x + width / 2
    q1_px = y_to_px(q1)
    q3_px = y_to_px(q3)
    vmin_px = y_to_px(vmin)
    vmax_px = y_to_px(vmax)
    center_px = y_to_px(center_value)

    box_top = min(q1_px, q3_px)
    box_bottom = max(q1_px, q3_px)
    edge = (17, 24, 39)
    fill = blend(color, 0.22)

    draw.rectangle([x0, box_top, x1, box_bottom], fill=fill, outline=edge, width=2)
    draw.line([x, vmax_px, x, box_top], fill=edge, width=2)
    draw.line([x, box_bottom, x, vmin_px], fill=edge, width=2)
    draw.line([x - width * 0.28, vmax_px, x + width * 0.28, vmax_px], fill=edge, width=2)
    draw.line([x - width * 0.28, vmin_px, x + width * 0.28, vmin_px], fill=edge, width=2)
    draw.line([x0, center_px, x1, center_px], fill=edge, width=4)

    jitter = np.linspace(-width * 0.22, width * 0.22, len(values))
    if len(values) > 1:
        rng = np.random.default_rng(7)
        jitter = rng.permutation(jitter)
    for offset, value in zip(jitter, values):
        cx = x + offset
        cy = y_to_px(value)
        r = 7
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color, outline=(255, 255, 255), width=2)

    if label_font is not None:
        label = format_sig(center_value)
        text_y = center_px
        if label_side == "left":
            text_x = x0 - 10
            anchor = "rm"
        else:
            text_x = x1 + 10
            anchor = "lm"
        bbox = draw.textbbox((text_x, text_y), label, font=label_font, anchor=anchor)
        pad = 4
        draw.rounded_rectangle(
            [bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad],
            radius=5,
            fill=(255, 255, 255),
        )
        draw.text((text_x, text_y), label, fill=edge, font=label_font, anchor=anchor)


def draw_rotated_ylabel(image, text, pos, font_obj):
    temp = Image.new("RGBA", (360, 60), (255, 255, 255, 0))
    temp_draw = ImageDraw.Draw(temp)
    temp_draw.text((180, 30), text, fill=(17, 24, 39), font=font_obj, anchor="mm")
    rotated = temp.rotate(90, expand=True)
    image.paste(rotated, pos, rotated)


def draw_plot(
    data,
    pvals,
    factor_type,
    cell_line=None,
    pvalue_prefix="p",
    secondary_pvals=None,
    secondary_pvalue_prefix="Wilcoxon p",
    center_stat="mean",
):
    width, height = 1600, 1000
    margin_left, margin_right = 150, 70
    margin_top, margin_bottom = 155, 160
    plot_left = margin_left
    plot_right = width - margin_right
    plot_top = margin_top
    plot_bottom = height - margin_bottom
    plot_width = plot_right - plot_left
    plot_height = plot_bottom - plot_top

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    title_font = font(34, bold=True)
    label_font = font(25)
    small_font = font(21)
    tick_font = font(22)
    legend_font = font(22)

    metrics = [metric for metric, _label in METRICS]
    ymax = max(data[metrics].astype(float).max().max(), 1) * 1.22

    def y_to_px(value):
        return plot_bottom - (float(value) / ymax) * plot_height

    title = f"{factor_type} prediction vs control iDiffIR event counts"
    if cell_line:
        if cell_line == "combined":
            title = f"{factor_type} K562/HepG2 prediction vs control iDiffIR event counts"
        else:
            title = f"{factor_type} {cell_line} prediction vs control iDiffIR event counts"

    draw.text(
        (width / 2, 58),
        title,
        fill=(17, 24, 39),
        font=title_font,
        anchor="mm",
    )

    axis = (17, 24, 39)
    grid = (229, 231, 235)
    for tick in np.linspace(0, ymax / 1.22, 6):
        y = y_to_px(tick)
        draw.line([plot_left, y, plot_right, y], fill=grid, width=2)
        draw.text((plot_left - 16, y), f"{int(round(tick))}", fill=(55, 65, 81), font=tick_font, anchor="rm")
    draw.line([plot_left, plot_bottom, plot_right, plot_bottom], fill=axis, width=2)
    draw.line([plot_left, plot_top, plot_left, plot_bottom], fill=axis, width=2)

    centers = np.linspace(plot_left + plot_width * 0.17, plot_right - plot_width * 0.17, len(METRICS))
    box_width = 76
    offsets = {"prediction": -52, "control": 52}

    for x, (metric, label) in zip(centers, METRICS):
        for group in ["prediction", "control"]:
            vals = data.loc[data["group"] == group, metric].astype(float).values
            label_side = "left" if group == "prediction" else "right"
            draw_mean_box(
                draw,
                vals,
                x + offsets[group],
                box_width,
                y_to_px,
                COLORS[group],
                small_font,
                label_side,
                center_stat,
            )

        draw_centered_text(draw, (x, plot_bottom + 48), label, (17, 24, 39), label_font)
        p = pvals.get(metric)
        if p is not None:
            data_max = data[metric].astype(float).max()
            p_y = y_to_px(data_max * 1.08)
            draw_centered_text(draw, (x, p_y - 12), p_label(p, pvalue_prefix), (55, 65, 81), small_font)
            if secondary_pvals is not None and metric in secondary_pvals:
                draw_centered_text(
                    draw,
                    (x, p_y + 15),
                    p_label(secondary_pvals[metric], secondary_pvalue_prefix),
                    (55, 65, 81),
                    small_font,
                )

    draw_rotated_ylabel(image, "Event count", (24, int(height / 2 - 180)), label_font)

    legend_y = 108
    legend_x = 115
    for i, (name, color) in enumerate([("Prediction", COLORS["prediction"]), ("Control", COLORS["control"])]):
        x = legend_x + i * 185
        draw.ellipse([x, legend_y - 9, x + 18, legend_y + 9], fill=color)
        draw.text((x + 30, legend_y), name, fill=(17, 24, 39), font=legend_font, anchor="lm")
    mean_x = legend_x + 380
    draw.line([mean_x, legend_y, mean_x + 34, legend_y], fill=(17, 24, 39), width=4)
    center_label = "Median" if center_stat == "median" else "Mean"
    draw.text((mean_x + 46, legend_y), center_label, fill=(17, 24, 39), font=legend_font, anchor="lm")

    return image


def p_label(pvalue, prefix="p"):
    if pd.isna(pvalue):
        return ""
    return f"{prefix}={format_sig(pvalue)}"


def default_output_paths(factor_type):
    prefix = factor_type.lower()
    return (
        OUT_DIR / f"{prefix}_only_prediction_vs_control_mean_line_boxplot.png",
        OUT_DIR / f"{prefix}_only_prediction_vs_control_summary.tsv",
    )


def cellline_output_paths(factor_type, cell_line, stratification):
    prefix = factor_type.lower()
    cell = cell_line.lower()
    return (
        OUT_DIR / f"{prefix}_{cell}_{stratification}_prediction_vs_control_mean_line_boxplot.png",
        OUT_DIR / f"{prefix}_{cell}_{stratification}_prediction_vs_control_summary.tsv",
    )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["TF", "RBP"], default="TF")
    parser.add_argument("--cell-line", choices=["HepG2", "K562"], default=None)
    parser.add_argument("--stratification", choices=["explicit", "encode_support"], default="encode_support")
    return parser.parse_args()


def main():
    args = parse_args()
    factor_type = args.type
    if args.cell_line:
        png_path, summary_path = cellline_output_paths(factor_type, args.cell_line, args.stratification)
        df = pd.read_csv(CELLLINE_ROWS, sep="\t")
        data = df[
            (df["stratification"] == args.stratification)
            & (df["type"] == factor_type)
            & (df["assigned_cell_line"] == args.cell_line)
        ].copy()
    else:
        png_path, summary_path = default_output_paths(factor_type)
        df = pd.read_csv(INPUT, sep="\t")
        data = df[df["type"] == factor_type].copy()

    summary_rows = []
    for group in ["prediction", "control"]:
        sub = data[data["group"] == group]
        for metric, _label in METRICS:
            vals = pd.to_numeric(sub[metric], errors="coerce").dropna()
            summary_rows.append(
                {
                    "type": factor_type,
                    "group": group,
                    "metric": metric,
                    "n": len(vals),
                    "mean": vals.mean() if len(vals) else np.nan,
                    "median": vals.median() if len(vals) else np.nan,
                    "min": vals.min() if len(vals) else np.nan,
                    "max": vals.max() if len(vals) else np.nan,
                }
            )
    pd.DataFrame(summary_rows).to_csv(summary_path, sep="\t", index=False)

    pvals = load_wilcoxon_pvalues(factor_type, args.cell_line, args.stratification)

    image = draw_plot(data, pvals, factor_type, args.cell_line)
    image.save(png_path)
    print(f"Wrote {png_path}")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
