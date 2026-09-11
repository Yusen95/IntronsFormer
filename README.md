# Paper Reproducibility Repository

This repository contains metadata, example preprocessing outputs, processed inputs, and downstream analysis scripts for reproducing the analyses in the paper.

**Start here:** [Commands for readers and reviewers](docs/REVIEWER_RUN_GUIDE.md)
provides installation commands, an executable small example, all four plotting
commands, expected numerical results, and the conditional raw-data-to-model
runbook. Each route states its prerequisites and verification status.

The repository is organized as a reproducibility workflow rather than a standalone software package. Standard preprocessing tools such as IRFinder and Cufflinks are documented, and example outputs are provided so downstream scripts can be tested without re-running all raw-data processing steps.

## Workflow Overview

Latest cross-project plotting scripts, their required input tables and local
rerun commands are documented in [the plotting synchronization guide](docs/PLOT_CODE_SYNC.md).
The [actual September HPCC code snapshot](provenance/hpcc_20260911/README.md)
includes source hashes, runtime versions and rebuilt checkpoint identity.

For the complete input-to-results map, including the August–September 2026
rebuild and remaining release gaps, see [the full workflow guide](docs/FULL_WORKFLOW.md).
The raw FASTQ-to-model-input Slurm scripts and input manifests are in
[`hpcc_full_rebuild/`](hpcc_full_rebuild/README.md). These scripts retain the
original HPCC paths and require the setup described there.

See the [per-script local reproduction check](docs/LOCAL_REPRODUCTION_CHECK.md)
for tested local commands, platform requirements and remaining blockers. A
successful processed-data example does not imply that the entire raw-data
workflow runs without Slurm, external references or the training environment.

1. Collect ENCODE RNA-seq datasets for selected human cell lines.
2. Quantify intron retention with IRFinder.
3. Quantify gene expression as FPKM with Cufflinks.
4. Filter retained and non-retained introns using IRFinder metrics and gene-level FPKM.
5. Filter BED intervals by intron length and extend each interval by 100 bp.
6. Build per-interval sequence and chromatin-signal feature arrays.
7. Combine IR and sampled nonIR feature arrays into model-training datasets.
8. Train the IntronsFormer model.
9. Compute integrated-gradient attribution scores.
10. Extract high-attribution sequence patterns from IG scores.
11. Convert extracted motifs to MEME format for TomTom comparison.
12. Validate candidate TF/RBP binding occupancy with ENCODE ChIP-seq/eCLIP peaks.
13. Validate candidate TF/RBP effects with ENCODE knockdown RNA-seq, IRFinder, and iDiffIR.
14. Run downstream analyses used in the paper.

## Reference Setup

- Genome build: hg38
- Annotation: Ensembl release 111 for hg38
- Python: 3.8.19
- PyTorch: 1.12.0+cu113
- Intron retention tool: IRFinder 1.3.1
- Expression quantification tool: Cufflinks 2.2.1

Create the Python environment with:

```bash
conda env create -f environment.yml
conda activate intronsformer
```

Download the pretrained checkpoint from the GitHub Release asset:

```bash
mkdir -p models
curl -L \
  -o models/best_2conv_auc.pt \
  https://github.com/Yusen95/IntronsFormer/releases/download/model-v1.0.0/best_2conv_auc.pt
```

File integrity can then be checked with `sha256sum -c checksums.sha256`.

External command-line tools used outside the Python environment:

- IRFinder 1.3.1
- Cufflinks 2.2.1
- samtools
- MEME suite / TomTom
- iDiffIR

## Repository Layout

```text
metadata/
  encode_data_sources.tsv     # ENCODE IDs for H3K36me3, DHS, CpG, and RNA-seq inputs
  rnaseq_sources.tsv          # ENCODE RNA-seq sources used for IRFinder/Cufflinks

example/
  irfinder/K562_IRFinder-IR-dir.txt
  cufflinks/K562_genes.fpkm_tracking

models/
  best_2conv_auc.pt           # Downloaded pretrained checkpoint

data/
  processed/                  # Processed matrices used by downstream scripts

scripts/
  01_filter_ir_events.py      # Generate retained/non-retained intron BED files
  02_filter_bed_windows.py    # Keep <=10 kb introns and extend intervals by 100 bp
  03_build_feature_npz.py     # Build sequence/H3K36me3/DNase/CpG feature arrays
  04_create_training_dataset.py  # Combine IR/nonIR feature arrays and labels
  05_train_intronsformer.py   # Train IntronsFormer
  06_integrated_gradients.py  # Compute integrated-gradient scores
  07_extract_ig_motifs.py     # Extract high-IG sequence patterns
  08_motifs_to_meme.py        # Convert motif CSV to MEME format
  09_binding_overlap_analysis.py  # Compare TF/RBP peak occupancy over IR vs nonIR regions
  10_plot_binding_occupancy.py    # Plot binding occupancy results
  download_encode_peaks_from_selected_tsv.sh
  run_binding_overlap_hpcc.sh
  prepare_encode_knockdown.py
  create_knockdown_new_only_scripts.py
  summarize_tf_rbp_prediction_control_idiffir_counts_HPCC.py
  summarize_idiffir_allIntrons_adjP_threshold_HPCC.py
  plot_tf_rbp_all_prediction_only.py
  plot_tf_only_prediction_vs_control.py

outputs/
  knockdown/                  # ENCODE knockdown metadata and generated HPCC scripts
  event_count_comparison/     # Processed RBP prediction/control event-count table
  encode_current_prediction_perturbation_check/
                              # Processed TF prediction/control event-count table
```

