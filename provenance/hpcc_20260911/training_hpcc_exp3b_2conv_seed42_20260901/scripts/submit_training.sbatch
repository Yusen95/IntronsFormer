#!/bin/bash
#SBATCH --job-name=IF_exp3b_2conv
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=3-00:00:00
#SBATCH --output=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/training_hpcc_exp3b_2conv_seed42_20260901/logs/train_%j.out
#SBATCH --error=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/training_hpcc_exp3b_2conv_seed42_20260901/logs/train_%j.err

set -euo pipefail
RUN=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/training_hpcc_exp3b_2conv_seed42_20260901
PY=/rhome/yzhan677/bigdata/.conda/envs/performer/bin/python
cd "$RUN"
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
printf 'START %s
' "$(date -Is)"
printf 'HOST %s
' "$(hostname)"
printf 'JOB %s
' "$SLURM_JOB_ID"
nvidia-smi -L
"$PY" -u scripts/exp3b_2conv_rebuild.py
printf 'END %s
' "$(date -Is)"
