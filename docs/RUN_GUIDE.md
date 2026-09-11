# Running the workflow

For fewer manual steps, use the [single-command pipelines](SIMPLE_PIPELINES.md):
`run_pipeline.py preprocess`, `train`, `interpret` and `plot`. The detailed
commands below remain available for examining individual stages.

This guide provides executable commands, their prerequisites and expected
outputs. Start with **A** to check the included data and re-create the plots.
Use **B–D** for a new model run after supplying the external data and software.
**E** describes downstream validation and the remaining breaks in that chain.
Replotting the archived tables and reproducing a newly trained model are separate
checks. Figure filenames retain their source-project names, not current
manuscript numbering.

| Route | Required resources | Verification status |
| --- | --- | --- |
| A: included example and plots | Git, Python 3.12, CPU; no model download | Executed locally with included data |
| B: raw FASTQ to model inputs | Linux, Slurm, FASTQ/BigWig/reference files, IRFinder/Cufflinks | Setup-dependent; not a clean-checkout test |
| C–D: training, IG and motifs | Eight model-input NPZ files, model environment, GPU recommended, Tomtom databases | Commands correspond to public script interfaces; full numerical equivalence to the frozen HPCC run is not certified |
| E: binding/knockdown validation | Event BEDs, peaks, knockdown data, iDiffIR environment | Historical commands available; new-run hand-off remains incomplete |

## A. Run the included example and re-create the plots

### A1. Clone the repository

```bash
git clone https://github.com/Yusen95/IntronsFormer.git
cd IntronsFormer
git rev-parse HEAD
```

Record the printed commit with your results. Run subsequent commands from this
directory. Plotting regenerates files under `outputs/`, so use this dedicated
checkout rather than a directory containing other results.

### A2. Install the CPU plotting environment

Linux/macOS, with Python 3.12 installed:

```bash
python3.12 -m venv .venv-plots
source .venv-plots/bin/activate
python -m pip install -r requirements-plotting.txt
```

Windows PowerShell, with Python 3.12 installed:

```powershell
py -3.12 -m venv .venv-plots
.\.venv-plots\Scripts\Activate.ps1
python -m pip install -r requirements-plotting.txt
```

If PowerShell does not permit activation, use
`.\.venv-plots\Scripts\python.exe` in place of `python` in every command;
activation is not required. PNG rendering needs Arial or DejaVu Sans. On a
Debian/Ubuntu machine without fonts, install `fonts-dejavu-core` using your
normal package-management procedure. Different fonts may change pixels.

### A3. Run the small preprocessing example

These single-line commands work in Bash and PowerShell:

```bash
python -c "from pathlib import Path; Path('outputs/run_example').mkdir(parents=True, exist_ok=True)"
python scripts/01_filter_ir_events.py example/cufflinks/K562_genes.fpkm_tracking example/irfinder/K562_IRFinder-IR-dir.txt outputs/run_example/K562_IRs.bed outputs/run_example/K562_nonIRs.bed
python scripts/02_filter_bed_windows.py outputs/run_example/K562_IRs.bed outputs/run_example/K562_IRs_windows.bed
python scripts/02_filter_bed_windows.py outputs/run_example/K562_nonIRs.bed outputs/run_example/K562_nonIRs_windows.bed
python -c "from pathlib import Path; p=Path('outputs/run_example'); n=[sum(1 for _ in (p/f).open()) for f in ['K562_IRs.bed','K562_nonIRs.bed']]; print('IR, nonIR:', n); assert n == [10670, 55360]"
```

Expected: 10,670 IR and 55,360 nonIR rows **before** length filtering. The two
`*_windows.bed` files contain 10,354 IR and 44,436 nonIR rows after filtering;
these are filtered/flanked feature inputs. They are not the
original intron-coordinate inputs for binding analysis. This small example
uses the included directional K562 IRFinder table; it is separate from the
eight-cell HPCC rebuild.

### A4. Re-create all four included plot workflows

```bash
python scripts/make_paper_ir_found_control_log2_permutation_figure.py
python scripts/plot_tf_rbp_all_prediction_only.py
python scripts/make_figure5_submission_current_data_pil.py
python scripts/figure5_tf_positive_plus_both.py
```

