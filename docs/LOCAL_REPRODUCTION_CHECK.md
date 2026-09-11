# Per-script local reproduction check

**Later update, same date:** [PLOT_CODE_SYNC.md](PLOT_CODE_SYNC.md) covers the
additional plotting/preparation scripts, restored input tables and successful
replotting checks. [The HPCC snapshot](../provenance/hpcc_20260911/README.md)
now preserves the actual frozen code and observed environment. The table below
is the earlier 18-script audit; a clean installation and a complete raw-data
rerun remain unverified.

Checked 2026-09-11 against commit `6dca3e3`, plus the portability fixes described
below. Scope: all 18 tracked Python analysis scripts and all nine tracked
Shell/Slurm scripts. The untracked manuscript PDF-label helper is addressed
separately. This is a code and small-input audit, not a complete paper rerun.

**Conclusion:** the repository can run several processed-data steps locally.
A clean checkout cannot yet reproduce the complete raw-input-to-paper workflow
on an ordinary Windows machine. Raw processing requires external tools,
references and data; its current entry point requires Slurm. The training and
IG environments and actual HPCC script equivalence remain unverified.

## What was executed

Checks ran in a temporary copy made from tracked Git files, with the reviewed
script fixes copied into it. No unpublished manuscript files or local edits to
the event-count tables were used. No raw ENCODE data were downloaded and no
HPCC job was submitted.

- Windows, Python 3.12.14; test environment: NumPy 2.5.3, pandas 3.0.1,
  SciPy 1.18.1, matplotlib 3.11.1, Biopython 1.88, Pillow 12.3.0.
- 20 subprocess checks had expected outcomes: 18 successful executions and
  two intentional missing-input failures. They covered the K562 example,
  synthetic dataset assembly, positive/negative motif extraction and MEME
  conversion, iDiffIR summaries, auxiliary script generation, occupancy on
  synthetic loci, and plots from the published event-count tables.
- K562 filtering produced 10,670 IR and 55,360 nonIR rows before window filtering.
- All nine tracked Shell/Slurm files passed `bash -n`.
- The knockdown downloader and runner each reference 248 distinct FASTQ paths;
  every runner FASTQ is present in the downloader, and the metadata has 248 rows.
- The four committed regression tests passed, including nested output paths,
  CLI help, and a CSV field longer than 131,072 characters on Windows.

The test environment is **not** an export of the paper's training environment.
PyBigWig and PyTorch were not installed in it. A binary-only pip download probe
found no matching pyBigWig wheel for this Windows/Python combination. That does
not prove that source compilation or other platforms are unsupported.

## Python files: individual results

Paths below are under `scripts/`. “Executed” means the stated bounded check,
not validation of all scientific edge cases or equivalence to HPCC results.

