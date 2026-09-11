# HPCC full model-input rebuild

This run starts from the raw RNA-seq FASTQ files in `/rhome/yzhan677/bigdata/fastq`.
It does not read IRFinder, FPKM, BED, raw feature NPZ, or model-input NPZ files from
`Project1` or any earlier run.

Each biological replicate is run through IRFinder independently. For GM23248,
each replicate contains two single-end FASTQ files, so only the files belonging to
the same replicate are streamed together. The two newly generated replicate BAMs
are then concatenated and explicitly query-name sorted before a second
`IRFinder -m BAM` run. The same combined BAM is coordinate-sorted for Cufflinks.

The Slurm dependency chain is:

1. `01_irfinder_replicates.sbatch`: run IRFinder 1.3.1 separately for all 16
   cell-line/replicate combinations.
2. `02_combine_irfinder_fpkm.sbatch`: `samtools cat` the two replicate BAMs,
   query-name sort the combined stream, re-run IRFinder in BAM mode, then
   coordinate-sort that combined BAM and run Cufflinks 2.2.1.
3. `02_model_inputs.sbatch`: apply the repository IR/nonIR and FPKM thresholds,
   restrict introns to 10 kb, add 100-bp flanks, extract sequence, H3K36me3, DHS,
   and strand-specific CpG tracks, then sample nonIR at up to 4:1 with seed 1.
4. `03_validate.sbatch`: verify all eight NPZ files, channel count, labels, BED
   metadata, and finite feature values.

All outputs, logs, job IDs, tool/input records, and code hashes are written below
`/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830`.

## Included input manifests

- `samples.tsv`: eight cell lines, RNA-seq files and the four signal BigWigs
  (H3K36me3, DHS, CpG plus and CpG minus).
- `replicates.tsv`: sixteen processing groups with explicit PE/SE layout and
  read-file pairing. The `rep1`/`rep2` labels are local processing identifiers;
  consult `../metadata/encode_data_sources.tsv` for original ENCODE replicates.
  In particular, H1 combines libraries from two experiments, and SK-N-SH uses
  ENCODE biological replicates 3 and 4.

The source table records ENCODE accessions and local renamed CpG files. Preserve
its unresolved provenance notes when preparing downloads. Most RNA-seq paths
refer to decompressed FASTQ; HepG2 paths retain `.fastq.gz`.

## Setup and submission

These are the original UCR HPCC paths, not a portable environment installer.
Before submitting on another account, edit the absolute paths in `submit.sh`,
all four `.sbatch` files (including `#SBATCH` log paths), and both TSV manifests.
Use a new run directory for a new reproduction. Existing completion markers
cause the stage scripts to skip work.

Required existing inputs and software:

- FASTQ and BigWig files listed in the manifests.
- `Homo_sapiens.GRCh38.dna.primary_assembly.fa`.
- A compatible IRFinder reference at `refDir`, including `transcripts.gtf`;
  the exact reference-build procedure still needs to be recovered.
- IRFinder 1.3.1 and its alignment dependencies in the `align` environment.
- Cufflinks 2.2.1 and samtools at `$RUN/envs/cufflinks/bin/`.
- Python with NumPy, pandas, Biopython and pyBigWig in the `performer` environment.
- Slurm partitions and memory/time limits appropriate to your cluster.

After setup, from the repository root:

```bash
bash hpcc_full_rebuild/submit.sh
```

The submission entry point installs missing manifests into `$RUN/config/` and
missing Slurm scripts into `$RUN/scripts/`, copies repository preprocessing
scripts, checks input paths, and submits the four-stage dependency chain.
It does not replace existing manifests or Slurm scripts. The deployment copy
step was added during repository packaging; it is not an algorithm change.

## Outputs and hand-off

Under the run directory:

| Stage | Output |
| --- | --- |
| Per-library IRFinder | `outputs/irfinder_replicates/<cell>/rep1/` and `rep2/` |
| Combined IRFinder | `outputs/irfinder_combined/<cell>/` |
| Combined expression | `outputs/fpkm_combined/<cell>/genes.fpkm_tracking` |
| Event intervals | `outputs/beds/<cell>/<cell>.IR.raw.bed`, `.nonIR.raw.bed`, `.IR.final.bed`, `.nonIR.final.bed` |
| Sequence/signal features | `outputs/raw_features/<cell>/group_<cell>_IR_raw.npz` and `group_<cell>_nonIR_raw.npz` |
| Training inputs | `outputs/model_inputs/group_<cell>_model_input_seed1.npz` |
| Validation | `outputs/validation_summary.json`, `outputs/PIPELINE_COMPLETE` |
| Provenance | `provenance/`, stage records under `outputs/completion/` |

The historical rebuild record reports use of `IRFinder-IR-nondir.txt` for all
eight cell lines. The archived scripts still select the first matching
`IRFinder-IR-*.txt`; verify and record the selected table before a new run.
The K562 repository example uses `IRFinder-IR-dir.txt` and is a separate example.

The validation checks shapes, counts and finite values; it does not prove
reference identity, biological equivalence, or sequence/signal alignment.
Training and subsequent analysis are described in
[`../docs/FULL_WORKFLOW.md`](../docs/FULL_WORKFLOW.md).
