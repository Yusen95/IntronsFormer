# Full input-to-results workflow

This guide maps the complete IntronsFormer workflow to the available files.
It distinguishes the original repository implementation from the
August–September 2026 HPCC rebuild. Matching step names do not establish that
the two versions are identical.

## Inputs and preparation

The eight cell lines are K562, GM12878, H1, IMR-90, HepG2, HeLa-S3, GM23248,
and SK-N-SH. Start with:

- [ENCODE file sources](../metadata/encode_data_sources.tsv): RNA-seq, H3K36me3,
  DHS and strand-specific CpG source identifiers, local aliases and provenance notes.
- [RNA-seq experiment sources](../metadata/rnaseq_sources.tsv).
- [Sample manifest](../hpcc_full_rebuild/samples.tsv): actual local input paths.
- [Library manifest](../hpcc_full_rebuild/replicates.tsv): read pairing and SE/PE layout.

Obtain the listed ENCODE files, preserving file-accession identities when local
names differ. Raw files are not committed. The reference genome is GRCh38 and
the stated annotation is Ensembl release 111. The historical scripts use
`Homo_sapiens.GRCh38.dna.primary_assembly.fa` and the IRFinder reference's
`transcripts.gtf`. The original reference-build recipe, checksums and complete
software environment exports still need to be archived before claiming a
fully self-contained raw-data reproduction.

H1 RNA-seq includes one library from each of ENCSR670WQY and ENCSR043RSE.
GM23248 is single-ended with two FASTQ files per processing group. The source
table flags an inferred GM23248 CpG minus accession and a mismatched SK-N-SH
CpG BED; the feature builder consumes CpG BigWigs, not that BED. Resolve these
notes by checking the actual input files rather than silently substituting data.

## Stage-by-stage map

Paths in the output column are relative to the HPCC rebuild directory unless
otherwise stated. See the [HPCC setup guide](../hpcc_full_rebuild/README.md)
before submission; those scripts retain author-specific paths.

| Stage | Available code / input | Output and next step | Packaging status |
| --- | --- | --- | --- |
| 1. Raw input and reference preparation | Source tables and both manifests above | FASTQ, reference, four BigWigs per cell | Files identified; automated downloads and exact reference setup remain to be packaged |
| 2. Per-library alignment and IR quantification | `hpcc_full_rebuild/01_irfinder_replicates.sbatch` | `outputs/irfinder_replicates/<cell>/<rep>/Unsorted.bam` | Rebuild script included |
| 3. Pool BAMs and re-quantify IR/expression | `hpcc_full_rebuild/02_combine_irfinder_fpkm.sbatch` | Combined IRFinder tables and `outputs/fpkm_combined/<cell>/genes.fpkm_tracking` | Rebuild script included |
| 4. Define IR/nonIR events | `scripts/01_filter_ir_events.py` | `outputs/beds/<cell>/*.raw.bed` | Repository script called by rebuild |
| 5. Filter length and extend windows | `scripts/02_filter_bed_windows.py` | `outputs/beds/<cell>/*.final.bed` | Repository script called by rebuild |
| 6. Extract sequence and signals | `scripts/03_build_feature_npz.py` | `outputs/raw_features/<cell>/*.npz` | Repository script called by rebuild; ambiguous-base alignment needs impact assessment |
| 7. Sample negatives and assemble model inputs | `scripts/04_create_training_dataset.py` | `outputs/model_inputs/group_<cell>_model_input_seed1.npz` | Repository script called by rebuild |
| 8. Validate model inputs | `hpcc_full_rebuild/03_validate.sbatch` | `outputs/validation_summary.json` | Structural validation included |
| 9. Train and evaluate | Repository: `scripts/05_train_intronsformer.py`; rebuild: frozen `exp3b_2conv_rebuild.py` | Checkpoint and validation/test metrics | Actual HPCC training copy, environment and split records still need recovery/comparison |
| 10. Compute integrated gradients | Repository: `scripts/06_integrated_gradients.py`; rebuild switched to `ig_full_all.py` | Sequence/score CSVs and selection/completion records | Actual HPCC copy and final wrapper still need recovery/comparison |
| 11. Extract motifs | Repository: `scripts/07_extract_ig_motifs.py`; rebuild: `motif_extract.py` | Positive and negative motif CSVs | Actual HPCC copy still needs recovery/comparison |
| 12. Convert motifs and match databases | Repository: `scripts/08_motifs_to_meme.py` and README Tomtom commands; rebuild: `motif_to_meme.py`, `tomtom_to_tf.py` | Positive/negative × TF/RBP matches | Final wrapper and four result sets still need archiving |
| 13. Build candidate lists | Existing `metadata/knockdown/Pos_TF.tsv`, `Neg_TF.tsv`, `Pos_RBP.tsv`, `Neg_RBP.tsv` | Candidate classes and selected assays | Mapping from new Tomtom results to these lists must be documented; existing lists are not automatically new-run results |
| 14. Binding occupancy validation | `scripts/run_binding_overlap_hpcc.sh`, `09_binding_overlap_analysis.py`, `10_plot_binding_occupancy.py`; selected peaks TSV | Occupancy summary and plots | Existing workflow included; event paths still target `Project1` |
| 15. Knockdown processing | `scripts/prepare_encode_knockdown.py`; `outputs/knockdown/` metadata and shell scripts | IRFinder and iDiffIR results | Existing workflow included; exact environment/reference setup still required |
| 16. Summarize and plot perturbation results | `scripts/summarize_tf_rbp_prediction_control_idiffir_counts_HPCC.py` and `scripts/plot_tf_rbp_all_prediction_only.py` | Event-count/statistics tables and figure | Existing processed tables and plotting route included; paper-wide figure mapping remains incomplete |

