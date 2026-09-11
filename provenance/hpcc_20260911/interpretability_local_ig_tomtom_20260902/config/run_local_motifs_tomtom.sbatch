#!/usr/bin/env bash
#SBATCH --job-name=IF_local_motif
#SBATCH --partition=batch
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=2-00:00:00
#SBATCH --output=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/interpretability_local_ig_tomtom_20260902/logs/postprocess_%j.out
#SBATCH --error=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/interpretability_local_ig_tomtom_20260902/logs/postprocess_%j.err


set -euo pipefail
RUN=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/interpretability_local_ig_tomtom_20260902
PY=/rhome/yzhan677/bigdata/.conda/envs/performer/bin/python
TOMTOM=/rhome/yzhan677/bigdata/.conda/envs/baseline/bin/tomtom
TFDB=/rhome/yzhan677/bigdata/CIS-BP/Homo_sapiens_2.0.meme
RBPDB=/rhome/yzhan677/bigdata/CIS-BP/Homo_sapiens.dna_encoded.meme
IG=$RUN/staging
OUT=$RUN/outputs
[[ -f "$OUT/IG_COMPLETE" ]]
mkdir -p "$OUT/motifs" "$OUT/tomtom"
"$PY" "$RUN/config/motif_extract.py" --direction pos --seq "$IG/ig_all_pos_sequence.csv" --score "$IG/ig_all_pos_score.csv" --out "$OUT/motifs/positive.csv" --min_len 5 --count 3
"$PY" "$RUN/config/motif_extract.py" --direction neg --seq "$IG/ig_all_neg_sequence.csv" --score "$IG/ig_all_neg_score.csv" --out "$OUT/motifs/negative.csv" --min_len 5 --count 3
"$PY" "$RUN/config/motif_to_meme.py" --in "$OUT/motifs/positive.csv" --out "$OUT/motifs/positive.meme"
"$PY" "$RUN/config/motif_to_meme.py" --in "$OUT/motifs/negative.csv" --out "$OUT/motifs/negative.meme"
for sign in positive negative; do
  "$TOMTOM" -oc "$OUT/tomtom/tf_$sign" -thresh 0.05 "$OUT/motifs/$sign.meme" "$TFDB"
  "$PY" "$RUN/config/tomtom_to_tf.py" --meme "$TFDB" --tomtom "$OUT/tomtom/tf_$sign/tomtom.tsv" --out "$OUT/tomtom/tf_$sign/matched_factors.csv" --qthresh 0.05
  "$TOMTOM" -oc "$OUT/tomtom/rbp_$sign" -thresh 0.05 "$OUT/motifs/$sign.meme" "$RBPDB"
  "$PY" "$RUN/config/tomtom_to_tf.py" --meme "$RBPDB" --tomtom "$OUT/tomtom/rbp_$sign/tomtom.tsv" --out "$OUT/tomtom/rbp_$sign/matched_factors.csv" --qthresh 0.05
done
touch "$OUT/INTERPRETABILITY_COMPLETE"
echo "completed=$(date -Is)"

