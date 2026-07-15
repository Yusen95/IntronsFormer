#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${BASE_DIR:-$PWD}"
SELECTED_TSV="${SELECTED_TSV:-encode_selected_peaks_pos_both_neg_tsv.tsv}"

cd "$BASE_DIR"

if [ ! -f "$SELECTED_TSV" ]; then
  echo "[ERROR] Missing selected TSV: $BASE_DIR/$SELECTED_TSV" >&2
  exit 1
fi

tail -n +2 "$SELECTED_TSV" | while IFS=$'\t' read -r \
  Class Category Original_ID ENCODE_Target Cell_Line Experiment Assay Selected_File \
  Assembly Output_Type Biological_Replicates Date_For_Choice Date_Released Date_Created \
  Download_URL Experiment_Link File_Link
do
  if [ -z "$Download_URL" ] || [ -z "$ENCODE_Target" ] || [ -z "$Cell_Line" ]; then
    echo "[WARN] Skipping incomplete row: ${Category} ${Original_ID} ${Cell_Line}" >&2
    continue
  fi

  case "$Assay" in
    *eCLIP*) assay_dir="eCLIP" ;;
    *) assay_dir="ChIP-seq" ;;
  esac

  out_dir="${assay_dir}_${Cell_Line}/${ENCODE_Target}"
  mkdir -p "$out_dir"

  if ls "$out_dir"/*.narrowPeak.bed >/dev/null 2>&1; then
    echo "[SKIP] Existing BED in $out_dir"
    continue
  fi

  rep_label="${Biological_Replicates//,/-}"
  out_bed="${out_dir}/${ENCODE_Target}_${Cell_Line}_${Experiment}_${Selected_File}_${Assembly}_rep${rep_label}.narrowPeak.bed"
  tmp_gz="${out_bed}.gz"

  echo "[GET] ${Class} ${Category} ${ENCODE_Target} ${Cell_Line} ${Experiment} ${Selected_File}"
  wget -c -O "$tmp_gz" "$Download_URL"
  gzip -cd "$tmp_gz" > "$out_bed"
  rm -f "$tmp_gz"
done
