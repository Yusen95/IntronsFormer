from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "outputs" / "figure5_original_style" / "knockdown_results_draft_compatible.csv"
TF_INPUT = ROOT / "outputs/figure5_original_style/knockdown_results_download_snapshot.csv"
OUT_DIR = ROOT / "outputs" / "figure5_submission_current_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COMBINED_PNG = OUT_DIR / "Figure5_knockdown_TF_all_IR_shared_selected_nonIR_RBP_K562_HepG2_submission.png"
COMBINED_PDF = OUT_DIR / "Figure5_knockdown_TF_all_IR_shared_selected_nonIR_RBP_K562_HepG2_submission.pdf"
TF_PNG = OUT_DIR / "Figure5A_TF_all_IR_top_shared_selected_nonIR_submission.png"
RBP_PNG = OUT_DIR / "Figure5B_RBP_knockdown_K562_HepG2_top_by_class_submission.png"
SELECTED_TSV = OUT_DIR / "Figure5_selected_targets_TF_all_IR_shared_selected_nonIR.tsv"

GROUP_ORDER = ["P", "B", "N"]
GROUP_COLORS = {
    "P": (76, 120, 168),
    "B": (235, 195, 76),
    "N": (228, 87, 86),
}
GROUP_NAMES = {
    "P": "IR",
    "B": "shared",
    "N": "non-IR",
}


def font(size, bold=False):
    names = ["arialbd.ttf", "Arial Bold.ttf"] if bold else ["arial.ttf", "Arial.ttf", "calibri.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)


def text_width(draw, text, text_font):
    box = draw.textbbox((0, 0), str(text), font=text_font)
    return box[2] - box[0]


def map_group(value):
    s = str(value).strip().lower()
    if s.startswith("positive"):
        return "P"
    if s.startswith("both"):
        return "B"
    if s.startswith("negative"):
        return "N"
    return None


def normalize_cell_line(value):
    s = str(value).strip()
    if not s or s.lower() in {"nan", "na"}:
        return "K562"
    return s


def prepare_data(input_path):
    df = pd.read_csv(input_path).rename(
        columns={
            "Regulator": "regulator",
            "Regulator_Type": "type",
            "Candidate_Group": "group",
            "Cell_Line": "cell_line",
            "iDiffIR_Down": "downregulated_ir",
            "iDiffIR_Up": "upregulated_ir",
        }
    )
    df["group"] = df["group"].apply(map_group)
    df = df[df["group"].isin(GROUP_ORDER)].copy()
    df["type"] = df["type"].astype(str).str.upper()
    df["cell_line"] = df["cell_line"].apply(normalize_cell_line)
    df["downregulated_ir"] = pd.to_numeric(df["downregulated_ir"], errors="coerce").fillna(0).astype(int)
    df["upregulated_ir"] = pd.to_numeric(df["upregulated_ir"], errors="coerce").fillna(0).astype(int)
    df["total"] = df["downregulated_ir"].abs() + df["upregulated_ir"].abs()
    return df


def select_tf_panel(tf_df, current_df):
    tf = tf_df[tf_df["type"] == "TF"].copy()
    ir_found = tf[tf["group"] == "P"].sort_values(
        ["total", "downregulated_ir", "upregulated_ir", "regulator"],
        ascending=[False, False, False, True],
    )
    shared = tf[tf["group"] == "B"].sort_values(
        ["total", "downregulated_ir", "upregulated_ir", "regulator"],
        ascending=[False, False, False, True],
    ).head(4)
    non_ir = current_df[
        (current_df["type"] == "TF")
        & (current_df["group"] == "N")
        & (current_df["regulator"].isin(["GLI1", "PPARD", "FOXF2"]))
    ].copy()
    non_ir["_target_order"] = non_ir["regulator"].map({"FOXF2": 0, "GLI1": 1, "PPARD": 2})
    non_ir = non_ir.sort_values(["_target_order", "regulator"]).drop(columns=["_target_order"])
    out = pd.concat([ir_found, shared, non_ir], ignore_index=True)
    out["_group_order"] = out["group"].map({"P": 0, "B": 1, "N": 2})
    return out.sort_values(["_group_order", "total"], ascending=[True, False]).drop(columns=["_group_order"])


def top_by_class(df, regulator_type, n_per_class=6):
    sub = df[df["type"] == regulator_type].copy()
    selected = []
    for group in GROUP_ORDER:
        block = sub[sub["group"] == group].sort_values(
            ["total", "downregulated_ir", "upregulated_ir", "regulator"],
            ascending=[False, False, False, True],
        )
        selected.append(block.head(n_per_class))
    out = pd.concat(selected, ignore_index=True)
    out["_group_order"] = out["group"].map({g: i for i, g in enumerate(GROUP_ORDER)})
    out = out.sort_values(["_group_order", "total"], ascending=[True, False]).copy()
    return out.drop(columns=["_group_order"])


def draw_hatched_rect(draw, rect, fill, outline=(0, 0, 0), width=2, spacing=11):
    x0, y0, x1, y1 = [int(round(v)) for v in rect]
    if x1 < x0:
        x0, x1 = x1, x0
    draw.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=width)
    line_color = tuple(max(0, c - 70) for c in fill)
    h = max(1, y1 - y0)
    for s in range(x0 - h, x1 + h, spacing):
        t0 = max(0.0, (x0 - s) / h)
        t1 = min(1.0, (x1 - s) / h)
        if t0 <= t1:
            xa = s + t0 * h
            ya = y1 - t0 * h
            xb = s + t1 * h
            yb = y1 - t1 * h
            draw.line([xa, ya, xb, yb], fill=line_color, width=2)
    draw.rectangle([x0, y0, x1, y1], outline=outline, width=width)


