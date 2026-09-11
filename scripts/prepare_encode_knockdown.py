#!/usr/bin/env python3

from __future__ import annotations

import csv
import argparse
import hashlib
import json
import re
import shlex
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


CELL_LINES = ["HepG2", "K562", "GM12878"]
ASSAY_TITLES = ["shRNA RNA-seq", "CRISPRi RNA-seq"]
ENCODE = "https://www.encodeproject.org"
OUT_DIR = Path("outputs") / "knockdown"
CACHE_DIR = OUT_DIR / "encode_api_cache"

INPUTS = {
    ("TF", "positive"): Path("tf_positive.csv"),
    ("TF", "negative"): Path("tf_negative.csv"),
    ("TF", "neutral"): Path("tf_neutral.csv"),
    ("RBP", "positive"): Path("rbp_positive.csv"),
    ("RBP", "negative"): Path("rbp_negative.csv"),
    ("RBP", "neutral"): Path("rbp_neutral.csv"),
}

ALIASES = {
    "BORCS8-MEF2B": "MEF2B",
    "BRUNOL4": "CELF4",
    "BRUNOL5": "CELF5",
    "BRUNOL6": "CELF6",
    "CSDA": "YBX3",
    "Fusip1": "SRSF10",
    "hnRNPK": "HNRNPK",
    "hnRNPLL": "HNRNPLL",
    "STAR-PAP": "TUT1",
    "YB-1": "YBX1",
}


def read_targets(path: Path) -> set[str]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if "tf_name" not in (reader.fieldnames or []):
            raise ValueError(f"Missing tf_name column in {path}")
        return {
            row["tf_name"].strip()
            for row in reader
            if row.get("tf_name") and row["tf_name"].strip()
        }


def input_targets() -> list[dict]:
    rows = []
    for (category, class_name), path in INPUTS.items():
        for original in sorted(read_targets(path), key=str.upper):
            rows.append({
                "Category": category,
                "Class": class_name,
                "Original_ID": original,
                "ENCODE_Target": ALIASES.get(original, original),
            })
    return rows


def cache_path(url: str) -> Path:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest}.json"


def get_json(url: str) -> dict:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = cache_path(url)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"@graph": [], "total": 0}
        raise

    try:
        path.write_text(json.dumps(data), encoding="utf-8")
    except OSError as exc:
        print(f"[WARN] Could not write ENCODE cache file {path}: {exc}")
    return data


def search_perturbation_experiments(target: str) -> list[dict]:
    experiments = []
    seen = set()
    for assay_title in ASSAY_TITLES:
        params = {
            "type": "Experiment",
            "assay_title": assay_title,
            "searchTerm": target,
            "status": "released",
            "format": "json",
            "limit": "all",
        }
        url = f"{ENCODE}/search/?{urllib.parse.urlencode(params)}"
        for exp in get_json(url).get("@graph", []):
            accession = exp.get("accession")
            if accession and accession not in seen:
                seen.add(accession)
                experiments.append(exp)
    return experiments


def assays_label() -> str:
    return ", ".join(ASSAY_TITLES)


def assay_rank(assay_title: str) -> int:
    try:
        return ASSAY_TITLES.index(assay_title)
    except ValueError:
        return len(ASSAY_TITLES)


def experiment_detail(experiment_id: str) -> dict:
    return get_json(f"{ENCODE}{experiment_id}?format=json&frame=embedded")


def experiment_link(exp: dict) -> str:
    return urllib.parse.urljoin(ENCODE, exp.get("@id", f"/experiments/{exp.get('accession', '')}/"))


def file_download_url(file_obj: dict) -> str:
    href = file_obj.get("href")
    if href:
        return urllib.parse.urljoin(ENCODE, href)
    acc = file_obj["accession"]
    return f"{ENCODE}/files/{acc}/@@download/{acc}.fastq.gz"


def cell_line_of(exp: dict) -> str | None:
    term = exp.get("biosample_ontology", {}).get("term_name")
    if term in CELL_LINES:
        return term
    summary = exp.get("biosample_summary", "") or ""
    for cell_line in CELL_LINES:
        if cell_line in summary:
            return cell_line
    return None