| Script | Local result | Remaining requirement or issue |
| --- | --- | --- |
| `01_filter_ir_events.py` | Executed with the published K562 IRFinder/FPKM example | Output parent must already exist. Uses fixed IRFinder/Cufflinks column positions and truncates IntronDepth to an integer. |
| `02_filter_bed_windows.py` | Executed on both K562 BED outputs | pandas required. Flanks can produce negative BED starts; later feature extraction clips them, while stored BED metadata retains the original coordinates. |
| `03_build_feature_npz.py` | Source reviewed; full execution not tested because pyBigWig is absent | Requires reference FASTA and four real BigWigs. Removing non-ACGT bases without matching signal masking can misalign features. Assembly/coordinate identity needs checking. |
| `04_create_training_dataset.py` | Executed with synthetic 4-channel arrays; 3 positives + 12 sampled negatives and 15 metadata rows verified | Real feature inputs required. Use `--seed 1` for the documented deterministic sampling. |
| `05_train_intronsformer.py` | Source reviewed; training/import not verified in a PyTorch environment | Loads all datasets into RAM; uses a large model and BF16 on every CUDA device. Small splits may contain one class and fail AUC. Gradient accumulation and threshold-selection issues are listed below. |
| `06_integrated_gradients.py` | Source reviewed; execution/import not verified in a PyTorch/Captum environment | Needs matching checkpoint, full NPZ inputs and substantial memory. Resume state is not bound to input/checkpoint hashes; mismatched keys only warn. |
| `07_extract_ig_motifs.py` | Executed on synthetic positive and negative sequence/score files | Output directory must exist. Loads all CSVs into RAM. Input is headerless; exact row/base correspondence matters. |
| `08_motifs_to_meme.py` | Executed for both signs and a 200,000-character CSV field after Windows fix | Motif IDs are renumbered; retain an explicit mapping if linking Tomtom query IDs back to CSV IDs. |
| `09_binding_overlap_analysis.py` | Executed on synthetic GTF, events and peak data | Still requires all three hardcoded cell-line event layouts, even for a one-cell selected table. Treats event coordinates as 1-based inclusive; do not blindly substitute conventional BED or flanked feature windows. |
| `10_plot_binding_occupancy.py` | Executed on the synthetic overlap output; PNG/PDF generated | Requires the summary schema from `09`; plots K562/HepG2. Does not reconstruct missing occupancy results. |
| `prepare_encode_knockdown.py` | Import, `--help`, missing-file validation and generated-script functions checked; no live ENCODE selection run | Six candidate CSVs with a `tf_name` column are not included. Now accepts `--input-dir` and `--out-dir`. Its assay search uses shRNA/CRISPRi, while README mentions a broader perturbation set. |
| `create_knockdown_new_only_scripts.py` | Executed using one published selected run, its FASTQs and a synthetic comparison status | Now accepts `--comparison`, `--fastqs`, `--out-dir`. The historical comparison TSV is not included; users must supply it. Generated scripts still require external tools/environments. |
| `summarize_tf_rbp_prediction_control_idiffir_counts_HPCC.py` | Executed against synthetic iDiffIR lists and published motif tables | Actual iDiffIR lists are not included. Output schema uses `analysis_type`, unlike downstream classified tables' `type`; overlapping positive/negative memberships are prioritized as positive, not `positive_and_negative`. |
| `summarize_idiffir_allIntrons_adjP_threshold_HPCC.py` | Executed against synthetic `allIntrons.txt`; counts checked in regression test | Requires `adjPValue` and `logFoldChange`; events with zero log-fold-change are reported separately and excluded from `all_events`. |
| `summarize_prediction_pos_both_neg_with_control_event_counts.py` | Executed with synthetic classified counts and an explicit output directory | Now accepts `--input`. Historical `idiffir_event_counts_classified.tsv` and its generation step are absent; the list-summary output cannot be substituted unchanged. |
| `summarize_encode_prediction_vs_control_event_counts.py` | Executed with synthetic classified counts and ENCODE support table | Now accepts `--counts`, `--support`, `--out-dir`. Both historical intermediate inputs remain absent. |
| `plot_tf_rbp_all_prediction_only.py` | Executed with both published event-count tables; figure/statistics generated | Can run locally with NumPy, pandas and Pillow. Uses the existing tables, not newly computed iDiffIR results. Linux font rendering may differ. |
| `plot_tf_only_prediction_vs_control.py` | Default TF plot executed with published table | Cell-specific mode fails because the stratified input is absent. Missing optional Wilcoxon tables omit p-values, so a successful plot does not certify complete statistical reproduction. |

## Shell and Slurm files: individual results

All passed syntax checks. None was executed against real FASTQ, BAM or Slurm.

| File | Local execution status and dependencies |
| --- | --- |
| `hpcc_full_rebuild/submit.sh` | Not a plain local runner: requires `sbatch`, original path configuration, reference/tool environments and all input files. Copies preprocessing files and submits dependent jobs. |
| `hpcc_full_rebuild/01_irfinder_replicates.sbatch` | Requires Slurm array index, Linux FIFO/process behavior, IRFinder and STAR. Resource request: 16 CPUs, 128 GB RAM per task; these are requests, not measured minima. |
| `hpcc_full_rebuild/02_combine_irfinder_fpkm.sbatch` | Requires preceding completion records/BAMs, samtools, IRFinder, Cufflinks and hardcoded paths. Requests 128 GB RAM. |
| `hpcc_full_rebuild/02_model_inputs.sbatch` | Requires Slurm array index and the preceding IRFinder/FPKM outputs; invokes `01–04`. First-match IRFinder table selection is still ambiguous. Requests 96 GB RAM. |
| `hpcc_full_rebuild/03_validate.sbatch` | Embedded Python could run locally after path adaptation, but wrapper hardcodes Python/run paths. Shape/count/finiteness checks do not validate binary labels, minimum sequence lengths or coordinate alignment. |
| `scripts/download_encode_peaks_from_selected_tsv.sh` | Bash/wget/gzip and a selected TSV required; standalone default TSV path differs from the repository layout. Skips a target if any BED exists, not necessarily the selected accession; interrupted output may remain. |
| `scripts/run_binding_overlap_hpcc.sh` | No Slurm command; can run on a configured Linux workstation. Requires expected event/GTF layout, external downloads and Python packages. Enables fallback to non-selected peak files, weakening strict input reproducibility. |
| `outputs/knockdown/download_encode_knockdown_fastq_HPCC.sh` | Bash/wget required; no Slurm. Published paths match the runner. Writes directly to final files and skips nonempty files, so interrupted downloads need explicit integrity checks before reuse. |
| `outputs/knockdown/run_all_knockdown_irfinder_idiffir.sh` | No Slurm, but requires IRFinder, `idiffir_py2` Conda environment, iDiffIR/convertBam and references. Relative BAM source paths assume the original directory nesting. Environment activation persists into subsequent IRFinder blocks. |