def draw_panel(sub, panel_label, width=1800, row_height=49, top=92, bottom=88, show_cell_line=True):
    n = len(sub)
    height = top + bottom + n * row_height
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    label_font = font(22)
    tick_font = font(19)
    axis_font = font(20)
    panel_font = font(35, bold=True)

    label_examples = []
    for _, row in sub.iterrows():
        name = str(row["regulator"])
        if show_cell_line:
            name = f"{name} ({row['cell_line']})"
        label_examples.append(name)
    max_label = max(text_width(draw, x, label_font) for x in label_examples)
    left = min(520, max(340, max_label + 55))
    right = width - 80
    plot_top = top
    plot_bottom = top + n * row_height
    center_x = (left + right) / 2
    plot_half = (right - left) / 2

    max_val = max(int(sub["downregulated_ir"].max()), int(sub["upregulated_ir"].max()), 1)
    lim = int(np.ceil(max_val / 100.0) * 100)

    def x_pos(value):
        return center_x + (value / (lim * 1.08)) * plot_half

    axis = (17, 24, 39)
    grid = (229, 231, 235)

    draw.text((26, 34), panel_label, fill=axis, font=panel_font, anchor="lm")
    ticks = list(range(-lim, lim + 1, 100))
    for tick in ticks:
        x = x_pos(tick)
        draw.line([x, plot_top - 8, x, plot_bottom + 7], fill=grid, width=1)
        draw.text((x, plot_bottom + 27), str(abs(tick)), fill=(55, 65, 81), font=tick_font, anchor="mt")

    draw.line([center_x, plot_top - 10, center_x, plot_bottom + 7], fill=(0, 0, 0), width=3)
    draw.line([left, plot_bottom + 7, right, plot_bottom + 7], fill=axis, width=2)

    group_values = sub["group"].tolist()
    for idx in range(1, len(group_values)):
        if group_values[idx] != group_values[idx - 1]:
            y_sep = plot_top + idx * row_height - row_height / 2
            draw.line([left, y_sep, right, y_sep], fill=(0, 0, 0), width=1)

    bar_h = 25
    for i, (_, row) in enumerate(sub.iterrows()):
        y = plot_top + i * row_height + row_height / 2
        group = row["group"]
        color = GROUP_COLORS[group]
        label = str(row["regulator"])
        if show_cell_line:
            label = f"{label} ({row['cell_line']})"
        draw.text((left - 18, y), label, fill=axis, font=label_font, anchor="rm")

        down = int(row["downregulated_ir"])
        up = int(row["upregulated_ir"])
        draw.rectangle([x_pos(-down), y - bar_h / 2, center_x, y + bar_h / 2], fill=color, outline=(0, 0, 0), width=2)
        draw_hatched_rect(draw, [center_x, y - bar_h / 2, x_pos(up), y + bar_h / 2], fill=color)

    draw.text(
        ((left + right) / 2, height - 30),
        "Number of differential IR events (left: down-regulated; right: up-regulated)",
        fill=axis,
        font=axis_font,
        anchor="mm",
    )
    return image