def target_matches(exp: dict, target: str, original: str) -> bool:
    text_parts = [
        exp.get("biosample_summary", ""),
        exp.get("description", ""),
        " ".join(exp.get("aliases", []) or []),
    ]
    text = " ".join(part for part in text_parts if part)
    variants = {target, original, ALIASES.get(original, original)}
    for variant in variants:
        pattern = rf"(?<![A-Za-z0-9]){re.escape(variant)}(?![A-Za-z0-9])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False


def fastq_pairs(exp: dict) -> list[dict]:
    files = [
        f for f in exp.get("files", [])
        if isinstance(f, dict)
        and f.get("status") == "released"
        and f.get("file_format") == "fastq"
        and f.get("output_type") == "reads"
        and f.get("paired_end") in {"1", "2"}
        and f.get("biological_replicates")
    ]

    by_rep: dict[int, dict[str, list[dict]]] = {}
    for file_obj in files:
        rep = int(file_obj["biological_replicates"][0])
        by_rep.setdefault(rep, {"1": [], "2": []})[file_obj["paired_end"]].append(file_obj)

    pairs = []
    for rep in sorted(by_rep):
        read1s = sorted(by_rep[rep]["1"], key=lambda f: (f.get("technical_replicates") or [""], f["accession"]))
        read2s = sorted(by_rep[rep]["2"], key=lambda f: (f.get("technical_replicates") or [""], f["accession"]))
        if not read1s or not read2s:
            continue

        read1_by_id = {f.get("@id"): f for f in read1s}
        read2_by_id = {f.get("@id"): f for f in read2s}
        chosen = None
        for read1 in read1s:
            paired = read1.get("paired_with")
            if paired in read2_by_id:
                chosen = (read1, read2_by_id[paired])
                break
        if chosen is None:
            for read2 in read2s:
                paired = read2.get("paired_with")
                if paired in read1_by_id:
                    chosen = (read1_by_id[paired], read2)
                    break
        if chosen is None:
            chosen = (read1s[0], read2s[0])

        pairs.append({
            "biological_replicate": rep,
            "read1": chosen[0],
            "read2": chosen[1],
        })

    return pairs


def control_candidates(exp: dict) -> list[dict]:
    candidates = []
    for control in exp.get("possible_controls", []) or []:
        if not isinstance(control, dict):
            continue
        control_id = control.get("@id")
        if not control_id:
            continue
        detail = experiment_detail(control_id)
        candidates.append(detail)
        time.sleep(0.03)
    return candidates


def choose_control(kd_exp: dict, kd_pairs: list[dict]) -> tuple[dict | None, list[dict]]:
    kd_cell = cell_line_of(kd_exp)
    best_control = None
    best_pairs: list[dict] = []

    for control in control_candidates(kd_exp):
        if control.get("status") != "released":
            continue
        if cell_line_of(control) != kd_cell:
            continue
        pairs = fastq_pairs(control)
        if len(pairs) > len(best_pairs):
            best_control = control
            best_pairs = pairs

    return best_control, best_pairs


def choose_experiment(row: dict) -> tuple[dict | None, dict | None, list[dict], list[dict], list[str]]:
    messages = []
    candidates = []
    for exp in search_perturbation_experiments(row["ENCODE_Target"]):
        if exp.get("assay_title") not in ASSAY_TITLES:
            continue
        cell_line = cell_line_of(exp)
        if cell_line not in CELL_LINES:
            continue
        detail = experiment_detail(exp["@id"])
        if not target_matches(detail, row["ENCODE_Target"], row["Original_ID"]):
            continue
        kd_pairs = fastq_pairs(detail)
        if len(kd_pairs) < 2:
            messages.append(f"{detail.get('accession', '')}: fewer than 2 paired biological replicates")
            continue
        control, control_pairs = choose_control(detail, kd_pairs)
        if not control or len(control_pairs) < 2:
            messages.append(f"{detail.get('accession', '')}: no matched control with at least 2 paired biological replicates")
            continue
        used_reps = min(len(kd_pairs), len(control_pairs))
        candidates.append((detail, control, kd_pairs[:used_reps], control_pairs[:used_reps]))
        time.sleep(0.05)

    if not candidates:
        return None, None, [], [], messages or [f"No released {assays_label()} in HepG2/K562/GM12878"]

    candidates.sort(
        key=lambda item: (
            len(item[2]),
            -assay_rank(item[0].get("assay_title", "")),
            item[0].get("date_released") or "",
            item[0].get("accession") or "",
        ),
        reverse=True,
    )
    kd_exp, control_exp, kd_pairs, control_pairs = candidates[0]
    return kd_exp, control_exp, kd_pairs, control_pairs, messages


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value)


