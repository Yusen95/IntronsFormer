#!/usr/bin/env bash
#SBATCH --job-name=if_validate
#SBATCH --partition=short
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/logs/validate_%j.out
#SBATCH --error=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/logs/validate_%j.err

set -euo pipefail
RUN=/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830
PYTHON=/rhome/yzhan677/bigdata/.conda/envs/performer/bin/python

"$PYTHON" - "$RUN" <<'PY'
import csv
import json
import sys
from pathlib import Path

import numpy as np

run = Path(sys.argv[1])
cells = []
with (run / "config" / "samples.tsv").open() as handle:
    for row in csv.DictReader(handle, delimiter="\t"):
        cells.append(row["cell"])

report = {"run_root": str(run), "cells": {}, "all_valid": True}
for cell in cells:
    path = run / "outputs" / "model_inputs" / f"group_{cell}_model_input_seed1.npz"
    entry = {"path": str(path), "exists": path.is_file()}
    if not path.is_file():
        report["all_valid"] = False
        report["cells"][cell] = entry
        continue
    with np.load(path, allow_pickle=True) as data:
        array_keys = sorted(
            (k for k in data.files if k.startswith("arr_")),
            key=lambda k: int(k.split("_")[1]),
        )
        y = data["y"]
        bed_info = data["bed_info"]
        shapes = [data[k].shape for k in array_keys]
        channels_ok = all(len(s) == 2 and s[0] == 4 for s in shapes)
        finite_ok = all(np.isfinite(data[k]).all() for k in array_keys)
        labels = y.reshape(-1)
        entry.update(
            samples=len(array_keys),
            labels=int(labels.size),
            positives=int((labels == 1).sum()),
            negatives=int((labels == 0).sum()),
            bed_rows=int(len(bed_info)),
            channels_ok=channels_ok,
            finite_ok=finite_ok,
            valid=(
                len(array_keys) > 0
                and len(array_keys) == labels.size == len(bed_info)
                and channels_ok
                and finite_ok
            ),
        )
        if not entry["valid"]:
            report["all_valid"] = False
    report["cells"][cell] = entry

out = run / "outputs" / "validation_summary.json"
out.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
if not report["all_valid"]:
    raise SystemExit(1)
PY

date -Is > "$RUN/outputs/PIPELINE_COMPLETE"
