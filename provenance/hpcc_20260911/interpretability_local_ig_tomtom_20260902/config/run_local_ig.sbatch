#!/usr/bin/env bash
#SBATCH --job-name=IF_local_IG
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=7-00:00:00
#SBATCH --output=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/interpretability_local_ig_tomtom_20260902/logs/ig_%j.out
#SBATCH --error=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/interpretability_local_ig_tomtom_20260902/logs/ig_%j.err

set -euo pipefail
RUN=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/interpretability_local_ig_tomtom_20260902
PY=/rhome/yzhan677/bigdata/.conda/envs/performer/bin/python
cd "$RUN/staging"
[[ -s best_2conv_auc.pt ]]
for f in Project1/Dataset/group_*_raw.npz; do [[ -s "$f" ]]; done
echo "start=$(date -Is) host=$(hostname) job=$SLURM_JOB_ID"
nvidia-smi -L
"$PY" "$RUN/config/ig_full_all.py"
[[ -s selection_all.npz ]]
[[ -s ig_all_pos_sequence.csv ]]
[[ -s ig_all_pos_score.csv ]]
[[ -s ig_all_neg_sequence.csv ]]
[[ -s ig_all_neg_score.csv ]]
touch "$RUN/outputs/IG_COMPLETE"
echo "completed=$(date -Is)"
