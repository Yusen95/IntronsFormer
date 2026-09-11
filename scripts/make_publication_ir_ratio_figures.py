#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "outputs/ir_nonir_ratio_analysis/ir_nonir_ratio_combined_rows.tsv"
OUT_DIR = ROOT / "outputs/ir_nonir_ratio_analysis"

CLASS_ORDER = ["positive_only", "both", "negative_only", "control"]
CLASS_LABELS = {
    "positive_only": "IR TF/RBP",
    "both": "IR-nonIR TF/RBP",
    "negative_only": "non-IR TF/RBP",
    "control": "Control",
}
CLASS_COLORS = {
    "positive_only": "#1F77B4",
    "both": "#2CA02C",
    "negative_only": "#D62728",
    "control": "#7F7F7F",
}
CELL_LINE_ORDER = ["HepG2", "K562", "GM12878"]
CATEGORY_ORDER = ["TF", "RBP"]


@dataclass(frozen=True)
class FigureSpec:
    name: str
    panel_label: str
    value_col: str
    title: str
    y_label: str
    parity: float
    y_scale: str
    subtitle_extra: str


FIGURES = [
    FigureSpec(
        name="log2",
        panel_label="A",
        value_col="log2_IR_vs_nonIR_occupancy_ratio",
        title="IR vs nonIR binding occupancy ratio",
        y_label="log2 corrected IR/nonIR occupancy ratio",
        parity=0.0,
        y_scale="linear",
        subtitle_extra="Dashed line = IR/nonIR parity (log2 ratio = 0).",
    ),
    FigureSpec(
        name="raw",
        panel_label="B",
        value_col="raw_occupancy_ratio",
        title="IR/nonIR binding occupancy ratio (raw)",
        y_label="IR/nonIR occupancy ratio (raw; log-scaled axis)",
        parity=1.0,
        y_scale="log",
        subtitle_extra="Dashed line = IR/nonIR parity (raw ratio = 1); axis is log-scaled for readability.",
    ),
    FigureSpec(
        name="raw_linear",
        panel_label="B2",
        value_col="raw_occupancy_ratio",
        title="IR/nonIR binding occupancy ratio (raw, linear axis)",
        y_label="IR/nonIR occupancy ratio (raw)",
        parity=1.0,
        y_scale="linear",
        subtitle_extra="Dashed line = IR/nonIR parity (raw ratio = 1); axis is linear.",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render class-split IR/nonIR ratio figures.")
    parser.add_argument("--input", default=str(INPUT), help="Row-level TSV input.")
    parser.add_argument("--out-dir", default=str(OUT_DIR), help="Output directory.")
    parser.add_argument(
        "--output-prefix",
        default="ir_nonir_event_region",
        help="Filename prefix for generated figures.",
    )
    parser.add_argument(
        "--classes",
        default=",".join(CLASS_ORDER),
        help="Comma-separated class names to include, e.g. positive_only,control.",
    )
    parser.add_argument("--title-suffix", default="", help="Optional text appended to figure titles.")
    parser.add_argument("--subtitle-prefix", default="", help="Optional text prepended to subtitles.")
    return parser.parse_args()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    return (*hex_to_rgb(value), alpha)


def finite(values: pd.Series | np.ndarray | list[float]) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    return arr[np.isfinite(arr)]


def box_stats(values: np.ndarray) -> dict[str, float] | None:
    values = finite(values)
    if len(values) == 0:
        return None
    q1, median, q3 = np.quantile(values, [0.25, 0.5, 0.75])
    iqr = q3 - q1
    low_bound = q1 - 1.5 * iqr
    high_bound = q3 + 1.5 * iqr
    whisker_low = values[values >= low_bound].min()
    whisker_high = values[values <= high_bound].max()
    return {
        "q1": float(q1),
        "median": float(median),
        "q3": float(q3),
        "low": float(whisker_low),
        "high": float(whisker_high),
    }


def nice_ticks(low: float, high: float, count: int = 7) -> list[float]:
    span = high - low
    step_raw = span / max(count - 1, 1)
    magnitude = 10 ** math.floor(math.log10(abs(step_raw)))
    residual = step_raw / magnitude
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
        ticks.append(round(value, 10))
        value += step
    return ticks


def axis_limits(values: np.ndarray, spec: FigureSpec) -> tuple[float, float, list[float]]:
    if spec.y_scale == "log":
        positive = values[values > 0]
        if len(positive) == 0:
            return 0.25, 4.0, [0.25, 0.5, 1, 2, 4]
        low = 2 ** math.floor(math.log2(float(positive.min()) * 0.75))
        high = 2 ** math.ceil(math.log2(float(positive.max()) * 1.15))
        low = min(low, 0.25)
        high = max(high, 4.0)
        ticks = [2 ** i for i in range(-4, 7) if low <= 2 ** i <= high]
        return low, high, ticks
    low = math.floor((float(values.min()) - 0.25) * 2) / 2
    high = math.ceil((float(values.max()) + 0.25) * 2) / 2
    if spec.parity == 1.0:
        low = max(0.0, low)
    return low, high, nice_ticks(low, high)


def build_control_notes(df: pd.DataFrame) -> list[str]:
    notes = []
    for category in CATEGORY_ORDER:
        control_cells = set(
            df.loc[(df["Category"] == category) & (df["Class"] == "control"), "Cell_line"].dropna()
        )
        data_cells = set(df.loc[df["Category"] == category, "Cell_line"].dropna())
        missing = [cell for cell in CELL_LINE_ORDER if cell in data_cells and cell not in control_cells]
        if missing:
            notes.append(f"{category} control absent: {', '.join(missing)}")
    if not notes:
        notes.append("Controls included.")
    return notes


def load_font(size: int, bold: bool = False):
    from PIL import ImageFont

    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size=size)


def format_value(value: float) -> str:
    if abs(value) >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


class FigureCanvas:
    def __init__(self, width: int, height: int, scale: int = 2):
        from PIL import Image, ImageDraw

        self.width = width
        self.height = height
        self.scale = scale
        self.image = Image.new("RGBA", (width * scale, height * scale), (255, 255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
        self.svg: list[str] = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<style>text{font-family:Arial,Helvetica,sans-serif;dominant-baseline:auto;}</style>',
            f'<rect x="0" y="0" width="{width}" height="{height}" fill="#FFFFFF"/>',
        ]

    def s(self, value: float) -> float:
        return value * self.scale

    def rect(self, x0, y0, x1, y1, fill, stroke=None, width=1, opacity=1.0):
        fill_rgba = rgba(fill, round(255 * opacity))
        stroke_rgba = rgba(stroke) if stroke else None
        self.draw.rectangle(
            [self.s(x0), self.s(y0), self.s(x1), self.s(y1)],
            fill=fill_rgba,
            outline=stroke_rgba,
            width=max(1, round(width * self.scale)),
        )
        attrs = [f'x="{x0:.1f}"', f'y="{y0:.1f}"', f'width="{x1 - x0:.1f}"', f'height="{y1 - y0:.1f}"', f'fill="{fill}"']
        if opacity < 1:
            attrs.append(f'fill-opacity="{opacity:.2f}"')
        if stroke:
            attrs.extend([f'stroke="{stroke}"', f'stroke-width="{width:.1f}"'])
        self.svg.append(f"<rect {' '.join(attrs)}/>")

    def line(self, x1, y1, x2, y2, color="#111111", width=1, dash: tuple[int, int] | None = None):
        if dash is None:
            self.draw.line(
                [(self.s(x1), self.s(y1)), (self.s(x2), self.s(y2))],
                fill=rgba(color),
                width=max(1, round(width * self.scale)),
            )
            dash_attr = ""
        else:
            length = math.hypot(self.s(x2 - x1), self.s(y2 - y1))
            if length:
                dx = self.s(x2 - x1) / length
                dy = self.s(y2 - y1) / length
                pos = 0
                on, off = dash[0] * self.scale, dash[1] * self.scale
                sx1, sy1 = self.s(x1), self.s(y1)
                while pos < length:
                    end = min(pos + on, length)
                    self.draw.line(
                        [(sx1 + dx * pos, sy1 + dy * pos), (sx1 + dx * end, sy1 + dy * end)],
                        fill=rgba(color),
                        width=max(1, round(width * self.scale)),
                    )
                    pos += on + off
            dash_attr = f' stroke-dasharray="{dash[0]} {dash[1]}"'
        self.svg.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width:.1f}"{dash_attr}/>'
        )

    def circle(self, cx, cy, r, fill, stroke="#FFFFFF", width=0.55, opacity=1.0):
        self.draw.ellipse(
            [self.s(cx - r), self.s(cy - r), self.s(cx + r), self.s(cy + r)],
            fill=rgba(fill, round(255 * opacity)),
            outline=rgba(stroke) if stroke else None,
            width=max(1, round(width * self.scale)),
        )
        attrs = [f'cx="{cx:.1f}"', f'cy="{cy:.1f}"', f'r="{r:.1f}"', f'fill="{fill}"']
        if opacity < 1:
            attrs.append(f'fill-opacity="{opacity:.2f}"')
        if stroke:
            attrs.extend([f'stroke="{stroke}"', f'stroke-width="{width:.2f}"'])
        self.svg.append(f"<circle {' '.join(attrs)}/>")

    def text(self, x, y, label, size=10, anchor="middle", fill="#111111", bold=False, rotate=None):
        from PIL import Image, ImageDraw

        label = str(label)
        weight = "bold" if bold else None
        transform = f' transform="rotate({rotate:.1f} {x:.1f} {y:.1f})"' if rotate is not None else ""
        weight_attr = f' font-weight="{weight}"' if weight else ""
        self.svg.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{weight_attr}{transform}>{esc(label)}</text>'
        )

        pil_anchor = {"start": "lm", "middle": "mm", "end": "rm"}.get(anchor, anchor)
        font = load_font(size * self.scale, bold=bold)
        color = rgba(fill)
        if rotate is None:
            self.draw.text((self.s(x), self.s(y)), label, font=font, fill=color, anchor=pil_anchor)
            return

        bbox = self.draw.textbbox((0, 0), label, font=font)
        tile = Image.new("RGBA", (max(1, bbox[2] - bbox[0] + 8), max(1, bbox[3] - bbox[1] + 8)), (255, 255, 255, 0))
        tile_draw = ImageDraw.Draw(tile)
        tile_draw.text((4 - bbox[0], 4 - bbox[1]), label, font=font, fill=color)
        rotated = tile.rotate(-rotate, expand=True, resample=Image.Resampling.BICUBIC)
        px, py = self.s(x), self.s(y)
        if pil_anchor.endswith("e"):
            paste_x = int(px - rotated.width)
        elif pil_anchor.endswith("w"):
            paste_x = int(px)
        else:
            paste_x = int(px - rotated.width / 2)
        if pil_anchor.startswith(("a", "t")):
            paste_y = int(py)
        elif pil_anchor.startswith(("d", "b")):
            paste_y = int(py - rotated.height)
        else:
            paste_y = int(py - rotated.height / 2)
        self.image.alpha_composite(rotated, (paste_x, paste_y))

    def save(self, svg_path: Path, png_path: Path):
        self.svg.append("</svg>")
        svg_path.write_text("\n".join(self.svg) + "\n", encoding="utf-8")
        self.image.convert("RGB").save(png_path, quality=95)