| Command, in the order above | Main output under `outputs/` |
| --- | --- |
| Occupancy-ratio plot | `ir_nonir_ratio_analysis/Figure5.png` and `.svg` |
| TF/RBP event-count plot | `direction_specific_original_counts/Figure7.png` and `.svg` |
| Selected up/down bars | `figure5_submission_current_data/Figure5_knockdown_TF_all_IR_shared_selected_nonIR_RBP_K562_HepG2_submission.png` and `.pdf` |
| Powerpoint-project bars | `figure5_tf_positive_plus_both/Figure5_knockdown_color_hatch_combined_tf_positive_plus_both.png` and `.pdf` |

Statistics and selected/point-level tables are written alongside the images.
Inspect numerical outputs as well as images:

```bash
python -c "import pandas as pd; p='outputs/direction_specific_original_counts/tf_rbp_all_prediction_only_stats.tsv'; print(pd.read_csv(p, sep='\t').to_string(index=False))"
python -c "import pandas as pd; p='outputs/ir_nonir_ratio_analysis/paper_ir_found_control_hepg2_k562_log2_summary.tsv'; print(pd.read_csv(p, sep='\t').to_string(index=False))"
python -m unittest discover -s tests -v
```

Expected event-count comparison: TF candidate/control counts **5/15**, means
**344.2/213.4**, permutation p approximately **0.00664**; RBP counts **43/8**,
means **260.0233/245.875**, p approximately **0.7494**. Occupancy comparison:
TF counts **20/21**, p approximately **0.001106**; RBP counts **10/7**,
p approximately **0.25350**. These tests operate on different row populations.
The original packaging check contained five unit tests; additional pipeline
tests now also run through this command.

### A5. Optionally rebuild the tables used for plotting

First rebuild event-count inputs from the archived classification/support:

```bash
python scripts/summarize_encode_prediction_vs_control_event_counts.py
python scripts/summarize_prediction_pos_both_neg_with_control_event_counts.py
python scripts/cellline_stratified_prediction_control_results.py
```

Then rebuild occupancy ratios from the three archived overlap summaries:

```bash
python scripts/plot_ir_nonir_ratio_analysis.py --summary outputs/ir_nonir_ratio_analysis/baseline_like_overlap_three_class_summary.tsv --summary outputs/ir_nonir_ratio_analysis/baseline_like_overlap_three_class_summary_control.tsv --summary outputs/ir_nonir_ratio_analysis/control_rbp_only_summary.tsv --out_dir outputs/ir_nonir_ratio_analysis
```

Re-run A4 to draw those regenerated tables. These intermediate calculations
were verified against the archived plotting inputs; the ratio table's
`Source_File` paths change when rebuilt in a new checkout.

**Do not regenerate the historical classification using the current candidate
lists and expect identical results:** that earlier step currently yields 87
rows versus the archived 95. The archived classification is the supported
starting point for A5. See the [version mismatch record](../provenance/classification_version_mismatch.tsv).

## B. Rebuild model inputs from raw FASTQ (Linux/Slurm)

This section is a conditional runbook, not an unattended installation command.
Before submission, obtain all FASTQ/BigWig files listed in
`hpcc_full_rebuild/samples.tsv` and `replicates.tsv`, the genome FASTA, and a
compatible IRFinder reference. ENCODE source identities are in
`metadata/encode_data_sources.tsv`. The exact reference-build recipe and some
source provenance remain unresolved; see [FULL_WORKFLOW.md](FULL_WORKFLOW.md).

Configure IRFinder 1.3.1, Cufflinks 2.2.1, samtools and the feature-extraction
Python environment. Edit **both TSV manifests, `submit.sh` and all four sbatch
files**, including tool paths, reference paths, `RUN`, `REPO`, Slurm partitions
and log paths. Merely exporting `RUN` does not override assignments inside
these files. Use a new run directory; existing completion markers skip work.
The [HPCC setup guide](../hpcc_full_rebuild/README.md) lists the exact prerequisites.

After configuration:

```bash
bash -n hpcc_full_rebuild/submit.sh
for f in hpcc_full_rebuild/*.sbatch; do bash -n "$f"; done
bash hpcc_full_rebuild/submit.sh
```

Set `RUN_DIR` below to the **same directory configured in the scripts**:

```bash
RUN_DIR=/absolute/path/to/your/new_run
cat "$RUN_DIR/provenance/slurm_jobs.tsv"
squeue -u "$USER"
```

The dependency chain is replicate IRFinder → combined IRFinder/Cufflinks →
feature/model-input construction → validation. After jobs finish:

```bash
test -f "$RUN_DIR/outputs/PIPELINE_COMPLETE"
python -m json.tool "$RUN_DIR/outputs/validation_summary.json"
ls -lh "$RUN_DIR"/outputs/model_inputs/group_*_model_input_seed1.npz
```

Expected: eight model-input NPZ files and a validation report. Inspect job logs
if the marker is absent; scheduler completion alone does not certify biological
or reference equivalence. No complete clean-machine raw-data run has been
verified for this release.

## C. Train a model from the eight NPZ files (Linux/Bash)

Leave the plotting environment and prepare the model environment:

```bash
deactivate
conda env create -f environment.yml
conda activate intronsformer
python -c "import torch, numpy, pandas, captum, performer_pytorch, transformers; print('torch:', torch.__version__, 'CUDA:', torch.cuda.is_available())"
```

Skip `deactivate` if no venv is active. `environment.yml` is a starting
specification; restoration in a clean environment has not been validated.
Compare installed versions with [the observed HPCC package inventory](../provenance/hpcc_20260911/runtime/packages.txt).
The actual run used Python 3.8.19/PyTorch 1.12.0+cu113 and an A100, with 64 GB
requested for training and 96 GB for IG. These are historical allocations, not
measured minimum requirements. Run long calculations on an allocated compute
node, following your cluster's policy.

With `RUN_DIR` set as in B, preserve this dataset order:

```bash
MODEL_INPUT_DIR="$RUN_DIR/outputs/model_inputs"
datasets=()
for cell in K562 GM12878 IMR-90 HepG2 H1 GM23248 HeLa-S3 SK-N-SH; do
  f="$MODEL_INPUT_DIR/group_${cell}_model_input_seed1.npz"
  test -s "$f" || { echo "Missing input: $f"; exit 1; }
  datasets+=("$f")
done
python scripts/05_train_intronsformer.py --datasets "${datasets[@]}" --output-dir outputs/run_model --epochs 15 --batch-size 16 --num-workers 4 --seed 42 --k-mer 3
ls -lh outputs/run_model/best_2conv_auc.pt outputs/run_model/best_2conv_loss.pt
sha256sum outputs/run_model/best_2conv_auc.pt
```

The script prints validation and final-test metrics. Record stdout, the input
identities, environment and checkpoint hash. A newly trained model need not
have the same hash or exactly the same metrics across hardware/environments.
The frozen actual HPCC source is preserved in [provenance](../provenance/hpcc_20260911/README.md).

## D. Run IG, motif extraction and four Tomtom searches

Continue in the same Bash session/model environment with `datasets` from C.
Use the checkpoint just trained, and a fresh IG output directory:

```bash
python scripts/06_integrated_gradients.py --datasets "${datasets[@]}" --checkpoint outputs/run_model/best_2conv_auc.pt --output-dir outputs/run_ig --steps 50 --internal-batch-size 10 --infer-batch-size 32 --num-workers 4 --seed 42
mkdir -p outputs/run_motifs
for sign in pos neg; do
  python scripts/07_extract_ig_motifs.py --direction "$sign" --seq "outputs/run_ig/ig_all_${sign}_sequence.csv" --score "outputs/run_ig/ig_all_${sign}_score.csv" --out "outputs/run_motifs/${sign}.csv" --min_len 5 --count 3
  python scripts/08_motifs_to_meme.py --in "outputs/run_motifs/${sign}.csv" --out "outputs/run_motifs/${sign}.meme"
done
```

IG writes paired positive/negative sequence and score CSVs, selection metadata
and `.done` progress files. Reuse an IG directory only when resuming with the
same ordered inputs, checkpoint and settings. The script does not bind its
resume files to their hashes.

Install/configure Tomtom, and provide the TF database at the path below. The
RBP database is already included and matches the HPCC database hash:

```bash
TF_DB=/absolute/path/to/CIS-BP/Homo_sapiens_2.0.meme
RBP_DB="$PWD/metadata/knockdown/Homo_sapiens.meme"
test -s "$TF_DB"
test -s "$RBP_DB"
sha256sum "$TF_DB" "$RBP_DB"
mkdir -p outputs/run_tomtom
for sign in pos neg; do
  tomtom -oc "outputs/run_tomtom/tf_${sign}" -thresh 0.05 "outputs/run_motifs/${sign}.meme" "$TF_DB"
  python scripts/tomtom_to_tf.py --meme "$TF_DB" --tomtom "outputs/run_tomtom/tf_${sign}/tomtom.tsv" --out "outputs/run_tomtom/tf_${sign}/matched_factors.csv" --qthresh 0.05
  tomtom -oc "outputs/run_tomtom/rbp_${sign}" -thresh 0.05 "outputs/run_motifs/${sign}.meme" "$RBP_DB"
  python scripts/tomtom_to_tf.py --meme "$RBP_DB" --tomtom "outputs/run_tomtom/rbp_${sign}/tomtom.tsv" --out "outputs/run_tomtom/rbp_${sign}/matched_factors.csv" --qthresh 0.05
done
```

Compare database hashes with [database_sha256.txt](../provenance/hpcc_20260911/runtime/database_sha256.txt).
Expected: four Tomtom result directories, each containing `tomtom.tsv` and
`matched_factors.csv`. Mapping to factor names does not automatically generate
the historical peak-selection and perturbation-classification inputs.

### Optional: use the older released checkpoint

To inspect the original release instead of training, download it explicitly:

```bash
mkdir -p models
curl --fail -L -o models/best_2conv_auc.pt https://github.com/Yusen95/IntronsFormer/releases/download/model-v1.0.0/best_2conv_auc.pt
sha256sum models/best_2conv_auc.pt
```

Expected SHA256:
`87262fadd1f4f9f4fd3b8f51e63904b68cc757a16061ab26d0e1bfe1e9cf9748`.
Use that path as `--checkpoint` in D and a **different IG output directory**.
This is not the September rebuilt model, whose observed hash starts `98c79031`.
The release checkpoint alone does not provide the eight matching NPZ datasets.

## E. Downstream binding and knockdown validation

These commands require the original event/reference layout and external tools;
they do not form an automatic continuation of D. The selected candidate table
is historical. The exact new-Tomtom-to-candidate-table mapping remains open.

### Binding occupancy

Prepare `BASE_DIR/Project1/IRevent/`, `BASE_DIR/Project1/nonIRevent/` and
`BASE_DIR/Homo_sapiens.GRCh38.111.gtf` as described in the
[binding section of the README](../README.md#binding-occupancy-validation).
Supply the original intron BEDs for all cells expected by the analysis; do not
copy the flanked feature windows from A3 into these locations.

```bash
BASE_DIR=/absolute/path/to/validation_data bash scripts/run_binding_overlap_hpcc.sh
```

Expected summary:
`BASE_DIR/baseline14_event_overlap_pos_both_neg_tsv_no_first_intron_length_adjusted_start_in_gene/baseline_like_overlap_three_class_summary.tsv`.
This candidate-only run does not recreate the two historical control summaries
used in A5; their complete raw-data recreation is not packaged here.

### Knockdown/iDiffIR

Prepare the `idiffir_py2` conda environment, `convertBam.sh`, IRFinder reference
and transcript-only GTF before running this batch on a compute node. The
generated script expects `IDIFFIR_DIR=BASE_DIR/Project1/iDiffIR`, because BAM
paths inside it are relative to that layout. It activates `idiffir_py2` itself.

```bash
BASE_DIR=/absolute/path/to/validation_data
BASE_DIR="$BASE_DIR" bash outputs/knockdown/download_encode_knockdown_fastq_HPCC.sh
BASE_DIR="$BASE_DIR" IRFINDER_REF="$BASE_DIR/refDir" IDIFFIR_DIR="$BASE_DIR/Project1/iDiffIR" GTF="$BASE_DIR/Homo_sapiens.GRCh38.111.transcript_only.gtf" bash outputs/knockdown/run_all_knockdown_irfinder_idiffir.sh
```

Result directories contain `lists/allDIRs.txt`, `upDIRs.txt` and `downDIRs.txt`.
For count-summary commands, follow the
[knockdown README section](../README.md#knockdown-perturbation-validation).
Those newly classified results must not silently replace A5's archived table:
the original four candidate-list versions are still unresolved.

## What to report if a command fails

Include the repository commit (`git rev-parse HEAD`), route/step, exact command,
Python/package versions, input file identities and the full error output.
For Slurm, include the failed job ID and its stdout/stderr log. Passing A
demonstrates replotting and the included preprocessing example; it does not
certify a completed B–E raw-data reproduction.