def add_bottom_space(image, extra=125):
    canvas = Image.new("RGB", (image.width, image.height + extra), "white")
    canvas.paste(image, (0, 0))
    return canvas


def draw_legend(image, present_groups):
    draw = ImageDraw.Draw(image)
    legend_font = font(20)
    title_font = font(21, bold=True)
    axis = (17, 24, 39)
    y = image.height - 78
    x = 115
    draw.text((x, y - 32), "Candidate group", fill=axis, font=title_font, anchor="lm")
    for group in GROUP_ORDER:
        if group not in present_groups:
            continue
        draw.rectangle([x, y - 11, x + 32, y + 11], fill=GROUP_COLORS[group], outline=(0, 0, 0), width=1)
        draw.text((x + 43, y), GROUP_NAMES[group], fill=axis, font=legend_font, anchor="lm")
        x += 330 if group == "B" else 205

    x = image.width - 520
    draw.text((x, y - 32), "Direction", fill=axis, font=title_font, anchor="lm")
    draw.rectangle([x, y - 11, x + 32, y + 11], fill="white", outline=(0, 0, 0), width=2)
    draw.text((x + 43, y), "Down-regulated IR events", fill=axis, font=legend_font, anchor="lm")
    y2 = y + 34
    draw_hatched_rect(draw, [x, y2 - 11, x + 32, y2 + 11], fill=(245, 245, 245), width=2)
    draw.text((x + 43, y2), "Up-regulated IR events", fill=axis, font=legend_font, anchor="lm")


def combine_panels(tf_image, rbp_image):
    gap = 48
    width = max(tf_image.width, rbp_image.width)
    height = tf_image.height + rbp_image.height + gap + 120
    canvas = Image.new("RGB", (width, height), "white")
    canvas.paste(tf_image, ((width - tf_image.width) // 2, 0))
    canvas.paste(rbp_image, ((width - rbp_image.width) // 2, tf_image.height + gap))
    return canvas


def main():
    tf_source = TF_INPUT if TF_INPUT.exists() else INPUT
    tf_df = prepare_data(tf_source)
    rbp_df = prepare_data(INPUT)
    tf_top = select_tf_panel(tf_df, rbp_df)
    rbp_top = top_by_class(rbp_df, "RBP", n_per_class=6)

    selected = pd.concat(
        [
            tf_top.assign(panel="TF"),
            rbp_top.assign(panel="RBP"),
        ],
        ignore_index=True,
    )
    selected[
        [
            "panel",
            "regulator",
            "type",
            "cell_line",
            "group",
            "downregulated_ir",
            "upregulated_ir",
            "total",
        ]
    ].to_csv(SELECTED_TSV, sep="\t", index=False)

    tf_panel = draw_panel(tf_top, "a", row_height=49, top=88, bottom=88, show_cell_line=False)
    rbp_panel = draw_panel(rbp_top, "b", row_height=49, top=88, bottom=88, show_cell_line=False)

    tf_single = add_bottom_space(tf_panel)
    draw_legend(tf_single, set(tf_top["group"]))
    tf_single.save(TF_PNG)

    rbp_single = add_bottom_space(rbp_panel)
    draw_legend(rbp_single, set(rbp_top["group"]))
    rbp_single.save(RBP_PNG)

    combined = combine_panels(tf_panel, rbp_panel)
    draw_legend(combined, set(selected["group"]))
    combined.save(COMBINED_PNG)
    combined.save(COMBINED_PDF, "PDF", resolution=300.0)

    print(f"Wrote {COMBINED_PNG}")
    print(f"Wrote {COMBINED_PDF}")
    print(f"Wrote {TF_PNG}")
    print(f"Wrote {RBP_PNG}")
    print(f"Wrote {SELECTED_TSV}")
    print(selected[["panel", "regulator", "cell_line", "group", "downregulated_ir", "upregulated_ir", "total"]].to_string(index=False))


if __name__ == "__main__":
    main()
