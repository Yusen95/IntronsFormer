#!/usr/bin/env python
from __future__ import print_function

import argparse
import csv
import io
import math
import os


CELL_LINES = ["HepG2", "K562", "GM12878"]

FIELDS = [
    "result_dir",
    "target",
    "cell_line",
    "run_id",
    "threshold",
    "all_events",
    "up_events",
    "down_events",
    "zero_logfc_events",
    "rows_read",
    "rows_valid_adjPValue",
    "rows_valid_logFoldChange",
    "status",
    "note",
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--idiffir-dir", default="~/bigdata/Project1/iDiffIR")
    parser.add_argument("--threshold", type=float, default=0.01)
    parser.add_argument("--out", default="idiffir_event_counts_from_allIntrons_adjP001.tsv")
    return parser.parse_args()


def parse_result_dir_name(name):
    for cell in CELL_LINES:
        suffix = "_result_" + cell
        if name.endswith(suffix):
            target = name[:-len(suffix)]
            return target, cell, target + "_" + cell

    base = name[:-len("_result")] if name.endswith("_result") else name
    for cell in CELL_LINES:
        suffix = "_" + cell
        if base.endswith(suffix):
            target = base[:-len(suffix)]
            return target, cell, base

    return base, "", base


def parse_float(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() in ("NA", "NAN", "NULL", "NONE"):
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    if math.isnan(parsed) or math.isinf(parsed):
        return None
    return parsed


def read_dict_rows(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as handle:
        lines = [line for line in handle if line.strip()]
    if not lines:
        return [], []
    reader = csv.DictReader(lines, delimiter="\t")
    return reader.fieldnames or [], list(reader)


def summarize_one(result_path, threshold):
    result_dir = os.path.basename(result_path.rstrip(os.sep))
    target, cell_line, run_id = parse_result_dir_name(result_dir)
    all_introns = os.path.join(result_path, "lists", "allIntrons.txt")

    row = {
        "result_dir": result_dir,
        "target": target,
        "cell_line": cell_line,
        "run_id": run_id,
        "threshold": str(threshold),
        "all_events": "",
        "up_events": "",
        "down_events": "",
        "zero_logfc_events": "",
        "rows_read": "0",
        "rows_valid_adjPValue": "0",
        "rows_valid_logFoldChange": "0",
        "status": "ok",
        "note": "",
    }

    if not os.path.exists(all_introns):
        row["status"] = "missing_allIntrons"
        row["note"] = all_introns
        return row

    try:
        fieldnames, rows = read_dict_rows(all_introns)
    except Exception as exc:
        row["status"] = "read_error"
        row["note"] = str(exc)
        return row

    missing_cols = []
    if "adjPValue" not in fieldnames:
        missing_cols.append("adjPValue")
    if "logFoldChange" not in fieldnames:
        missing_cols.append("logFoldChange")
    if missing_cols:
        row["status"] = "missing_columns"
        row["note"] = ",".join(missing_cols)
        return row

    up = 0
    down = 0
    zero = 0
    valid_adj = 0
    valid_lfc = 0

    for intron in rows:
        adj_p = parse_float(intron.get("adjPValue"))
        lfc = parse_float(intron.get("logFoldChange"))

        if adj_p is not None:
            valid_adj += 1
        if lfc is not None:
            valid_lfc += 1
        if adj_p is None or lfc is None:
            continue
        if adj_p >= threshold:
            continue

        if lfc > 0:
            up += 1
        elif lfc < 0:
            down += 1
        else:
            zero += 1

    row["all_events"] = str(up + down)
    row["up_events"] = str(up)
    row["down_events"] = str(down)
    row["zero_logfc_events"] = str(zero)
    row["rows_read"] = str(len(rows))
    row["rows_valid_adjPValue"] = str(valid_adj)
    row["rows_valid_logFoldChange"] = str(valid_lfc)
    return row


def write_tsv(path, rows):
    with io.open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    args = parse_args()
    idiffir_dir = os.path.abspath(os.path.expanduser(args.idiffir_dir))
    out_path = os.path.expanduser(args.out)

    rows = []
    if not os.path.isdir(idiffir_dir):
        raise SystemExit("[ERROR] Not a directory: {0}".format(idiffir_dir))

    for name in sorted(os.listdir(idiffir_dir)):
        path = os.path.join(idiffir_dir, name)
        if os.path.isdir(path) and "_result" in name:
            rows.append(summarize_one(path, args.threshold))

    write_tsv(out_path, rows)

    ok = len([row for row in rows if row["status"] == "ok"])
    print("[INFO] iDiffIR dir: {0}".format(idiffir_dir))
    print("[INFO] threshold: adjPValue < {0}".format(args.threshold))
    print("[INFO] wrote: {0}".format(out_path))
    print("[INFO] result dirs scanned: {0}".format(len(rows)))
    print("[INFO] ok rows: {0}".format(ok))
    if ok != len(rows):
        print("[WARN] rows needing check:")
        for row in rows:
            if row["status"] != "ok":
                print("  {0}\t{1}\t{2}".format(row["result_dir"], row["status"], row["note"]))


if __name__ == "__main__":
    main()
