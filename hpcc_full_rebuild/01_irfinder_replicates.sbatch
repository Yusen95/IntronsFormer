#!/usr/bin/env bash
#SBATCH --job-name=if_replicates
#SBATCH --partition=batch
#SBATCH --array=0-15%4
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=7-00:00:00
#SBATCH --output=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/logs/irfinder_replicate_%A_%a.out
#SBATCH --error=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/logs/irfinder_replicate_%A_%a.err

set -euo pipefail

RUN=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830
MANIFEST="$RUN/config/replicates.tsv"
REF=/rhome/yzhan677/bigdata/refDir
IRFINDER=/rhome/yzhan677/bigdata/.conda/envs/align/bin/IRFinder
THREADS="${SLURM_CPUS_PER_TASK:-16}"
export PATH="/rhome/yzhan677/bigdata/.conda/envs/align/bin:$RUN/envs/cufflinks/bin:$PATH"

row=$(awk -F '\t' -v n="$SLURM_ARRAY_TASK_ID" 'NR == n + 2 {print; exit}' "$MANIFEST")
if [[ -z "$row" ]]; then
    echo "No replicate manifest row for array index $SLURM_ARRAY_TASK_ID" >&2
    exit 2
fi
IFS=$'\t' read -r CELL REPLICATE LAYOUT READ1S READ2S <<< "$row"

IR_DIR="$RUN/outputs/irfinder_replicates/$CELL/$REPLICATE"
CELL_WORK="$RUN/work/irfinder_replicates/$CELL/$REPLICATE"
COMPLETE="$RUN/outputs/completion/${CELL}.${REPLICATE}.irfinder.complete"

if [[ -s "$COMPLETE" ]]; then
    echo "Already complete: $CELL $REPLICATE"
    exit 0
fi

safe_reset() {
    case "$1" in
        "$RUN"/outputs/irfinder_replicates/*|"$RUN"/work/irfinder_replicates/*)
            rm -rf -- "$1"
            ;;
        *)
            echo "Refusing to reset path outside replicate run root: $1" >&2
            exit 3
            ;;
    esac
}

safe_reset "$IR_DIR"
safe_reset "$CELL_WORK"
mkdir -p "$(dirname "$IR_DIR")" "$CELL_WORK" "$RUN/outputs/completion" "$RUN/provenance/$CELL/$REPLICATE"

IFS=',' read -r -a R1_FILES <<< "$READ1S"
for file in "${R1_FILES[@]}"; do
    [[ -s "$file" ]] || { echo "Missing/empty FASTQ: $file" >&2; exit 4; }
done

suffix=.fastq
[[ "${R1_FILES[0]}" == *.gz ]] && suffix=.fastq.gz
FIFO1="$CELL_WORK/input_R1${suffix}"
mkfifo "$FIFO1"

feeder_pids=()
cleanup() {
    for pid in "${feeder_pids[@]:-}"; do kill "$pid" 2>/dev/null || true; done
    rm -f -- "$FIFO1"
    [[ -n "${FIFO2:-}" ]] && rm -f -- "$FIFO2"
}
trap cleanup EXIT

cat "${R1_FILES[@]}" > "$FIFO1" &
feeder_pids+=("$!")

IR_ARGS=("$FIFO1")
if [[ "$LAYOUT" == PE ]]; then
    IFS=',' read -r -a R2_FILES <<< "$READ2S"
    [[ "${#R1_FILES[@]}" -eq "${#R2_FILES[@]}" ]] || {
        echo "R1/R2 file count mismatch for $CELL $REPLICATE" >&2
        exit 5
    }
    for file in "${R2_FILES[@]}"; do
        [[ -s "$file" ]] || { echo "Missing/empty FASTQ: $file" >&2; exit 4; }
    done
    FIFO2="$CELL_WORK/input_R2${suffix}"
    mkfifo "$FIFO2"
    cat "${R2_FILES[@]}" > "$FIFO2" &
    feeder_pids+=("$!")
    IR_ARGS+=("$FIFO2")
elif [[ "$LAYOUT" != SE ]]; then
    echo "Unsupported layout: $LAYOUT" >&2
    exit 6
fi

{
    echo -e "cell\t$CELL"
    echo -e "replicate\t$REPLICATE"
    echo -e "layout\t$LAYOUT"
    echo -e "irfinder\t$($IRFINDER -v 2>&1 | head -1)"
    echo -e "star\t$(STAR --version 2>&1 | head -1)"
    printf 'read1\t%s\n' "${R1_FILES[@]}"
    if [[ "$LAYOUT" == PE ]]; then printf 'read2\t%s\n' "${R2_FILES[@]}"; fi
} > "$RUN/provenance/$CELL/$REPLICATE/tools_and_inputs.tsv"

echo "[$(date -Is)] Starting replicate IRFinder for $CELL $REPLICATE ($LAYOUT)"
"$IRFINDER" -r "$REF" -d "$IR_DIR" -t "$THREADS" "${IR_ARGS[@]}"
for pid in "${feeder_pids[@]}"; do wait "$pid"; done
feeder_pids=()
rm -f -- "$FIFO1"
[[ -n "${FIFO2:-}" ]] && rm -f -- "$FIFO2"
trap - EXIT

[[ -s "$IR_DIR/Unsorted.bam" ]] || { echo "Replicate BAM missing: $CELL $REPLICATE" >&2; exit 7; }
IR_TXT=$(find "$IR_DIR" -maxdepth 1 -type f -name 'IRFinder-IR-*.txt' -print -quit)
[[ -n "$IR_TXT" && -s "$IR_TXT" ]] || { echo "Replicate IRFinder table missing" >&2; exit 8; }

{
    echo -e "cell\t$CELL"
    echo -e "replicate\t$REPLICATE"
    echo -e "bam\t$IR_DIR/Unsorted.bam"
    echo -e "irfinder_table\t$IR_TXT"
    echo -e "irfinder_rows\t$(( $(wc -l < "$IR_TXT") - 1 ))"
    echo -e "finished\t$(date -Is)"
} > "$COMPLETE"
echo "[$(date -Is)] Completed replicate IRFinder for $CELL $REPLICATE"