## Filtering Retained Introns

The first downstream script combines Cufflinks FPKM output with IRFinder intron-retention metrics:

```bash
python scripts/01_filter_ir_events.py \
  <genes.fpkm_tracking> \
  <IRFinder_output.txt> \
  <IRs.bed> \
  <nonIRs.bed>
```

The included K562 files can be used to test this step directly:

```bash
mkdir -p outputs/example
python scripts/01_filter_ir_events.py \
  example/cufflinks/K562_genes.fpkm_tracking \
  example/irfinder/K562_IRFinder-IR-dir.txt \
  outputs/example/K562_IRs.bed \
  outputs/example/K562_nonIRs.bed
```

The current thresholds are:

- expressed gene: FPKM >= 1
- retained intron: IRratio >= 0.1 and IntronDepth >= 10
- non-retained intron: IRratio <= 0.01 and IntronDepth < 10

The resulting BED files are further filtered and expanded with:

```bash
python scripts/02_filter_bed_windows.py <input.bed> <output.bed>
```

This keeps introns with length <= 10,000 bp and extends each interval by 100 bp on both sides.

Feature arrays are then generated with:

```bash
python scripts/03_build_feature_npz.py \
  --bed <filtered_extended.bed> \
  --fasta <hg38.fa> \
  --chip <H3K36me3.bigWig> \
  --dnase <DNase.bigWig> \
  --cpg-plus <CpG_plus.bigWig> \
  --cpg-minus <CpG_minus.bigWig> \
  --output <features.npz>
```

Each saved interval array contains four tracks in this order: integer-encoded DNA sequence, H3K36me3 signal, DNase/DHS signal, and strand-specific CpG signal.

The model-training dataset is created with:

```bash
python scripts/04_create_training_dataset.py \
  --ir <IR_features.npz> \
  --non-ir <nonIR_features.npz> \
  --output <training_dataset.npz> \
  --seed 1
```

This labels IR intervals as 1, samples up to four times as many nonIR intervals as negatives, labels them as 0, shuffles the combined dataset, and saves arrays, labels, and BED metadata to one `.npz` file.

Train the model with:

```bash
python scripts/05_train_intronsformer.py \
  --datasets \
    <group_K562_raw.npz> \
    <group_GM12878_raw.npz> \
    <group_IMR-90_raw.npz> \
    <group_HepG2_raw.npz> \
    <group_H1_raw.npz> \
    <group_GM23248_raw.npz> \
    <group_HeLa-S3_raw.npz> \
    <group_SK-N-SH_raw.npz> \
  --output-dir <model_output_dir> \
  --epochs 15 \
  --batch-size 16 \
  --seed 42
```

The training script splits samples by genomic interval to avoid placing the same interval in multiple splits, trains a Performer-based sequence/signal model, and reports ROC-AUC, PR-AUC, and F1 on the held-out test split.

After training, compute integrated-gradient scores with:

```bash
python scripts/06_integrated_gradients.py \
  --datasets \
    <group_K562_raw.npz> \
    <group_GM12878_raw.npz> \
    <group_IMR-90_raw.npz> \
    <group_HepG2_raw.npz> \
    <group_H1_raw.npz> \
    <group_GM23248_raw.npz> \
    <group_HeLa-S3_raw.npz> \
    <group_SK-N-SH_raw.npz> \
  --checkpoint models/best_2conv_auc.pt \
  --output-dir <ig_output_dir> \
  --steps 50
```

This script computes integrated gradients for all samples, writes separate positive and negative sequence/score CSV files, records model probabilities in `ig_full_meta.csv`, and supports resume through `.done` files.