def selected_rows_and_fastqs(target_rows: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    selected = []
    fastq_rows = []
    missing = []

    for row in target_rows:
        print(f"[INFO] Querying {row['Class']} {row['Category']} {row['Original_ID']} as {row['ENCODE_Target']}")
        kd_exp, control_exp, kd_pairs, control_pairs, messages = choose_experiment(row)
        if kd_exp is None or control_exp is None:
            for message in messages:
                missing.append({
            **row,
            "Assay": assays_label(),
            "Reason": message,
                })
            continue

        cell_line = cell_line_of(kd_exp) or ""
        run_id = f"{safe_name(row['ENCODE_Target'])}_{cell_line}"
        selected.append({
            **row,
            "Assay": kd_exp.get("assay_title", ""),
            "Cell_Line": cell_line,
            "Run_ID": run_id,
            "KD_Experiment": kd_exp.get("accession", ""),
            "Control_Experiment": control_exp.get("accession", ""),
            "Used_Replicate_Count": len(kd_pairs),
            "KD_Available_Replicate_Count": len(fastq_pairs(kd_exp)),
            "Control_Available_Replicate_Count": len(fastq_pairs(control_exp)),
            "KD_Description": kd_exp.get("description", ""),
            "Control_Description": control_exp.get("description", ""),
            "KD_Link": experiment_link(kd_exp),
            "Control_Link": experiment_link(control_exp),
        })

        base_dir = f"{row['Category']}_knockdown"
        local_subdir = f"{base_dir}/{run_id}"
        for condition, pairs in [("KO", kd_pairs), ("control", control_pairs)]:
            for index, pair in enumerate(pairs, start=1):
                for read_num, file_obj in [("1", pair["read1"]), ("2", pair["read2"])]:
                    if condition == "KO":
                        local_file = f"{run_id}_{index}_{read_num}.fastq.gz"
                    else:
                        local_file = f"{run_id}_control{index}_{read_num}.fastq.gz"
                    fastq_rows.append({
                        **row,
                        "Assay": kd_exp.get("assay_title", ""),
                        "Cell_Line": cell_line,
                        "Run_ID": run_id,
                        "Condition": condition,
                        "Replicate_Index": index,
                        "Biological_Replicate": pair["biological_replicate"],
                        "Read": read_num,
                        "Experiment": kd_exp.get("accession", "") if condition == "KO" else control_exp.get("accession", ""),
                        "File_Accession": file_obj.get("accession", ""),
                        "Download_URL": file_download_url(file_obj),
                        "Local_Subdir": local_subdir,
                        "Local_File": local_file,
                    })
    return selected, fastq_rows, missing


def write_tsv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_download_script(path: Path, fastq_rows: list[dict]) -> None:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        'BASE_DIR="${BASE_DIR:-$HOME/bigdata}"',
        "",
        'echo "[INFO] BASE_DIR=$BASE_DIR"',
        "",
    ]
    for row in fastq_rows:
        out_dir = f'$BASE_DIR/{row["Local_Subdir"]}'
        out_file = f'{out_dir}/{row["Local_File"]}'
        lines.extend([
            f'mkdir -p "{out_dir}"',
            f'out="{out_file}"',
            'tmp="${out}.part"',
            'if [ -s "$out" ] && gzip -t "$out" 2>/dev/null; then',
            '  echo "[SKIP] already exists: $out"',
            "else",
            f'  echo "[GET] {row["Run_ID"]} {row["Condition"]} rep{row["Replicate_Index"]} read{row["Read"]} {row["File_Accession"]}"',
            f'  wget -c -O "$tmp" {shlex.quote(row["Download_URL"])}',
            '  gzip -t "$tmp"',
            '  mv "$tmp" "$out"',
            "fi",
            "",
        ])

    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


