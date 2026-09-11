# Actual HPCC code snapshot

Recovered on 2026-09-11 from:
`/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/`.

All eight files in `manifest.tsv` were transferred without source changes and
verified against SHA256 computed on HPCC. Git line-ending conversion is disabled
for this directory to preserve those hashes. Five Python scripts and three
Slurm wrappers record the **actual run**, including the corrected `--seq`
argument in `run_local_motifs_tomtom.sbatch`.

| Actual script | Public entry point / status |
| --- | --- |
| `training_hpcc_exp3b_2conv_seed42_20260901/scripts/exp3b_2conv_rebuild.py` | `scripts/05_train_intronsformer.py` is the parameterized implementation; the original is archived here |
| `interpretability_local_ig_tomtom_20260902/config/ig_full_all.py` | `scripts/06_integrated_gradients.py` is the parameterized implementation |
| `config/motif_extract.py` within the interpretation directory | `scripts/07_extract_ig_motifs.py` |
| `config/motif_to_meme.py` within that directory | `scripts/08_motifs_to_meme.py`, including the Windows field-size fix |
| `config/tomtom_to_tf.py` within that directory | **Previously missing**, now `scripts/tomtom_to_tf.py`, with output-directory creation added |

The archived scripts retain HPCC-specific paths and execution behavior. They
are provenance, not the default portable commands. The public implementations
have additional CLI/path handling; identical filenames or matching architecture
settings do not establish numerical equivalence of a full training/IG run.

## Runtime evidence

The `runtime/` directory contains read-only observations at approximately
**2026-09-11 08:13 UTC**:

- Python **3.8.19**, PyTorch **1.12.0+cu113**, Captum **0.7.0**,
  performer-pytorch **1.1.4**, transformers **4.46.2**, numpy **1.24.3**.
  `packages.txt` is the observed environment inventory, not a tested clean
  installation lock file (the environment includes unrelated packages).
- The rebuilt training checkpoint and IG staging checkpoint have identical
  SHA256: `98c79031b60ea4ee088adeead1a90e98d26627cb544650c4a1c0ca8d21f4ccf4`.
  This differs from the older `model-v1.0.0` release checkpoint
  (`87262fadd1f4f9f4fd3b8f51e63904b68cc757a16061ab26d0e1bfe1e9cf9748`).
- The RBP database hash matches the repository's
  `metadata/knockdown/Homo_sapiens.meme`. Both database hashes are recorded.
- All eight IG dataset symlinks point to the rebuilt `group_*_model_input_seed1.npz`
  files; historical `*_raw.npz` link names do not refer to old model inputs.
- IG job **28020657 completed**. Done files contain 48,623 positive and 189,740
  negative entries (238,363 total). These are line counts, not a uniqueness or
  sequence/score alignment audit.
- Original postprocessing job **28020660 failed**. Corrected job **28292072 was
  still running**; `INTERPRETABILITY_COMPLETE` and final `matched_factors.csv`
  files were absent at the observation time. No jobs were submitted or cancelled.

The raw outputs in `runtime/` retain missing-file messages as evidence. The
latest plotting tables are historical analysis inputs; they have not been
silently replaced by unfinished September Tomtom outputs.

## Remaining publication gaps

The rebuilt checkpoint itself, exact input NPZ/reference hashes, complete
model-input validation report, persisted training split, IG alignment audit,
four completed Tomtom outputs and their downstream candidate/overlap mapping
are not yet distributed in this repository. Code recovery alone does not close
those gaps. The original training script does not save a split manifest, so that
manifest cannot simply be copied from its checkpoint output.
