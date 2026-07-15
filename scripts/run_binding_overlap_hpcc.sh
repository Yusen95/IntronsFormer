#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${BASE_DIR:-$HOME/bigdata}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SELECTED_TSV="${SELECTED_TSV:-$REPO_DIR/metadata/encode_selected_peaks_pos_both_neg_tsv.tsv}"
DOWNLOAD_SCRIPT="$REPO_DIR/scripts/download_encode_peaks_from_selected_tsv.sh"
OVERLAP_SCRIPT="$REPO_DIR/scripts/09_binding_overlap_analysis.py"
PLOT_SCRIPT="$REPO_DIR/scripts/10_plot_binding_occupancy.py"

OUT_DIR="${OUT_DIR:-$BASE_DIR/baseline14_event_overlap_pos_both_neg_tsv_no_first_intron_length_adjusted_start_in_gene}"
PLOT_DIR="${PLOT_DIR:-$BASE_DIR/baseline14_event_overlap_pos_both_neg_tsv_no_first_intron_length_adjusted_start_in_gene_plots}"

mkdir -p "$BASE_DIR"

for file in "$SELECTED_TSV" "$DOWNLOAD_SCRIPT" "$OVERLAP_SCRIPT" "$PLOT_SCRIPT"; do
  if [ ! -f "$file" ]; then
    echo "[ERROR] Missing required file: $file" >&2
    exit 1
  fi
done

echo "[INFO] Downloading missing ENCODE ChIP-seq/eCLIP peak files"
BASE_DIR="$BASE_DIR" SELECTED_TSV="$SELECTED_TSV" bash "$DOWNLOAD_SCRIPT"

echo "[INFO] Running event-level binding overlap"
python "$OVERLAP_SCRIPT" \
  --base_dir "$BASE_DIR" \
  --selected_tsv "$SELECTED_TSV" \
  --out_dir "$OUT_DIR" \
  --allow_existing_fallback \
  --exclude_first_intron \
  --length_adjust_nonir \
  --length_adjust_sd_multiplier 1.0 \
  --start_in_gene_filter

echo "[INFO] Plotting event-region occupancy"
python "$PLOT_SCRIPT" \
  --input "$OUT_DIR/baseline_like_overlap_three_class_summary.tsv" \
  --out_dir "$PLOT_DIR" \
  --metric event_region

echo "[INFO] Done"
echo "[INFO] Summary: $OUT_DIR/baseline_like_overlap_three_class_summary.tsv"
echo "[INFO] Plots: $PLOT_DIR"