def by_run_fastqs(fastq_rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in fastq_rows:
        grouped.setdefault((row["Category"], row["Run_ID"]), []).append(row)
    return grouped


def write_run_script(path: Path, selected: list[dict], fastq_rows: list[dict]) -> None:
    grouped_fastqs = by_run_fastqs(fastq_rows)
    selected_by_run = {(row["Category"], row["Run_ID"]): row for row in selected}
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        'BASE_DIR="${BASE_DIR:-$HOME/bigdata}"',
        'IRFINDER_REF="${IRFINDER_REF:-$BASE_DIR/refDir}"',
        'IDIFFIR_DIR="${IDIFFIR_DIR:-$BASE_DIR/Project1/iDiffIR}"',
        'GTF="${GTF:-Homo_sapiens.GRCh38.111.transcript_only.gtf}"',
        'IRFINDER_BIN="${IRFINDER_BIN:-IRFinder}"',
        'IRFINDER_ENV="${IRFINDER_ENV:-}"',
        'THREADS="${THREADS:-4}"',
        'MINMAP="${MINMAP:-5}"',
        "",
        'echo "[INFO] BASE_DIR=$BASE_DIR"',
        'echo "[INFO] IRFINDER_REF=$IRFINDER_REF"',
        'echo "[INFO] IDIFFIR_DIR=$IDIFFIR_DIR"',
        "",
    ]

    for key in sorted(grouped_fastqs):
        category, run_id = key
        rows = grouped_fastqs[key]
        category_dir = f"{category}_knockdown"
        selected_row = selected_by_run[key]
        reps = int(selected_row["Used_Replicate_Count"])
        lines.extend([
            '(',
            f'echo "[INFO] IRFinder {run_id}"',
            'if [ -n "$IRFINDER_ENV" ]; then',
            '  source ~/.bashrc',
            '  conda activate "$IRFINDER_ENV"',
            'fi',
            f'cd "$BASE_DIR/{category_dir}"',
        ])
        for index in range(1, reps + 1):
            kd_r1 = next(r for r in rows if r["Condition"] == "KO" and int(r["Replicate_Index"]) == index and r["Read"] == "1")
            kd_r2 = next(r for r in rows if r["Condition"] == "KO" and int(r["Replicate_Index"]) == index and r["Read"] == "2")
            ct_r1 = next(r for r in rows if r["Condition"] == "control" and int(r["Replicate_Index"]) == index and r["Read"] == "1")
            ct_r2 = next(r for r in rows if r["Condition"] == "control" and int(r["Replicate_Index"]) == index and r["Read"] == "2")
            for condition, out_dir, r1, r2 in [
                ("KO", run_id + "_KO_" + str(index), kd_r1, kd_r2),
                ("control", run_id + "_control_" + str(index), ct_r1, ct_r2),
            ]:
                done = f"{out_dir}/.irfinder_done"
                bam = f"{out_dir}/Unsorted.bam"
                lines.extend([
                    f'if [ -f {shlex.quote(done)} ] && [ -s {shlex.quote(bam)} ]; then',
                    f'  echo "[SKIP] IRFinder {run_id} {condition} rep{index}"',
                    "else",
                    f'  rm -rf {shlex.quote(out_dir)}',
                    f'  "$IRFINDER_BIN" -r "$IRFINDER_REF" -d {shlex.quote(out_dir)} '
                    f'{shlex.quote(run_id + "/" + r1["Local_File"])} {shlex.quote(run_id + "/" + r2["Local_File"])}',
                    f'  touch {shlex.quote(done)}',
                    "fi",
                ])
        lines.extend([
            "",
            f'echo "[INFO] iDiffIR {run_id}"',
            'cd "$IDIFFIR_DIR"',
            'source ~/.bashrc',
            'conda activate idiffir_py2',
            'mkdir -p KO Data',
        ])
        ko_bams = []
        control_bams = []
        for index in range(1, reps + 1):
            ko_bam = f"{run_id}_{index}.bam"
            control_bam = f"{run_id}_control{index}.bam"
            ko_bams.append(f"KO/{ko_bam}")
            control_bams.append(f"Data/{control_bam}")
            for condition, source_dir, dest_dir, bam_name in [
                ("KO", run_id + "_KO_" + str(index), "KO", ko_bam),
                ("control", run_id + "_control_" + str(index), "Data", control_bam),
            ]:
                bam_path = f"{dest_dir}/{bam_name}"
                done = f"{bam_path}.done"
                lines.extend([
                    f'if [ -f {shlex.quote(done)} ] && [ -s {shlex.quote(bam_path)} ]; then',
                    f'  echo "[SKIP] convertBam {run_id} {condition} rep{index}"',
                    "else",
                    f'  rm -f {shlex.quote(bam_path)} {shlex.quote(done)}',
                    f'  ./convertBam.sh ../../{category_dir}/{shlex.quote(source_dir)}/Unsorted.bam '
                    f'{dest_dir}/ {shlex.quote(bam_name)} -p "$THREADS" -m "$MINMAP" -v',
                    f'  touch {shlex.quote(done)}',
                    "fi",
                ])
        result_dir = run_id + "_result"
        result_done = f"{result_dir}/.idiffir_done"
        lines.extend([
            f'if [ -f {shlex.quote(result_done)} ]; then',
            f'  echo "[SKIP] iDiffIR {run_id}"',
            "else",
            f'  rm -rf {shlex.quote(result_dir)}',
            f'  idiffir.py -e IR -l KnockOut Wildtype -o {shlex.quote(result_dir)} "$GTF" '
            f'{":".join(ko_bams)} {":".join(control_bams)}',
            f'  mkdir -p {shlex.quote(result_dir)}',
            f'  touch {shlex.quote(result_done)}',
            "fi",
        ])
        lines.extend([")", ""])

    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