The untracked `scripts/update_figure7_ybx1_labels.py` is a manuscript-edit helper,
not a public reproduction step. It depends on an unpublished source PDF plus
pypdf/reportlab and fixed overlay coordinates. It was inspected but not run.

## Scientific/reproducibility issues not silently changed

These require comparison with the executed HPCC version before changing paper results:

1. **Feature alignment:** `03` deletes ambiguous bases and truncates signals,
   rather than applying a shared position mask. Example: `ACNGT` becomes four
   DNA values while signals still represent the first four original positions.
2. **Training updates:** `05` steps the optimizer only every fourth batch;
   remaining batches at the end of an epoch are discarded. With fewer than four
   training batches there is no optimizer update. The learning-rate schedule
   counts every batch although it advances only on optimizer updates.
3. **Evaluation meaning:** `05` selects the best F1 threshold separately inside
   each evaluation call, including test evaluation. Reported test F1 is not the
   result of a validation-fixed threshold. Splits/predictions are not archived.
4. **IG resume/model identity:** `06` reuses selection/done files without checking
   input or checkpoint identity; `strict=False` can leave unmatched parameters
   initialized while continuing. Use a fresh output directory for a changed run.
5. **Motif/validation hand-off:** `08` renumbers motifs; classification output
   schemas and positive/negative overlap rules differ between scripts. A
   documented conversion is needed before new-run validation can reproduce the
   existing published tables.
6. **Peak/download identity:** cached nonempty files and fallback peaks are not
   equivalent to verifying the accession and checksum requested by the manifest.

## Fixes included with this audit

- Bound the CSV field limit to a Windows-compatible value in `08`; create its
  output directory before writing.
- Replace personal absolute paths in four auxiliary scripts with explicit CLI
  input/output options or repository-relative defaults.
- Create output parents in both iDiffIR summarizers, so README-style nested
  output paths work in a clean checkout.
- Add `tests/test_portability.py`. Run with:

```bash
python -m unittest discover -s tests -v
```

No thresholds, model architecture, sampling or scientific result tables were
changed by these fixes.

## Small local entry point

For the processed example and existing TF/RBP plot only, Python with NumPy,
pandas and Pillow is sufficient. The command below does not install the full
training or raw-data environment:

```bash
python -m pip install numpy pandas pillow
mkdir -p outputs/example
python scripts/01_filter_ir_events.py example/cufflinks/K562_genes.fpkm_tracking example/irfinder/K562_IRFinder-IR-dir.txt outputs/example/K562_IRs.bed outputs/example/K562_nonIRs.bed
python scripts/02_filter_bed_windows.py outputs/example/K562_IRs.bed outputs/example/K562_IRs.final.bed
python scripts/plot_tf_rbp_all_prediction_only.py
```

On PowerShell, create the directory with `New-Item -ItemType Directory -Force
outputs/example` instead of `mkdir -p`. Other Python commands are the same.

For the complete raw-data route, a Linux workstation or Linux environment with
the required tools is the next validation target, and the Slurm orchestration
must be adapted for non-cluster use. Neither `requirements.txt` nor
`environment.yml` was tested as a fresh complete installation in this audit.
Do not interpret the successful local checks as GPU training verification.

The declared PyTorch 1.12 source does expose `torch.amp.autocast`; that import
alone is not evidence of incompatibility:
[PyTorch v1.12 source](https://github.com/pytorch/pytorch/blob/v1.12.0/torch/amp/__init__.py).
PyBigWig documents native libcurl/zlib requirements:
[pyBigWig installation](https://github.com/deeptools/pyBigWig#installation).
