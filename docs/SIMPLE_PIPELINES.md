# One command per workflow

`run_pipeline.py` connects the existing numbered scripts. It uses the active
Python environment, stops when a stage fails, and prints each command as it
runs. Install the environment described in the
[run guide](RUN_GUIDE.md) first. Run commands from the repository
root; all command lines below work in Bash and PowerShell.

## 1. Included preprocessing example (CPU)

```bash
python run_pipeline.py preprocess --example --output-dir outputs/example_run
```

This executes filtering and window construction together. Expected outputs:

```text
outputs/example_run/K562/IR.bed                 # 10,670 rows
outputs/example_run/K562/nonIR.bed              # 55,360 rows
outputs/example_run/K562/IR.windows.bed         # 10,354 rows
outputs/example_run/K562/nonIR.windows.bed      # 44,436 rows
```

The example ends at BED files. It does not contain the genome/BigWig inputs
needed for training and does not generate `datasets.txt`.

## 2. Full preprocessing: IRFinder/FPKM to model inputs

Copy [`config/preprocess.example.tsv`](../config/preprocess.example.tsv) to
`config/my_inputs.tsv` and replace the placeholder paths. Use one row per cell
line, with these tab-separated columns:

| Column | File |
| --- | --- |
| `sample` | Unique cell/sample name, e.g. `K562` |
| `fpkm` | Cufflinks `genes.fpkm_tracking` |
| `irfinder` | Selected IRFinder intron table |
| `fasta` | Genome FASTA |
| `chip` | H3K36me3 BigWig |
| `dnase` | DHS/DNase BigWig |
| `cpg_plus`, `cpg_minus` | Strand-specific CpG BigWigs |

Paths can be absolute or relative to the TSV's own directory. Do not quote TSV
paths merely because they contain spaces. For the eight-cell run, preserve this
row order: K562, GM12878, IMR-90, HepG2, H1, GM23248, HeLa-S3, SK-N-SH.

In the feature/model environment (NumPy, pandas, Biopython and pyBigWig):

```bash
python run_pipeline.py preprocess --manifest config/my_inputs.tsv --output-dir outputs/preprocessed --seed 1
```

One invocation performs both IR/nonIR branches: event filtering → length/flank
processing → sequence/signal extraction → labelled NPZ construction. Results
include `outputs/preprocessed/<sample>/model_input.npz` and
**`outputs/preprocessed/datasets.txt`**. The latter records the ordered NPZ paths
and is passed directly to training and interpretation. The driver preserves
the existing thresholds and up-to-4:1 nonIR sampling.

Full feature extraction needs pyBigWig; the tested Windows plotting environment
does not provide it. Use a configured Linux/HPCC environment for this stage.
The underlying sequence/coordinate caveats remain documented in
[the per-script audit](LOCAL_REPRODUCTION_CHECK.md).

**Starting from FASTQ:** the raw IRFinder/Cufflinks stages already have a single
Slurm submission entry point:

```bash
bash hpcc_full_rebuild/submit.sh
```

Configure its manifests, tools, references and paths as described in the
[HPCC guide](../hpcc_full_rebuild/README.md) before submitting. That command also
builds model inputs; do not run the TSV preprocessing route again unnecessarily.
Its eight existing NPZ files can be supplied to `train --datasets ...` directly
or listed one per line in a `datasets.txt` file. Relative entries in that list
are resolved against the list's directory. The unresolved reference setup is
not replaced by this driver.

## 3. Train with adjustable resource settings

Switch to the model environment first. Normal settings:

```bash
python run_pipeline.py train --dataset-list outputs/preprocessed/datasets.txt --output-dir outputs/model_run --batch-size 16 --accumulation-steps 4 --epochs 15
```

For a smaller GPU, try a smaller per-step batch:

```bash
python run_pipeline.py train --dataset-list outputs/preprocessed/datasets.txt --output-dir outputs/model_small_batch --batch-size 2 --accumulation-steps 32 --num-workers 0 --device cuda --precision auto
```

For a CPU run or a short execution check:

```bash
python run_pipeline.py train --dataset-list outputs/preprocessed/datasets.txt --output-dir outputs/model_cpu_check --device cpu --precision fp32 --batch-size 1 --accumulation-steps 1 --num-workers 0 --torch-threads 2 --epochs 1
```

| Option | Meaning / default |
| --- | --- |
| `--batch-size` | Samples per forward/backward pass; default 16 |
| `--accumulation-steps` | Passes per optimizer update; default 4 |
| `--epochs` | Training epochs; default 15 |
| `--device auto/cpu/cuda` | Auto selects CUDA when available, otherwise CPU |
| `--precision auto/fp32/bf16` | Auto uses BF16 only on supported CUDA GPUs, otherwise FP32 |
| `--num-workers` | DataLoader workers; driver default 0, convenient on Windows |
| `--torch-threads` | CPU computation threads; omitted retains PyTorch's default |
| `--seed` | Model/IG random seed; default 42 |

