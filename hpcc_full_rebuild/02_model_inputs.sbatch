#!/usr/bin/env bash
#SBATCH --job-name=if_inputs
#SBATCH --partition=batch
#SBATCH --array=0-7%4
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=2-00:00:00
#SBATCH --output=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/logs/model_inputs_%A_%a.out
#SBATCH --error=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/logs/model_inputs_%A_%a.err

set -euo pipefail

RUN=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830
MANIFEST="$RUN/config/samples.tsv"
PYTHON=/rhome/yzhan677/bigdata/.conda/envs/performer/bin/python
FASTA=/rhome/yzhan677/bigdata/Homo_sapiens.GRCh38.dna.primary_assembly.fa
SEED=1

row=$(awk -F '\t' -v n="$SLURM_ARRAY_TASK_ID" 'NR == n + 2 {print; exit}' "$MANIFEST")
IFS=$'\t' read -r CELL LAYOUT READ1S READ2S H3K36 DHS CPG_PLUS CPG_MINUS <<< "$row"

IR_DIR="$RUN/outputs/irfinder_combined/$CELL"
FPKM="$RUN/outputs/fpkm_combined/$CELL/genes.fpkm_tracking"
IR_TXT=$(find "$IR_DIR" -maxdepth 1 -type f -name 'IRFinder-IR-*.txt' -print -quit)
BED_DIR="$RUN/outputs/beds/$CELL"
FEATURE_DIR="$RUN/outputs/raw_features/$CELL"
MODEL_DIR="$RUN/outputs/model_inputs"
COMPLETE="$RUN/outputs/completion/${CELL}.model_input.complete"

[[ -s "$RUN/outputs/completion/${CELL}.combined_irfinder_fpkm.complete" ]]
[[ -s "$FPKM" ]]
[[ -n "$IR_TXT" && -s "$IR_TXT" ]]
for file in "$FASTA" "$H3K36" "$DHS" "$CPG_PLUS" "$CPG_MINUS"; do
    [[ -s "$file" ]] || { echo "Missing/empty feature source: $file" >&2; exit 10; }
done

if [[ -s "$COMPLETE" ]]; then
    echo "Already complete: $CELL"
    exit 0
fi
mkdir -p "$BED_DIR" "$FEATURE_DIR" "$MODEL_DIR"

RAW_IR="$BED_DIR/${CELL}.IR.raw.bed"
RAW_NONIR="$BED_DIR/${CELL}.nonIR.raw.bed"
FINAL_IR="$BED_DIR/${CELL}.IR.final.bed"
FINAL_NONIR="$BED_DIR/${CELL}.nonIR.final.bed"
IR_NPZ="$FEATURE_DIR/group_${CELL}_IR_raw.npz"
NONIR_NPZ="$FEATURE_DIR/group_${CELL}_nonIR_raw.npz"
MODEL_NPZ="$MODEL_DIR/group_${CELL}_model_input_seed${SEED}.npz"

echo "[$(date -Is)] Filtering IRFinder events for $CELL"
"$PYTHON" "$RUN/scripts/01_filter_ir_events.py" "$FPKM" "$IR_TXT" "$RAW_IR" "$RAW_NONIR"
"$PYTHON" "$RUN/scripts/02_filter_bed_windows.py" "$RAW_IR" "$FINAL_IR"
"$PYTHON" "$RUN/scripts/02_filter_bed_windows.py" "$RAW_NONIR" "$FINAL_NONIR"

echo "[$(date -Is)] Building four-track matrices for $CELL"
COMMON=(--fasta "$FASTA" --chip "$H3K36" --dnase "$DHS" --cpg-plus "$CPG_PLUS" --cpg-minus "$CPG_MINUS")
"$PYTHON" "$RUN/scripts/03_build_feature_npz.py" --bed "$FINAL_IR" "${COMMON[@]}" --output "$IR_NPZ"
"$PYTHON" "$RUN/scripts/03_build_feature_npz.py" --bed "$FINAL_NONIR" "${COMMON[@]}" --output "$NONIR_NPZ"

echo "[$(date -Is)] Sampling 1:4 IR/nonIR and writing model input for $CELL"
"$PYTHON" "$RUN/scripts/04_create_training_dataset.py" --ir "$IR_NPZ" --non-ir "$NONIR_NPZ" --seed "$SEED" --output "$MODEL_NPZ"
[[ -s "$MODEL_NPZ" ]]

{
    echo -e "cell\t$CELL"
    echo -e "raw_ir_bed_rows\t$(wc -l < "$RAW_IR")"
    echo -e "raw_nonir_bed_rows\t$(wc -l < "$RAW_NONIR")"
    echo -e "final_ir_bed_rows\t$(wc -l < "$FINAL_IR")"
    echo -e "final_nonir_bed_rows\t$(wc -l < "$FINAL_NONIR")"
    echo -e "model_input\t$MODEL_NPZ"
    echo -e "seed\t$SEED"
    echo -e "finished\t$(date -Is)"
} > "$COMPLETE"
echo "[$(date -Is)] Completed model input for $CELL"