## Processing choices recorded for the rebuild

Each of the sixteen processing groups runs IRFinder separately. For a cell line,
the two BAMs are concatenated, query-name sorted and passed to IRFinder in BAM
mode. The same pooled BAM is coordinate-sorted for Cufflinks. This is pooled
read re-quantification, not averaging the two IRratio or FPKM tables.

The downstream thresholds remain those in the repository:

- Gene FPKM >= 1.
- IR: IRratio >= 0.1 and IntronDepth >= 10.
- nonIR: IRratio <= 0.01 and IntronDepth < 10.
- Intron length <= 10,000 bp, with 100 bp added on each side.
- Four channels: integer DNA, raw H3K36me3, raw DHS, strand-specific CpG.
- Negative-strand DNA is reverse-complemented; signals are reversed and CpG uses
  the minus-strand track. Missing signal values are filled with zero.
- Keep IR samples and sample up to four nonIR samples per IR, seed 1.

The feature builder currently removes non-ACGT bases while truncating signals
to the resulting length. Assess affected intervals before changing this rule;
changing it changes the input version and may require regeneration.

## Training, interpretation and model identity

The recorded training execution used this HPCC copy:

```text
/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/
  training_hpcc_exp3b_2conv_seed42_20260901/scripts/exp3b_2conv_rebuild.py
```

The source was `exp3b_2conv.py`; the recorded adjustment replaced eight input
NPZ paths. Reported settings were 3-mer, embedding 768, six Performer layers,
six heads, two convolutions, batch size 16, gradient accumulation 4, 15 epochs,
seed 42 and a grouped random 70/15/15 interval split. The run record reports
validation AUC 0.8433 and best-AUC checkpoint test AUC 0.8414; these values
still need to be linked to archived logs, exact inputs and checkpoint hashes.

The interpretation route switched to frozen local scripts under:

```text
/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/
  interpretability_local_ig_tomtom_20260902
```

The recorded route uses 50 IG steps, motif minimum length 5 and minimum count 3.
The final motif wrapper corrected `--sequence` to `--seq`. Recover that wrapper
along with its frozen Python files. Verify selection and CSV header behavior
against the outputs; the conversation's aggregate IG counts were inconsistent
and are not a substitute for a sample-level audit.

The recorded database files are `CIS-BP/Homo_sapiens_2.0.meme` (1,065 TF motifs)
and `CIS-BP/Homo_sapiens.dna_encoded.meme` (98 RBP motifs). The latter was
reported hash-identical to the included `metadata/knockdown/Homo_sapiens.meme`.
Archive database checksums and final Tomtom settings/results. The recorded
Tomtom version is 4.11.2. Four searches are required: positive/negative motifs
against each database. Historical status at 2026-09-11 07:20 UTC still showed
Tomtom running; it does not certify completion.

The existing `model-v1.0.0` Release predates this rebuild. Its same-named
`best_2conv_auc.pt` must not be identified as the rebuilt checkpoint without a
hash comparison. Preserve the distinction between original paper results and
rebuilt results, and associate each published figure/metric with its inputs,
script, split and checkpoint.

## Reproduction entry points

1. **Small processed example:** follow the main README's K562 filtering command.
2. **Raw FASTQ to model inputs:** configure and run `hpcc_full_rebuild/submit.sh`.
3. **Repository training and interpretation:** use the numbered commands in the
   main README, specifying the eight model-input paths. These commands are the
   repository implementation; equivalence to the frozen HPCC run remains to be checked.
4. **Existing downstream validation:** follow the main README's occupancy and
   knockdown sections. Explicitly supply the appropriate event inputs before
   interpreting the results as a continuation of the new rebuild.

For occupancy, `09_binding_overlap_analysis.py` currently expects original
intron BEDs under `Project1/IRevent/` and `Project1/nonIRevent/`. Do not silently
substitute flanked feature windows. The new-run hand-off and candidate-list
derivation need an explicit reviewed mapping.

## Remaining files to archive from the successful run

- Frozen training/IG/motif/Tomtom Python scripts and final Slurm wrappers.
- Actual reference configuration and tool/environment exports.
- Model-input validation report, file hashes and per-cell counts.
- Ordered input list, training split, evaluation outputs and checkpoint hash.
- IG selection/done metadata and reconciled sequence/score counts.
- Both motif database identities, four Tomtom outputs and candidate derivation.
- A paper figure/table inventory with commands and input/output versions.

This guide describes available code and recorded behavior. It is not a claim
that a clean checkout has already passed the complete raw-input-to-paper workflow.
