#!/usr/bin/env bash
set -euo pipefail

RUN=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830
REPO=/rhome/yzhan677/bigdata/IntronsFormer
SOURCE_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

mkdir -p "$RUN"/{config,scripts,logs,work,outputs,provenance}
# Keep an existing run's manifests and frozen scripts intact.
for file in samples.tsv replicates.tsv; do
    [[ -e "$RUN/config/$file" ]] || cp "$SOURCE_DIR/$file" "$RUN/config/$file"
done
for file in "$SOURCE_DIR"/*.sbatch; do
    target="$RUN/scripts/$(basename "$file")"
    [[ -e "$target" ]] || cp "$file" "$target"
done
cp "$REPO/scripts/01_filter_ir_events.py" "$RUN/scripts/"
cp "$REPO/scripts/02_filter_bed_windows.py" "$RUN/scripts/"
cp "$REPO/scripts/03_build_feature_npz.py" "$RUN/scripts/"
cp "$REPO/scripts/04_create_training_dataset.py" "$RUN/scripts/"

git -C "$REPO" rev-parse HEAD > "$RUN/provenance/git_commit.txt"
sha256sum "$RUN"/scripts/* "$RUN"/config/samples.tsv "$RUN"/config/replicates.tsv > "$RUN/provenance/code_sha256.txt"

[[ -x "$RUN/envs/cufflinks/bin/cufflinks" ]]
[[ -x "$RUN/envs/cufflinks/bin/samtools" ]]
/rhome/yzhan677/bigdata/.conda/envs/performer/bin/python -c 'import Bio, numpy, pandas, pyBigWig'

while IFS=$'\t' read -r cell layout read1s read2s h3k36 dhs cpg_plus cpg_minus; do
    [[ "$cell" == cell ]] && continue
    for csv_field in "$read1s" "$read2s"; do
        [[ "$csv_field" == - ]] && continue
        IFS=',' read -r -a files <<< "$csv_field"
        for file in "${files[@]}"; do [[ -s "$file" ]]; done
    done
    for file in "$h3k36" "$dhs" "$cpg_plus" "$cpg_minus"; do [[ -s "$file" ]]; done
done < "$RUN/config/samples.tsv"

while IFS=$'\t' read -r cell replicate layout read1s read2s; do
    [[ "$cell" == cell ]] && continue
    for csv_field in "$read1s" "$read2s"; do
        [[ "$csv_field" == - ]] && continue
        IFS=',' read -r -a files <<< "$csv_field"
        for file in "${files[@]}"; do [[ -s "$file" ]]; done
    done
done < "$RUN/config/replicates.tsv"

replicate_job=$(sbatch --parsable "$RUN/scripts/01_irfinder_replicates.sbatch")
combined_job=$(sbatch --parsable --dependency="afterok:$replicate_job" "$RUN/scripts/02_combine_irfinder_fpkm.sbatch")
input_job=$(sbatch --parsable --dependency="afterok:$combined_job" "$RUN/scripts/02_model_inputs.sbatch")
validate_job=$(sbatch --parsable --dependency="afterok:$input_job" "$RUN/scripts/03_validate.sbatch")

{
    echo -e "replicate_irfinder_job\t$replicate_job"
    echo -e "combined_irfinder_fpkm_job\t$combined_job"
    echo -e "model_inputs_job\t$input_job"
    echo -e "validation_job\t$validate_job"
    echo -e "submitted\t$(date -Is)"
} | tee "$RUN/provenance/slurm_jobs.tsv"
