#!/usr/bin/env python3

import argparse
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(os.environ.get("BASE_DIR", os.path.expanduser("~/bigdata")))
CELL_LINES = ["K562", "HepG2"]
CLASSES = ["positive_only", "both", "negative_only", "neutral_only", "control"]
CATEGORIES = ["TF", "RBP"]

CLASS_LABEL_TEMPLATES = {
    "positive_only": "IR {category}",
    "negative_only": "non-IR {category}",
    "both": "shared {category}",
    "control": "control {category}",
    "neutral_only": "neutral {category}",
}

CLASS_DEFINITION_TEMPLATES = {
    "positive_only": "{category} candidates identified from motifs found in retained-intron regions",
    "negative_only": "{category} candidates identified from motifs found in non-retained intron regions",
    "both": "{category} candidates identified from motifs found in both retained-intron and non-retained intron regions",
    "control": "background/control {category} set processed with the same pipeline",
    "neutral_only": "{category} candidates from the neutral/background motif group",
}

METRICS = {
    "event_region": (
        "IR_event_region_occupancy_%",
        "NonIR_event_region_occupancy_%",
        "event_region_fisher_p_value",
        "event region",
    ),
    "intron_only": (
        "IR_intron_only_occupancy_%",
        "NonIR_intron_only_occupancy_%",
        "intron_only_fisher_p_value",
        "intron only",
    ),
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": False,
    "figure.dpi": 160,
    "savefig.dpi": 400,
    "savefig.facecolor": "white",
})


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=str(BASE_DIR / "baseline_like_overlap_three_class" / "baseline_like_overlap_three_class_summary.tsv"),
    )
    parser.add_argument(
        "--out_dir",
        default=str(BASE_DIR / "baseline_like_overlap_three_class_plots_6figures"),
    )
    parser.add_argument("--metric", choices=sorted(METRICS), default="event_region")
    parser.add_argument("--sort_by", choices=["ir", "nonir", "delta", "target"], default="ir")
    return parser.parse_args()


def p_label(p):
    if pd.isna(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def sort_panel(df, sort_by, ir_col, nonir_col):
    if sort_by == "target":
        return df.sort_values("Target")
    if sort_by == "nonir":
        return df.sort_values(nonir_col)
    if sort_by == "delta":
        return df.sort_values("delta_occupancy_%")
    return df.sort_values(ir_col)


def class_label(class_name, category):
    template = CLASS_LABEL_TEMPLATES.get(class_name, class_name.replace("_", " "))
    return template.format(category=category)


def class_definition(class_name, category):
    template = CLASS_DEFINITION_TEMPLATES.get(class_name, "")
    return template.format(category=category) if template else ""


def assay_label(category):
    return "ChIP-seq" if category == "TF" else "eCLIP"


def plot_one_combo(df, class_name, category, out_dir, metric, sort_by):
    ir_col, nonir_col, _p_col, metric_label = METRICS[metric]
    combo = df[(df["Class"] == class_name) & (df["Category"] == category)].copy()
    if combo.empty:
        print(f"[WARN] No rows for {class_name} {category}")
        return

    combo["delta_occupancy_%"] = combo[ir_col] - combo[nonir_col]
    max_rows = max(len(combo[combo["Cell_line"] == cell_line]) for cell_line in CELL_LINES)
    fig_h = max(4.0, 0.22 * max_rows + 2.0)

    fig, axes = plt.subplots(
        1,
        len(CELL_LINES),
        figsize=(18, fig_h),
        gridspec_kw={"wspace": 0.55},
    )

    for ax, cell_line in zip(axes, CELL_LINES):
        sub = combo[combo["Cell_line"] == cell_line].copy()
        if sub.empty:
            ax.axis("off")
            ax.set_title(f"{cell_line}\nno data")
            continue

        sub = sort_panel(sub, sort_by, ir_col, nonir_col)
        y = np.arange(len(sub))
        height = 0.36

        ax.barh(y + height / 2, sub[ir_col], height=height, label="IR", color="#4C78A8")
        ax.barh(y - height / 2, sub[nonir_col], height=height, label="non-IR", color="#F58518")

        ax.set_yticks(y)
        ax.set_yticklabels(sub["Target"])
        ax.set_xlabel("Occupancy (%)")
        ax.set_title(cell_line)

        xmax = max(sub[ir_col].max(), sub[nonir_col].max())
        xmax = xmax * 1.25 if xmax > 0 else 1
        ax.set_xlim(0, xmax)

    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.01))

    fig.suptitle(
        f"{class_label(class_name, category)}: {assay_label(category)} occupancy in IR vs non-IR",
        fontsize=12,
        y=1.01,
    )

    safe_class = class_name.replace("_only", "")
    for ext in ["png", "pdf"]:
        out = out_dir / f"baseline_like_{metric}_{safe_class}_{category}_K562_HepG2.{ext}"
        fig.savefig(out, bbox_inches="tight")
        print(f"[INFO] Saved {out}")

    plt.close(fig)


def main():
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input, sep="\t")
    df = df[df["Cell_line"].isin(CELL_LINES)].copy()
    df["Candidate_set_label"] = df.apply(lambda row: class_label(row["Class"], row["Category"]), axis=1)
    df["Candidate_set_definition"] = df.apply(
        lambda row: class_definition(row["Class"], row["Category"]),
        axis=1,
    )
    df.to_csv(out_dir / f"baseline_like_{args.metric}_plot_input.tsv", sep="\t", index=False)

    term_rows = []
    for class_name in CLASSES:
        for category in CATEGORIES:
            term_rows.append({
                "Class": class_name,
                "Category": category,
                "Short_label": class_label(class_name, category),
                "Full_definition": class_definition(class_name, category),
            })
    pd.DataFrame(term_rows).to_csv(out_dir / "candidate_set_term_definitions.tsv", sep="\t", index=False)

    classes = [class_name for class_name in CLASSES if class_name in set(df["Class"])]
    categories = [category for category in CATEGORIES if category in set(df["Category"])]

    for class_name in classes:
        for category in categories:
            plot_one_combo(df, class_name, category, out_dir, args.metric, args.sort_by)


if __name__ == "__main__":
    main()
