#!/usr/bin/env python3

from __future__ import annotations

import csv
from pathlib import Path

import prepare_encode_knockdown as kd


BASE = Path(r"C:\Users\Yusen Zhang\Documents\eCLIP data finding")
KNOCKDOWN_DIR = BASE / "outputs" / "knockdown"
COMPARISON = KNOCKDOWN_DIR / "knockdown_existing_vs_new.tsv"
FASTQS = KNOCKDOWN_DIR / "encode_knockdown_fastq_files.tsv"


def read_tsv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    selected = read_tsv(COMPARISON)
    fastqs = read_tsv(FASTQS)

    new_selected = [row for row in selected if row["Existing_Status"] == "need_new_run"]
    new_run_ids = {row["Run_ID"] for row in new_selected}
    new_fastqs = [row for row in fastqs if row["Run_ID"] in new_run_ids]

    write_tsv(KNOCKDOWN_DIR / "encode_knockdown_selected_NEW_ONLY.tsv", new_selected)
    write_tsv(KNOCKDOWN_DIR / "encode_knockdown_fastq_files_NEW_ONLY.tsv", new_fastqs)
    kd.write_download_script(KNOCKDOWN_DIR / "download_encode_knockdown_fastq_NEW_ONLY_HPCC.sh", new_fastqs)
    kd.write_run_script(KNOCKDOWN_DIR / "run_new_only_knockdown_irfinder_idiffir.sh", new_selected, new_fastqs)

    print(f"[INFO] New-only runs: {len(new_selected)}")
    print(f"[INFO] New-only FASTQ files: {len(new_fastqs)}")
    print(f"[INFO] Outputs written under {KNOCKDOWN_DIR}")


if __name__ == "__main__":
    main()
