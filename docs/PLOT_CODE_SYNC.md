# Plot code synchronized on 2026-09-11

This update follows the latest plotting code found in the **eCLIP data finding**
and **Powerpoint update** projects. Filenames such as `Figure5` and `Figure7`
are retained from those projects; they are **not a mapping to the current
manuscript's figure numbers**. The manuscript PDF overlay helper is not a
data-to-figure script and is not part of this workflow.

## Re-create the plots locally

Use a separate Python 3.12 environment for plotting:

```bash
python -m venv .venv-plots
# Linux/macOS: source .venv-plots/bin/activate
# Windows PowerShell: .venv-plots/Scripts/Activate.ps1
python -m pip install -r requirements-plotting.txt
python scripts/make_paper_ir_found_control_log2_permutation_figure.py
python scripts/plot_tf_rbp_all_prediction_only.py
python scripts/make_figure5_submission_current_data_pil.py
python scripts/figure5_tf_positive_plus_both.py
```

Run these commands from the repository root. Windows uses Arial when available;
Linux needs DejaVu Sans (for example, the `fonts-dejavu-core` distribution
package). Font choice can change PNG pixels without changing the statistics.
This plotting environment is separate from the Python 3.8 HPCC model environment.

| Plot content / source revision | Entry point under `scripts/` | Inputs under `outputs/` | Output directory under `outputs/` |
| --- | --- | --- | --- |
| IR/nonIR occupancy ratio, latest August 19 style | `make_paper_ir_found_control_log2_permutation_figure.py` | `ir_nonir_ratio_analysis/ir_nonir_ratio_combined_rows.tsv` | `ir_nonir_ratio_analysis/` (`Figure5.png`, `.svg`, points and statistics) |
| TF/RBP differential IR event counts, latest August 19 style | `plot_tf_rbp_all_prediction_only.py` | `encode_current_prediction_perturbation_check/encode_prediction_vs_control_event_counts.tsv`; `event_count_comparison/prediction_pos_both_neg_control_event_counts.tsv` | `direction_specific_original_counts/` (`Figure7.png`, `.svg`, points and statistics) |
| Selected TF/RBP up/down event bars, July 2 source | `make_figure5_submission_current_data_pil.py` | `figure5_original_style/knockdown_results_draft_compatible.csv`; `figure5_original_style/knockdown_results_download_snapshot.csv` | `figure5_submission_current_data/` |
| Powerpoint project's TF positive + both, June 8 source | `figure5_tf_positive_plus_both.py` | `figure5_original_style/knockdown_results_download_snapshot.csv` | `figure5_tf_positive_plus_both/` |

The first two import `make_publication_ir_ratio_figures.py`, now included. The
bar plots preserve their existing selection rules and labels; synchronizing
these scripts does not certify their correspondence to a manuscript figure.
In particular, the July bar script historically defaults unlabelled cell lines
to K562 and does not show cell lines on every bar. Use its selected-target TSV
to inspect the two YBX1 experiments separately.

Source file SHA256 values are recorded in
[`plot_source_manifest.tsv`](../provenance/plot_source_manifest.tsv). Changes
from those sources are limited to repository-relative input paths, explicit
classification input selection and scalable DejaVu font fallback. Statistical
tests, permutations, seeds and target-selection rules were retained.
Input identities are recorded in
[`plot_input_manifest.tsv`](../provenance/plot_input_manifest.tsv), with line
endings normalized to LF before hashing to support Windows and Linux checkouts.

## Re-create intermediate plotting inputs

Three overlap summaries are included, allowing the ratio table to be rebuilt:

```bash
python scripts/plot_ir_nonir_ratio_analysis.py --summary outputs/ir_nonir_ratio_analysis/baseline_like_overlap_three_class_summary.tsv --summary outputs/ir_nonir_ratio_analysis/baseline_like_overlap_three_class_summary_control.tsv --summary outputs/ir_nonir_ratio_analysis/control_rbp_only_summary.tsv --out_dir outputs/ir_nonir_ratio_analysis
```

The rebuilt table matches the archived table numerically. `Source_File` will
contain repository-relative paths instead of the original workstation paths.
Historical `Peak_file` and `Source_File` columns are provenance, not files read
by the plotting scripts. Rebuilding overlaps from peaks still requires the
event BEDs and peak files described in the full workflow guide.

The classified iDiffIR table and ENCODE support table have also been restored:

```bash
python scripts/summarize_encode_prediction_vs_control_event_counts.py
python scripts/summarize_prediction_pos_both_neg_with_control_event_counts.py
python scripts/cellline_stratified_prediction_control_results.py
```

The first two commands reproduce both checked-in event-count plotting inputs.
The September 10 correction `YBX1_result -> K562` is propagated to the raw count
snapshot and classified table so these commands retain it. The HepG2 experiment
is separate; event counts are unchanged (K562 412; HepG2 178).

**An earlier step is still unresolved:** the restored
`classify_idiffir_counts_and_plot.py` produces 87 classified rows with the
current `metadata/knockdown/Pos_*` and `Neg_*` files, whereas the historical table
contains 95. This is a version mismatch, not a missing plotting dependency.
The affected runs are listed in
[`classification_version_mismatch.tsv`](../provenance/classification_version_mismatch.tsv).
It now requires `--candidate-dir` and defaults to a separate output directory:

```bash
python scripts/classify_idiffir_counts_and_plot.py --candidate-dir /path/to/verified_historical_lists --out-dir outputs/classification_rebuild
```

Do not replace the archived classification until the four original lists have
been identified and compared. Exact-name searches in the local source project
and a bounded HPCC search did not locate them. They may exist under different
names or in deeper directories. No candidate labels were invented to force
agreement with the historical table.

## Verification performed

- All four plotting entry points executed successfully on Windows/Python 3.12
  using the pinned plotting environment and included inputs.
- Rebuilt both event-count inputs from the archived classification and support
  tables; every row and field matched the checked-in inputs.
- Rebuilt the occupancy ratio input from the three summaries; all columns
  matched except the expected `Source_File` path changes.
- Cell-line summary generation succeeded.
- The five repository unit tests passed, including restored Tomtom mapping.
- Eight frozen HPCC files were recovered and verified against source SHA256.

These checks establish local replotting from the included tables. They do not
establish a complete raw-FASTQ-to-new-figures rerun; see
[`FULL_WORKFLOW.md`](FULL_WORKFLOW.md) and the
[HPCC snapshot notes](../provenance/hpcc_20260911/README.md).