def render(
    df: pd.DataFrame,
    spec: FigureSpec,
    out_dir: Path,
    output_prefix: str,
    title_suffix: str = "",
    subtitle_prefix: str = "",
    class_order: list[str] | None = None,
) -> tuple[Path, Path]:
    class_order = class_order or CLASS_ORDER
    panel_w = 390
    panel_h = 310
    left = 60
    right = 18
    top = 42
    bottom = 76
    header_h = 112
    legend_w = 210
    width = panel_w * len(CELL_LINE_ORDER) + legend_w
    height = header_h + panel_h * len(CATEGORY_ORDER) + 50

    plot_df = df[df[spec.value_col].replace([np.inf, -np.inf], np.nan).notna()].copy()
    plot_df = plot_df[plot_df["Class"].isin(class_order)].copy()
    values = finite(plot_df[spec.value_col])
    y_low, y_high, y_ticks = axis_limits(values, spec)
    control_notes = build_control_notes(plot_df)
    canvas = FigureCanvas(width, height)
    rng = np.random.default_rng(7)

    def y_transform(value: float) -> float:
        return math.log10(value) if spec.y_scale == "log" else value

    y_low_t = y_transform(y_low)
    y_high_t = y_transform(y_high)

    def y_map(value: float, plot_y: float, plot_h: float) -> float:
        transformed = y_transform(value)
        return plot_y + plot_h - (transformed - y_low_t) / (y_high_t - y_low_t) * plot_h

    title = f"{spec.title}{title_suffix}"
    subtitle = f"{subtitle_prefix}Each point = one ENCODE peak row; box = IQR; black line = median. {spec.subtitle_extra}"
    canvas.text(26, 34, spec.panel_label, 20, anchor="start", bold=True)
    canvas.text(56, 34, title, 18, anchor="start", bold=True)
    canvas.text(
        56,
        58,
        "Baseline14 event-region overlap; first introns excluded; length-adjusted nonIR; start-in-gene filter",
        11,
        anchor="start",
        fill="#4B5563",
    )
    canvas.text(
        56,
        78,
        subtitle,
        11,
        anchor="start",
        fill="#4B5563",
    )

    legend_x = panel_w * len(CELL_LINE_ORDER) + 35
    legend_y = 130
    canvas.text(legend_x, legend_y - 20, "Class", 12, anchor="start", bold=True)
    for i, class_name in enumerate(class_order):
        y = legend_y + i * 28
        color = CLASS_COLORS[class_name]
        canvas.rect(legend_x, y - 12, legend_x + 14, y + 2, color, stroke=color, opacity=0.45, width=1.2)
        canvas.circle(legend_x + 7, y - 5, 3.5, color, stroke=None, opacity=0.85)
        canvas.text(legend_x + 24, y, CLASS_LABELS[class_name], 11, anchor="start")
    canvas.text(legend_x, legend_y + 132, "n = peak rows", 10, anchor="start", fill="#4B5563")
    canvas.text(legend_x, legend_y + 150, "t = unique targets", 10, anchor="start", fill="#4B5563")
    for i, note in enumerate(control_notes):
        canvas.text(legend_x, legend_y + 178 + i * 16, note, 10, anchor="start", fill="#B45309", bold=(i == 0))

    for row_i, category in enumerate(CATEGORY_ORDER):
        for col_i, cell_line in enumerate(CELL_LINE_ORDER):
            x0 = col_i * panel_w
            y0 = header_h + row_i * panel_h
            plot_x = x0 + left
            plot_y = y0 + top
            plot_w = panel_w - left - right
            plot_h = panel_h - top - bottom
            panel = plot_df[(plot_df["Category"] == category) & (plot_df["Cell_line"] == cell_line)].copy()

            canvas.rect(x0 + 10, y0 + 8, x0 + panel_w - 10, y0 + panel_h - 8, "#FFFFFF", stroke="#D1D5DB")
            canvas.text(x0 + panel_w / 2, y0 + 27, f"{category} | {cell_line}", 12, bold=True)

            for tick in y_ticks:
                if y_low <= tick <= y_high:
                    ty = y_map(tick, plot_y, plot_h)
                    canvas.line(plot_x, ty, plot_x + plot_w, ty, "#E5E7EB", width=0.8)
                    canvas.text(plot_x - 8, ty + 3, f"{tick:g}", 9, anchor="end", fill="#4B5563")

            parity_y = y_map(spec.parity, plot_y, plot_h)
            canvas.line(plot_x, parity_y, plot_x + plot_w, parity_y, "#111111", width=1, dash=(4, 3))
            canvas.line(plot_x, plot_y + plot_h, plot_x + plot_w, plot_y + plot_h, "#111827")
            canvas.line(plot_x, plot_y, plot_x, plot_y + plot_h, "#111827")

            if panel.empty:
                canvas.text(x0 + panel_w / 2, plot_y + plot_h / 2, "No data", 12, fill="#6B7280")
                continue

            group_step = plot_w / len(class_order)
            for group_i, class_name in enumerate(class_order):
                group = panel[panel["Class"] == class_name]
                group_values = finite(group[spec.value_col])
                if spec.y_scale == "log":
                    group_values = group_values[group_values > 0]
                cx = plot_x + group_step * (group_i + 0.5)
                color = CLASS_COLORS[class_name]
                label = CLASS_LABELS[class_name]

                if len(group_values) == 0:
                    canvas.text(cx, plot_y + plot_h / 2, "NA", 9, fill="#9CA3AF")
                    canvas.text(cx, plot_y + plot_h + 18, label, 9, anchor="end", fill="#6B7280", rotate=-30)
                    canvas.text(cx, plot_y + plot_h + 35, "n=0", 8, fill="#9CA3AF")
                    continue

                stats = box_stats(group_values)
                assert stats is not None
                box_w = min(32, group_step * 0.48)
                q1_y = y_map(stats["q1"], plot_y, plot_h)
                q3_y = y_map(stats["q3"], plot_y, plot_h)
                med_y = y_map(stats["median"], plot_y, plot_h)
                low_y = y_map(stats["low"], plot_y, plot_h)
                high_y = y_map(stats["high"], plot_y, plot_h)
                canvas.line(cx, high_y, cx, low_y, color, width=1.4)
                canvas.line(cx - box_w / 3, high_y, cx + box_w / 3, high_y, color, width=1.4)
                canvas.line(cx - box_w / 3, low_y, cx + box_w / 3, low_y, color, width=1.4)
                canvas.rect(cx - box_w / 2, min(q1_y, q3_y), cx + box_w / 2, max(q1_y, q3_y), color, stroke=color, opacity=0.30, width=1.2)
                canvas.line(cx - box_w / 2, med_y, cx + box_w / 2, med_y, "#111111", width=1.6)

                for value in group_values:
                    jitter = float(rng.normal(0, min(7.0, group_step * 0.10)))
                    canvas.circle(cx + jitter, y_map(value, plot_y, plot_h), 3.2, color, opacity=0.82)

                canvas.text(cx, med_y - 5, format_value(stats["median"]), 8, fill="#111111", bold=True)
                canvas.text(cx, plot_y + plot_h + 18, label, 9, anchor="end", rotate=-30)
                canvas.text(
                    cx,
                    plot_y + plot_h + 35,
                    f"n={len(group)}, t={group['Original_ID'].nunique()}",
                    8,
                    fill="#4B5563",
                )

            if col_i == 0:
                canvas.text(x0 + 17, plot_y + plot_h / 2, spec.y_label, 10, rotate=-90)

    interpretation = (
        "Interpretation: values above 1 indicate higher IR event occupancy; values below 1 indicate higher nonIR event occupancy."
        if spec.parity == 1.0
        else "Interpretation: values above 0 indicate higher IR event occupancy; values below 0 indicate higher nonIR event occupancy."
    )
    canvas.text(56, height - 20, interpretation, 10, anchor="start", fill="#4B5563")

    svg_path = out_dir / f"{output_prefix}_{spec.name}_ratio_boxplot_publication.svg"
    png_path = out_dir / f"{output_prefix}_{spec.name}_ratio_boxplot_publication.png"
    canvas.save(svg_path, png_path)
    return svg_path, png_path


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.input, sep="\t")
    class_order = [item.strip() for item in args.classes.split(",") if item.strip()]
    for spec in FIGURES:
        svg_path, png_path = render(
            df,
            spec,
            out_dir,
            args.output_prefix,
            title_suffix=args.title_suffix,
            subtitle_prefix=args.subtitle_prefix,
            class_order=class_order,
        )
        print(svg_path)
        print(png_path)


if __name__ == "__main__":
    main()