Extract candidate high-attribution sequence patterns with:

```bash
python scripts/07_extract_ig_motifs.py \
  --direction pos \
  --seq <ig_all_pos_sequence.csv> \
  --score <ig_all_pos_score.csv> \
  --out <pos_motifs.csv> \
  --min_len 5 \
  --count 3
```

Use `--direction neg` with the negative sequence and score files to extract high negative-attribution patterns from nonIR samples.

Convert extracted motif tables to MEME format for TomTom comparison with:

```bash
python scripts/08_motifs_to_meme.py \
  --in <pos_motifs.csv> \
  --out <pos_motifs.meme>
```

TomTom motif similarity search was run against CIS-BP v2.00 databases:

- CIS-BP DNA: `Homo_sapiens_2.0.meme`
- CIS-BP RNA: `Homo_sapiens.dna_encoded.meme`

Example commands:

```bash
tomtom -oc tomtom_pos_cisbp_dna pos_motifs.meme Homo_sapiens_2.0.meme
tomtom -oc tomtom_pos_cisbp_rna pos_motifs.meme Homo_sapiens.dna_encoded.meme
tomtom -oc tomtom_neg_cisbp_dna neg_motifs.meme Homo_sapiens_2.0.meme
tomtom -oc tomtom_neg_cisbp_rna neg_motifs.meme Homo_sapiens.dna_encoded.meme
```

## Binding Occupancy Validation

After TomTom annotation, candidate TFs and RBPs were validated by testing whether matched ENCODE ChIP-seq/eCLIP peaks preferentially overlap IR or nonIR event regions.

The selected ENCODE peak table is:

```text
metadata/encode_selected_peaks_pos_both_neg_tsv.tsv
```

The overlap analysis uses:

- IR event BED files under `<BASE_DIR>/Project1/IRevent/`
- nonIR event BED files under `<BASE_DIR>/Project1/nonIRevent/`
- hg38 Ensembl release 111 GTF at `<BASE_DIR>/Homo_sapiens.GRCh38.111.gtf`
- ENCODE ChIP-seq/eCLIP peaks downloaded from the selected TSV

Run the validation workflow on HPCC with:

```bash
BASE_DIR=~/bigdata bash scripts/run_binding_overlap_hpcc.sh
```

This wrapper:

1. downloads missing ENCODE peak BED files from `metadata/encode_selected_peaks_pos_both_neg_tsv.tsv`;
2. builds event regions from upstream exon, intron, and downstream exon;
3. excludes first introns;
4. length-adjusts nonIR events;
5. applies the start-in-gene boundary filter;
6. computes event-level occupancy, where one intron event is counted as occupied if it overlaps at least one peak;
7. runs Fisher exact tests comparing IR and nonIR occupancy;
8. plots K562 and HepG2 occupancy panels.

Main output:

```text
<BASE_DIR>/baseline14_event_overlap_pos_both_neg_tsv_no_first_intron_length_adjusted_start_in_gene/baseline_like_overlap_three_class_summary.tsv
```

Main plotting output:

```text
<BASE_DIR>/baseline14_event_overlap_pos_both_neg_tsv_no_first_intron_length_adjusted_start_in_gene_plots/
```

## Knockdown Perturbation Validation

Candidate TF/RBP perturbation effects were evaluated using ENCODE knockdown RNA-seq. For each target, FASTQ files were downloaded, IRFinder was run on knockdown and matched control replicates, iDiffIR was used to identify differential intron-retention events, and event counts were compared between prediction and control groups.

Small metadata files included in this repository:

```text
metadata/knockdown/Pos_TF.tsv
metadata/knockdown/Neg_TF.tsv
metadata/knockdown/Pos_RBP.tsv
metadata/knockdown/Neg_RBP.tsv
metadata/knockdown/Homo_sapiens.meme
outputs/knockdown/encode_knockdown_selected.tsv
outputs/knockdown/encode_knockdown_fastq_files.tsv
outputs/knockdown/encode_knockdown_missing.tsv
```

Generated HPCC scripts included in this repository:

```text
outputs/knockdown/download_encode_knockdown_fastq_HPCC.sh
outputs/knockdown/run_all_knockdown_irfinder_idiffir.sh
```

Large files are not committed and should be regenerated on HPCC:

```text
*.fastq.gz
*.bam
TF_knockdown/
RBP_knockdown/
Project1/iDiffIR/*_result/
```

Download the selected ENCODE FASTQ files on HPCC:

```bash
BASE_DIR=~/bigdata bash outputs/knockdown/download_encode_knockdown_fastq_HPCC.sh
```