def main() -> None:
    global INPUTS, OUT_DIR, CACHE_DIR
    parser = argparse.ArgumentParser(description="Select ENCODE knockdown experiments from six candidate CSVs.")
    parser.add_argument("--input-dir", type=Path, required=True,
                        help="Directory containing tf/rbp_positive, negative and neutral CSVs, each with a tf_name column.")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()
    INPUTS = {key: args.input_dir / path.name for key, path in INPUTS.items()}
    OUT_DIR = args.out_dir
    CACHE_DIR = OUT_DIR / "encode_api_cache"
    missing = [str(path) for path in INPUTS.values() if not path.is_file()]
    if missing:
        parser.error("Missing candidate CSVs: " + ", ".join(missing))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    targets = input_targets()
    write_tsv(
        OUT_DIR / "knockdown_input_targets.tsv",
        targets,
        ["Class", "Category", "Original_ID", "ENCODE_Target"],
    )

    selected, fastq_rows, missing = selected_rows_and_fastqs(targets)
    write_tsv(
        OUT_DIR / "encode_knockdown_selected.tsv",
        selected,
        [
            "Class",
            "Category",
            "Original_ID",
            "ENCODE_Target",
            "Assay",
            "Cell_Line",
            "Run_ID",
            "KD_Experiment",
            "Control_Experiment",
            "Used_Replicate_Count",
            "KD_Available_Replicate_Count",
            "Control_Available_Replicate_Count",
            "KD_Description",
            "Control_Description",
            "KD_Link",
            "Control_Link",
        ],
    )
    write_tsv(
        OUT_DIR / "encode_knockdown_fastq_files.tsv",
        fastq_rows,
        [
            "Class",
            "Category",
            "Original_ID",
            "ENCODE_Target",
            "Assay",
            "Cell_Line",
            "Run_ID",
            "Condition",
            "Replicate_Index",
            "Biological_Replicate",
            "Read",
            "Experiment",
            "File_Accession",
            "Download_URL",
            "Local_Subdir",
            "Local_File",
        ],
    )
    write_tsv(
        OUT_DIR / "encode_knockdown_missing.tsv",
        missing,
        ["Class", "Category", "Original_ID", "ENCODE_Target", "Assay", "Reason"],
    )
    write_download_script(OUT_DIR / "download_encode_knockdown_fastq_HPCC.sh", fastq_rows)
    write_run_script(OUT_DIR / "run_all_knockdown_irfinder_idiffir.sh", selected, fastq_rows)

    print(f"[INFO] Input targets: {len(targets)}")
    print(f"[INFO] Selected knockdown experiments: {len(selected)}")
    print(f"[INFO] FASTQ files: {len(fastq_rows)}")
    print(f"[INFO] Missing rows: {len(missing)}")
    print(f"[INFO] Outputs written under {OUT_DIR}")


if __name__ == "__main__":
    main()