For complete accumulation groups, batch 2 × accumulation 32 gives 64 samples
per optimizer update, like batch 16 × accumulation 4. This is not a guarantee
of identical results: padding, numerical precision and stochastic operations
can differ. The historical training loop's behavior is retained: incomplete
accumulation groups at an epoch's end are not applied, and its scheduler counts
are based on batches. Use accumulation 1 to avoid a partial group. A run with
fewer training batches than the accumulation setting now fails explicitly
instead of finishing without any optimizer update.

Model architecture is unchanged. Reducing batch size reduces activation memory
but does not shrink the model or the in-memory dataset; CPU training can still
be slow and require substantial RAM. A one-epoch run checks execution and is
not a reproduction of the 15-epoch result. No automatic downsampling occurs.

Expected checkpoints: `best_2conv_auc.pt` and `best_2conv_loss.pt` in the selected
output directory. An explicit unsupported `--device cuda` or `--precision bf16`
fails with guidance rather than silently selecting another requested mode.

## 4. IG → motif extraction → MEME conversion

```bash
python run_pipeline.py interpret --dataset-list outputs/preprocessed/datasets.txt --checkpoint outputs/model_run/best_2conv_auc.pt --output-dir outputs/interpret_run --infer-batch-size 1 --internal-batch-size 1 --num-workers 0
```

This executes IG once and then processes both positive and negative outputs.
Results are in `ig/` and `motifs/` under the selected output directory. IG uses
50 steps by default (`--steps`), motif minimum length 5 (`--min-len`) and minimum
occurrence count 3 (`--count`). Smaller inference/internal batches can lower
working memory. `--precision` applies to inference; IG attribution itself
retains FP32 calculations. CPU selection and thread options also work here.

To include all four Tomtom searches and factor-name mapping, supply both
databases in the same command (Tomtom must be installed):

```bash
python run_pipeline.py interpret --dataset-list outputs/preprocessed/datasets.txt --checkpoint outputs/model_run/best_2conv_auc.pt --output-dir outputs/interpret_with_tomtom --infer-batch-size 1 --internal-batch-size 1 --tf-db /path/to/Homo_sapiens_2.0.meme --rbp-db metadata/knockdown/Homo_sapiens.meme
```

Use `--tomtom /path/to/tomtom` if it is not on PATH. The additional `tomtom/`
directory contains `tf_pos`, `tf_neg`, `rbp_pos` and `rbp_neg` results. Omitting
both database options intentionally ends at MEME conversion and prints that
Tomtom was omitted. The downstream candidate-table version gap remains open.

## 5. Re-create all four plot workflows

In the CPU plotting environment:

```bash
python run_pipeline.py plot
```

To also rebuild the intermediate tables from archived classification/support
and overlap summaries before plotting:

```bash
python run_pipeline.py plot --rebuild-tables
```

Plots retain the existing `outputs/` locations listed in the
[plot guide](PLOT_CODE_SYNC.md). This route regenerates those files in the
checkout; use a separate checkout to preserve existing outputs. It does not use an unfinished model
run or recompute the unresolved historical candidate classification.

## Inspect commands, logs and validation status

```bash
python run_pipeline.py --help
python run_pipeline.py train --help
python run_pipeline.py preprocess --manifest config/my_inputs.tsv --dry-run
python run_pipeline.py train --dataset-list outputs/preprocessed/datasets.txt --batch-size 2 --dry-run
```

Dry runs validate supplied file paths and print the planned commands without
executing them or writing output. They do not load NPZ data, import model
dependencies or prove hardware capacity. Full input validation still occurs
inside each computational script.

For preprocessing/training/interpretation, choose a **new or empty** output
directory. `run_commands.json` records the executed command plan and
`PIPELINE_COMPLETE` is written only after all selected stages succeed and
expected files exist. It certifies those selected stages, not the entire paper
workflow. A failed run is left intact for inspection; use a new output directory
to retry. Automatic resume is not implemented by the driver. To capture console
output on either shell, append `> run.log 2>&1` to a command.

Validation during this update: the actual K562 preprocessing example and all
four plots ran through the driver. Tests cover failure propagation, protection
of existing outputs, ordered dataset-list hand-off, resource-argument routing,
both motif signs and all four Tomtom dispatches. Hardware-selection logic uses
test doubles. Full BigWig preprocessing, model training, IG and Tomtom execution
were not rerun locally; the driver does not close the existing environment/data
gaps recorded in the run guide.
