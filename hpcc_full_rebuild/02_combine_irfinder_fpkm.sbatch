#!/usr/bin/env bash
#SBATCH --job-name=if_combine
#SBATCH --partition=batch
#SBATCH --array=0-7%4
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=7-00:00:00
#SBATCH --output=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/logs/combine_irfinder_fpkm_%A_%a.out
#SBATCH --error=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/logs/combine_irfinder_fpkm_%A_%a.err

set -euo pipefail

RUN=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830
MANIFEST="$RUN/config/samples.tsv"
REF=/rhome/yzhan677/bigdata/refDir
IRFINDER=/rhome/yzhan677/bigdata/.conda/envs/align/bin/IRFinder
SAMTOOLS="$RUN/envs/cufflinks/bin/samtools"
CUFFLINKS="$RUN/envs/cufflinks/bin/cufflinks"
THREADS="${SLURM_CPUS_PER_TASK:-16}"
export PATH="/rhome/yzhan677/bigdata/.conda/envs/align/bin:$RUN/envs/cufflinks/bin:$PATH"

row=$(awk -F '\t' -v n="$SLURM_ARRAY_TASK_ID" 'NR == n + 2 {print; exit}' "$MANIFEST")
IFS=$'\t' read -r CELL LAYOUT READ1S READ2S H3K36 DHS CPG_PLUS CPG_MINUS <<< "$row"

REP1_DIR="$RUN/outputs/irfinder_replicates/$CELL/rep1"
REP2_DIR="$RUN/outputs/irfinder_replicates/$CELL/rep2"
IR_DIR="$RUN/outputs/irfinder_combined/$CELL"
FPKM_DIR="$RUN/outputs/fpkm_combined/$CELL"
CELL_WORK="$RUN/work/combined/$CELL"
COMPLETE="$RUN/outputs/completion/${CELL}.combined_irfinder_fpkm.complete"

[[ -s "$RUN/outputs/completion/${CELL}.rep1.irfinder.complete" ]]
[[ -s "$RUN/outputs/completion/${CELL}.rep2.irfinder.complete" ]]
[[ -s "$REP1_DIR/Unsorted.bam" ]]
[[ -s "$REP2_DIR/Unsorted.bam" ]]

if [[ -s "$COMPLETE" ]]; then
    echo "Already complete: $CELL combined"
    exit 0
fi

safe_reset() {
    case "$1" in
        "$RUN"/outputs/irfinder_combined/*|"$RUN"/outputs/fpkm_combined/*|"$RUN"/work/combined/*)
            rm -rf -- "$1"
            ;;
        *)
            echo "Refusing to reset path outside combined run root: $1" >&2
            exit 3
            ;;
    esac
}

safe_reset "$IR_DIR"
safe_reset "$FPKM_DIR"
safe_reset "$CELL_WORK"
mkdir -p "$(dirname "$IR_DIR")" "$FPKM_DIR" "$CELL_WORK" "$RUN/provenance/$CELL/combined"

REP1_BAM="$REP1_DIR/Unsorted.bam"
REP2_BAM="$REP2_DIR/Unsorted.bam"
NAME_BAM="$CELL_WORK/combined.queryname_sorted.bam"
COORD_BAM="$CELL_WORK/combined.coordinate_sorted.bam"

"$SAMTOOLS" quickcheck -v "$REP1_BAM" "$REP2_BAM"
echo "[$(date -Is)] Concatenating replicate BAMs and query-name sorting: $CELL"
"$SAMTOOLS" cat "$REP1_BAM" "$REP2_BAM" \
    | "$SAMTOOLS" sort -n -@ "$THREADS" -m 4G -O BAM -o "$NAME_BAM" -
"$SAMTOOLS" quickcheck -v "$NAME_BAM"

echo "[$(date -Is)] Re-quantifying combined BAM with IRFinder: $CELL"
"$IRFINDER" -m BAM -r "$REF" -d "$IR_DIR" -t "$THREADS" "$NAME_BAM"
IR_TXT=$(find "$IR_DIR" -maxdepth 1 -type f -name 'IRFinder-IR-*.txt' -print -quit)
[[ -n "$IR_TXT" && -s "$IR_TXT" ]] || { echo "Combined IRFinder table missing for $CELL" >&2; exit 8; }

echo "[$(date -Is)] Coordinate-sorting the same combined BAM: $CELL"
"$SAMTOOLS" sort -@ "$THREADS" -m 4G -o "$COORD_BAM" "$NAME_BAM"
"$SAMTOOLS" index -@ "$THREADS" "$COORD_BAM"

echo "[$(date -Is)] Running combined Cufflinks FPKM: $CELL"
"$CUFFLINKS" -p "$THREADS" -G "$REF/transcripts.gtf" -o "$FPKM_DIR" "$COORD_BAM"
[[ -s "$FPKM_DIR/genes.fpkm_tracking" ]] || { echo "Combined FPKM output missing for $CELL" >&2; exit 9; }

{
    echo -e "cell\t$CELL"
    echo -e "rep1_bam\t$REP1_BAM"
    echo -e "rep2_bam\t$REP2_BAM"
    echo -e "combined_queryname_bam\t$NAME_BAM"
    echo -e "combined_coordinate_bam\t$COORD_BAM"
    echo -e "irfinder_table\t$IR_TXT"
    echo -e "irfinder_rows\t$(( $(wc -l < "$IR_TXT") - 1 ))"
    echo -e "fpkm_table\t$FPKM_DIR/genes.fpkm_tracking"
    echo -e "fpkm_rows\t$(( $(wc -l < "$FPKM_DIR/genes.fpkm_tracking") - 1 ))"
    echo -e "samtools\t$($SAMTOOLS --version | head -1)"
    echo -e "cufflinks\t$($CUFFLINKS -v 2>&1 | head -1)"
    echo -e "finished\t$(date -Is)"
} > "$COMPLETE"
echo "[$(date -Is)] Completed combined IRFinder and FPKM for $CELL"