Run IRFinder and iDiffIR:

```bash
BASE_DIR=~/bigdata \
IRFINDER_REF=~/bigdata/refDir \
IDIFFIR_DIR=~/bigdata/Project1/iDiffIR \
GTF=Homo_sapiens.GRCh38.111.transcript_only.gtf \
bash outputs/knockdown/run_all_knockdown_irfinder_idiffir.sh
```

The iDiffIR convention is:

- `KnockOut` is the knockdown/perturbation group.
- `Wildtype` is the matched control group.
- `upDIRs.txt` means intron retention is higher after knockdown.
- `downDIRs.txt` means intron retention is lower after knockdown.

Summarize iDiffIR event counts from original iDiffIR lists:

```bash
python scripts/summarize_tf_rbp_prediction_control_idiffir_counts_HPCC.py \
  --idiffir-dir ~/bigdata/Project1/iDiffIR \
  --pos-tf metadata/knockdown/Pos_TF.tsv \
  --neg-tf metadata/knockdown/Neg_TF.tsv \
  --pos-rbp metadata/knockdown/Pos_RBP.tsv \
  --neg-rbp metadata/knockdown/Neg_RBP.tsv \
  --meme metadata/knockdown/Homo_sapiens.meme \
  --combined-out outputs/event_count_comparison/idiffir_prediction_control_event_counts_combined.tsv \
  --audit-out outputs/event_count_comparison/idiffir_all_result_dirs_event_counts.tsv
```

The main event-count metric is:

```text
all_events = non-empty lines in lists/allDIRs.txt
up_events = non-empty lines in lists/upDIRs.txt
down_events = non-empty lines in lists/downDIRs.txt
```

An optional sensitivity analysis can count events from `allIntrons.txt` with an adjusted p-value threshold:

```bash
python scripts/summarize_idiffir_allIntrons_adjP_threshold_HPCC.py \
  --idiffir-dir ~/bigdata/Project1/iDiffIR \
  --threshold 0.01 \
  --out outputs/event_count_comparison/idiffir_event_counts_from_allIntrons_adjP001.tsv
```

Processed event-count tables used by the final plot are included:

```text
outputs/encode_current_prediction_perturbation_check/encode_prediction_vs_control_event_counts.tsv
outputs/event_count_comparison/prediction_pos_both_neg_control_event_counts.tsv
```

Generate the final TF/RBP prediction-vs-control figure:

```bash
python scripts/plot_tf_rbp_all_prediction_only.py
```

Final plot outputs:

```text
outputs/direction_specific_original_counts/Figure7.png
outputs/direction_specific_original_counts/Figure7.svg
outputs/direction_specific_original_counts/tf_rbp_all_prediction_only_event_counts.tsv
outputs/direction_specific_original_counts/tf_rbp_all_prediction_only_stats.tsv
```

The final plot compares total iDiffIR event counts for predicted TFs/RBPs versus control TFs/RBPs. The statistical test is a permutation test on the difference in group means; dots represent individual targets/runs, boxes show Q1-Q3, whiskers span minimum to maximum, and the black horizontal line marks the mean.

## Current Entry Point

Two entry points are available: the matched K562 processed example below, and
the [HPCC raw-input rebuild](hpcc_full_rebuild/README.md). The latter includes
replicate-level IRFinder, combined-BAM IRFinder/Cufflinks, feature construction,
and model-input validation. It currently requires downloaded source files,
an existing IRFinder reference, and configured HPCC tool environments; reference
construction and environment restoration are not yet packaged as an automated setup.

The repository includes matched K562 IRFinder and Cufflinks outputs under `example/`, allowing users to run the first downstream filtering step without repeating FASTQ/BAM preprocessing. The trained model used for integrated-gradient analysis is distributed as the `best_2conv_auc.pt` asset in the `model-v1.0.0` GitHub Release.

## Metadata To Complete

The following information should still be completed before release:

- Resolve the remaining provenance notes in `metadata/encode_data_sources.tsv`,
  including the inferred GM23248 CpG minus accession.
- Add reference-download checksums and the exact IRFinder reference-build procedure.
- Validate installation of a clean model environment against the recovered
  [HPCC package inventory](provenance/hpcc_20260911/runtime/packages.txt).
- Compare full numerical behavior of the recovered HPCC scripts with the
  numbered repository scripts, and publish the rebuilt checkpoint itself.
- Complete the new-output-to-downstream-validation mapping described in
  [the full workflow guide](docs/FULL_WORKFLOW.md).

## License

This repository is released under the MIT License.
