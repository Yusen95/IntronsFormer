#!/usr/bin/env python
from __future__ import print_function

import argparse
import io
import os
import re


CELL_LINES = ["HepG2", "K562", "GM12878"]

TF_CONTROL_RUN_IDS = set([
    "USF1_K562",
    "SRF_K562",
    "FOXM1_K562",
    "MITF_K562",
    "NFATC1_K562",
    "STAT6_K562",
    "STAT1_K562",
    "NFE2L1_K562",
    "BACH1_K562",
    "RELA_K562",
    "LIN28B_K562",
    "HSF1_K562",
    "GATA2_K562",
    "NFYB_K562",
    "USF2_K562",
])

RBP_ALIASES = {
    "YB-1": "YBX1",
    "CSDA": "YBX3",
    "HNRNPDL": "HNRPDL",
    "BRUNOL4": "CELF4",
    "BRUNOL5": "CELF5",
    "BRUNOL6": "CELF6",
    "FUSIP1": "SRSF10",
}

FIELDS = [
    "analysis_type",
    "group",
    "class",
    "category",
    "target",
    "normalized_target",
    "cell_line",
    "run_id",
    "result_dir",
    "all_events",
    "up_events",
    "down_events",
    "status",
]


AUDIT_FIELDS = [
    "target",
    "cell_line",
    "run_id",
    "result_dir",
    "all_events",
    "up_events",
    "down_events",
    "status",
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--idiffir-dir", default="~/bigdata/Project1/iDiffIR")
    parser.add_argument("--pos-tf", default="Pos_TF.tsv")
    parser.add_argument("--neg-tf", default="Neg_TF.tsv")
    parser.add_argument("--pos-rbp", default="Pos_RBP.tsv")
    parser.add_argument("--neg-rbp", default="Neg_RBP.tsv")
    parser.add_argument("--meme", default="Homo_sapiens.meme")
    parser.add_argument("--tf-out", default="idiffir_tf_prediction_control_event_counts.tsv")
    parser.add_argument("--rbp-out", default="idiffir_rbp_prediction_control_event_counts.tsv")
    parser.add_argument("--combined-out", default="idiffir_prediction_control_event_counts_combined.tsv")
    parser.add_argument("--audit-out", default="idiffir_all_result_dirs_event_counts.tsv")
    return parser.parse_args()


def normalize_tf(name):
    return name.strip().upper()


def normalize_rbp(name):
    cleaned = name.strip()
    if not cleaned:
        return ""
    upper = cleaned.upper()
    return RBP_ALIASES.get(upper, upper)


def read_target_tsv(path, normalizer):
    targets = set()
    with io.open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
        header = handle.readline().rstrip("\n\r").split("\t")
        if "Target_ID" not in header:
            raise ValueError("Missing Target_ID column in {0}".format(path))
        target_index = header.index("Target_ID")
        for line in handle:
            parts = line.rstrip("\n\r").split("\t")
            if target_index >= len(parts):
                continue
            target = normalizer(parts[target_index])
            if target:
                targets.add(target)
    return targets


def read_rbp_meme_targets(path):
    targets = set()
    motif_re = re.compile(r"^MOTIF\s+\S+\s+(.+?)\s*$")
    with io.open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = motif_re.match(line.strip())
            if not match:
                continue
            annotation = match.group(1).strip()
            if not annotation:
                continue
            target = normalize_rbp(annotation.split()[0])
            if target:
                targets.add(target)
    return targets


def count_nonempty_lines(path):
    if not os.path.exists(path):
        return None
    count = 0
    with io.open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def parse_result_name(name):
    base = name

    for cell in CELL_LINES:
        suffix = "_result_" + cell
        if base.endswith(suffix):
            target = base[:-len(suffix)]
            return target, cell, target + "_" + cell

    if base.endswith("_result"):
        base = base[:-len("_result")]

    for cell in CELL_LINES:
        suffix = "_" + cell
        if base.endswith(suffix):
            target = base[:-len(suffix)]
            return target, cell, base

    return base, "", base


def count_result_dir(path):
    lists_dir = os.path.join(path, "lists")
    counts = {
        "all_events": count_nonempty_lines(os.path.join(lists_dir, "allDIRs.txt")),
        "up_events": count_nonempty_lines(os.path.join(lists_dir, "upDIRs.txt")),
        "down_events": count_nonempty_lines(os.path.join(lists_dir, "downDIRs.txt")),
    }
    missing = [key for key in ["all_events", "up_events", "down_events"] if counts[key] is None]
    status = "ok" if not missing else "missing_" + ",".join(missing)
    return counts, status


def classify_tf(run_id, norm_target, pos_tf, neg_tf):
    if run_id in TF_CONTROL_RUN_IDS:
        return "control", "random_tf_control", "TF"
    if norm_target in pos_tf:
        return "prediction", "positive", "TF"
    if norm_target in neg_tf:
        return "prediction", "negative", "TF"
    return "unlabeled", "not_tf_prediction_or_control", "unlabeled"


def classify_rbp(norm_target, pos_rbp, neg_rbp, rbp_control, rbp_meme):
    if norm_target in pos_rbp:
        return "prediction", "positive", "RBP"
    if norm_target in neg_rbp:
        return "prediction", "negative", "RBP"
    if norm_target in rbp_control:
        return "control", "meme_remaining_control", "RBP"
    if norm_target in rbp_meme:
        return "unlabeled", "meme_rbp_not_classified", "RBP"
    return "unlabeled", "not_in_rbp_meme", "unlabeled"


def make_row(analysis_type, group, klass, category, target, norm_target, cell_line, run_id, result_dir, counts, status):
    return {
        "analysis_type": analysis_type,
        "group": group,
        "class": klass,
        "category": category,
        "target": target,
        "normalized_target": norm_target,
        "cell_line": cell_line,
        "run_id": run_id,
        "result_dir": result_dir,
        "all_events": "" if counts["all_events"] is None else str(counts["all_events"]),
        "up_events": "" if counts["up_events"] is None else str(counts["up_events"]),
        "down_events": "" if counts["down_events"] is None else str(counts["down_events"]),
        "status": status,
    }


def write_tsv(path, fields, rows):
    parent = os.path.dirname(os.path.abspath(path))
    if not os.path.isdir(parent):
        os.makedirs(parent)
    with io.open(path, "w", encoding="utf-8") as handle:
        handle.write(u"\t".join(fields) + u"\n")
        for row in rows:
            handle.write(u"\t".join(row.get(field, "") for field in fields) + u"\n")


def main():
    args = parse_args()
    idiffir_dir = os.path.abspath(os.path.expanduser(args.idiffir_dir))

    pos_tf = read_target_tsv(os.path.expanduser(args.pos_tf), normalize_tf)
    neg_tf = read_target_tsv(os.path.expanduser(args.neg_tf), normalize_tf)
    pos_rbp = read_target_tsv(os.path.expanduser(args.pos_rbp), normalize_rbp)
    neg_rbp = read_target_tsv(os.path.expanduser(args.neg_rbp), normalize_rbp)
    rbp_meme = read_rbp_meme_targets(os.path.expanduser(args.meme))
    rbp_control = rbp_meme - (pos_rbp | neg_rbp)

    tf_rows = []
    rbp_rows = []
    audit_rows = []

    for name in sorted(os.listdir(idiffir_dir)):
        path = os.path.join(idiffir_dir, name)
        if not os.path.isdir(path) or "_result" not in name:
            continue

        target, cell_line, run_id = parse_result_name(name)
        counts, status = count_result_dir(path)

        audit_rows.append({
            "target": target,
            "cell_line": cell_line,
            "run_id": run_id,
            "result_dir": name,
            "all_events": "" if counts["all_events"] is None else str(counts["all_events"]),
            "up_events": "" if counts["up_events"] is None else str(counts["up_events"]),
            "down_events": "" if counts["down_events"] is None else str(counts["down_events"]),
            "status": status,
        })

        norm_tf = normalize_tf(target)
        tf_group, tf_class, tf_category = classify_tf(run_id, norm_tf, pos_tf, neg_tf)
        tf_rows.append(make_row("TF", tf_group, tf_class, tf_category, target, norm_tf, cell_line, run_id, name, counts, status))

        norm_rbp = normalize_rbp(target)
        rbp_group, rbp_class, rbp_category = classify_rbp(norm_rbp, pos_rbp, neg_rbp, rbp_control, rbp_meme)
        rbp_rows.append(make_row("RBP", rbp_group, rbp_class, rbp_category, target, norm_rbp, cell_line, run_id, name, counts, status))

    combined_rows = [
        row for row in tf_rows + rbp_rows
        if row["group"] in ("prediction", "control")
    ]

    write_tsv(os.path.expanduser(args.tf_out), FIELDS, tf_rows)
    write_tsv(os.path.expanduser(args.rbp_out), FIELDS, rbp_rows)
    write_tsv(os.path.expanduser(args.combined_out), FIELDS, combined_rows)
    write_tsv(os.path.expanduser(args.audit_out), AUDIT_FIELDS, audit_rows)

    print("[INFO] iDiffIR dir: {0}".format(idiffir_dir))
    print("[INFO] TF prediction targets: pos={0}, neg={1}".format(len(pos_tf), len(neg_tf)))
    print("[INFO] TF control run IDs: {0}".format(len(TF_CONTROL_RUN_IDS)))
    print("[INFO] RBP prediction targets: pos={0}, neg={1}".format(len(pos_rbp), len(neg_rbp)))
    print("[INFO] RBP MEME targets: {0}".format(len(rbp_meme)))
    print("[INFO] RBP MEME remaining controls: {0}".format(len(rbp_control)))
    print("[INFO] result dirs scanned: {0}".format(len(audit_rows)))
    print("[INFO] TF labeled prediction/control rows: {0}".format(len([r for r in tf_rows if r["group"] in ("prediction", "control")])))
    print("[INFO] RBP labeled prediction/control rows: {0}".format(len([r for r in rbp_rows if r["group"] in ("prediction", "control")])))
    print("[INFO] combined prediction/control rows: {0}".format(len(combined_rows)))
    print("[INFO] wrote: {0}".format(os.path.expanduser(args.tf_out)))
    print("[INFO] wrote: {0}".format(os.path.expanduser(args.rbp_out)))
    print("[INFO] wrote: {0}".format(os.path.expanduser(args.combined_out)))
    print("[INFO] wrote: {0}".format(os.path.expanduser(args.audit_out)))

    missing = [row for row in combined_rows if row["status"] != "ok"]
    if missing:
        print("[WARN] Combined labeled rows needing check:")
        for row in missing:
            print("  {0}\t{1}\t{2}\t{3}".format(row["analysis_type"], row["result_dir"], row["group"], row["status"]))


if __name__ == "__main__":
    main()
