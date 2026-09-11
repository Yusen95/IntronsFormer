#!/usr/bin/env python3
"""Single entry point for the existing IntronsFormer analysis scripts."""
import argparse
import csv
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from scripts.runtime_options import add_runtime_arguments, positive_int, nonnegative_int

ROOT = Path(__file__).resolve().parent
FIELDS = ("sample", "fpkm", "irfinder", "fasta", "chip", "dnase", "cpg_plus", "cpg_minus")
PLOTS = (
    "make_paper_ir_found_control_log2_permutation_figure.py",
    "plot_tf_rbp_all_prediction_only.py",
    "make_figure5_submission_current_data_pil.py",
    "figure5_tf_positive_plus_both.py",
)


def python_command(script, *args):
    return [sys.executable, str(ROOT / "scripts" / script), *map(str, args)]


def require_file(path):
    path = Path(path).resolve()
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Missing or empty input: {path}")
    return path


def read_datasets(args):
    if args.dataset_list:
        manifest = require_file(args.dataset_list)
        paths = [manifest.parent / line.strip() for line in manifest.read_text(encoding="utf-8-sig").splitlines()
                 if line.strip() and not line.lstrip().startswith("#")]
    else:
        paths = args.datasets
    if not paths:
        raise ValueError("No datasets supplied. The preprocessing example only creates BED files; full preprocessing creates datasets.txt.")
    paths = [require_file(path) for path in paths]
    if len(set(paths)) != len(paths):
        raise ValueError("Duplicate datasets would count samples twice; supply each file once.")
    return paths


def preprocess_plan(args, out):
    if args.example:
        rows = [{"sample": "K562", "fpkm": ROOT / "example/cufflinks/K562_genes.fpkm_tracking",
                 "irfinder": ROOT / "example/irfinder/K562_IRFinder-IR-dir.txt"}]
    else:
        manifest = require_file(args.manifest)
        with manifest.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if not set(FIELDS).issubset(reader.fieldnames or []):
                raise ValueError("Preprocessing TSV requires columns: " + ", ".join(FIELDS))
            rows = list(reader)
        for row in rows:
            for field in FIELDS[1:]:
                if not row[field] or not row[field].strip():
                    raise ValueError(f"Empty {field} for sample {row['sample']}")
                row[field] = manifest.parent / row[field].strip()
    if not rows:
        raise ValueError("Preprocessing manifest contains no samples.")
    seen, commands, expected, datasets, directories = set(), [], [], [], []
    for row in rows:
        sample = row["sample"] or ""
        if not re.fullmatch(r"[A-Za-z0-9_-]+", sample) or sample in seen:
            raise ValueError(f"Sample names must be unique letters/numbers/underscore/hyphen: {sample}")
        seen.add(sample)
        for field in FIELDS[1:3] if args.example else FIELDS[1:]:
            row[field] = require_file(row[field])
        work = out / sample
        directories.append(work)
        commands.append(python_command("01_filter_ir_events.py", row["fpkm"], row["irfinder"], work / "IR.bed", work / "nonIR.bed"))
        for label in ("IR", "nonIR"):
            bed = work / f"{label}.windows.bed"
            commands.append(python_command("02_filter_bed_windows.py", work / f"{label}.bed", bed))
            expected.append(bed)
            if not args.example:
                commands.append(python_command("03_build_feature_npz.py", "--bed", bed,
                    "--fasta", row["fasta"], "--chip", row["chip"], "--dnase", row["dnase"],
                    "--cpg-plus", row["cpg_plus"], "--cpg-minus", row["cpg_minus"],
                    "--output", work / f"{label}.features.npz"))
        if not args.example:
            dataset = work / "model_input.npz"
            commands.append(python_command("04_create_training_dataset.py", "--ir", work / "IR.features.npz",
                "--non-ir", work / "nonIR.features.npz", "--output", dataset, "--seed", args.seed))
            datasets.append(dataset)
            expected.append(dataset)
    return commands, expected, datasets, directories


def runtime_flags(args):
    flags = ["--device", args.device, "--precision", args.precision, "--num-workers", args.num_workers,
             "--seed", args.seed]
    if args.torch_threads is not None:
        flags += ["--torch-threads", args.torch_threads]
    return flags


def model_plan(args, out):
    datasets = read_datasets(args)
    if args.command == "train":
        commands = [python_command("05_train_intronsformer.py", "--datasets", *datasets,
            "--output-dir", out, "--epochs", args.epochs, "--batch-size", args.batch_size,
            "--accumulation-steps", args.accumulation_steps, *runtime_flags(args))]
        return commands, [out / "best_2conv_auc.pt", out / "best_2conv_loss.pt"], []
    checkpoint = require_file(args.checkpoint)
    if bool(args.tf_db) != bool(args.rbp_db):
        raise ValueError("Supply both --tf-db and --rbp-db to include the four Tomtom searches, or omit both for motifs only.")
    databases = []
    if args.tf_db:
        databases = [("tf", require_file(args.tf_db)), ("rbp", require_file(args.rbp_db))]
        if not shutil.which(args.tomtom):
            raise ValueError(f"Tomtom executable not found: {args.tomtom}")
    ig, motifs, tomtom = out / "ig", out / "motifs", out / "tomtom"
    commands = [python_command("06_integrated_gradients.py", "--datasets", *datasets,
        "--checkpoint", checkpoint, "--output-dir", ig, "--steps", args.steps,
        "--internal-batch-size", args.internal_batch_size, "--infer-batch-size", args.infer_batch_size,
        *runtime_flags(args))]
    expected = []
    for sign in ("pos", "neg"):
        commands.append(python_command("07_extract_ig_motifs.py", "--direction", sign,
            "--seq", ig / f"ig_all_{sign}_sequence.csv", "--score", ig / f"ig_all_{sign}_score.csv",
            "--out", motifs / f"{sign}.csv", "--min_len", args.min_len, "--count", args.count))
        commands.append(python_command("08_motifs_to_meme.py", "--in", motifs / f"{sign}.csv",
            "--out", motifs / f"{sign}.meme"))
        expected.append(motifs / f"{sign}.meme")
        for kind, database in databases:
            target = tomtom / f"{kind}_{sign}"
            commands.append([args.tomtom, "-oc", str(target), "-thresh", "0.05", str(motifs / f"{sign}.meme"), str(database)])
            commands.append(python_command("tomtom_to_tf.py", "--meme", database,
                "--tomtom", target / "tomtom.tsv", "--out", target / "matched_factors.csv", "--qthresh", "0.05"))
            expected.append(target / "matched_factors.csv")
    return commands, expected, [ig, motifs, tomtom]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("preprocess", help="IRFinder/FPKM -> BED -> features -> model inputs (or included BED example).")
    source = prep.add_mutually_exclusive_group(required=True)
    source.add_argument("--example", action="store_true")
    source.add_argument("--manifest", type=Path)
    prep.add_argument("--output-dir", type=Path, default=Path("outputs/pipeline_data"))
    prep.add_argument("--seed", type=int, default=1)
    for name in ("train", "interpret"):
        cmd = sub.add_parser(name, help="Train a model." if name == "train" else "IG -> motifs -> optional Tomtom.")
        inputs = cmd.add_mutually_exclusive_group(required=True)
        inputs.add_argument("--dataset-list", type=Path, help="datasets.txt from preprocessing, preserving row order.")
        inputs.add_argument("--datasets", type=Path, nargs="+")
        cmd.add_argument("--output-dir", type=Path, default=Path("outputs/pipeline_" + name))
        cmd.add_argument("--num-workers", type=nonnegative_int, default=0)
        cmd.add_argument("--seed", type=int, default=42)
        add_runtime_arguments(cmd)
        if name == "train":
            cmd.add_argument("--batch-size", type=positive_int, default=16)
            cmd.add_argument("--accumulation-steps", type=positive_int, default=4)
            cmd.add_argument("--epochs", type=positive_int, default=15)
        else:
            cmd.add_argument("--checkpoint", type=Path, required=True)
            cmd.add_argument("--infer-batch-size", type=positive_int, default=32)
            cmd.add_argument("--internal-batch-size", type=positive_int, default=10)
            cmd.add_argument("--steps", type=positive_int, default=50)
            cmd.add_argument("--min-len", type=positive_int, default=5)
            cmd.add_argument("--count", type=positive_int, default=3)
            cmd.add_argument("--tf-db", type=Path)
            cmd.add_argument("--rbp-db", type=Path)
            cmd.add_argument("--tomtom", default="tomtom")
    plot = sub.add_parser("plot", help="Re-create all four plots from the included tables.")
    plot.add_argument("--rebuild-tables", action="store_true", help="First regenerate event counts and occupancy ratios from archived summaries.")
    for cmd in (prep, sub.choices["train"], sub.choices["interpret"], plot):
        cmd.add_argument("--dry-run", action="store_true", help="Check input paths and print commands without running or writing files.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    out = args.output_dir.resolve() if hasattr(args, "output_dir") else None
    expected, datasets, directories = [], [], []
    if args.command == "preprocess":
        commands, expected, datasets, directories = preprocess_plan(args, out)
    elif args.command in ("train", "interpret"):
        commands, expected, directories = model_plan(args, out)
    else:
        commands = []
        if args.rebuild_tables:
            commands += [python_command(name) for name in (
                "summarize_encode_prediction_vs_control_event_counts.py",
                "summarize_prediction_pos_both_neg_with_control_event_counts.py",
                "cellline_stratified_prediction_control_results.py")]
            ratio = ROOT / "outputs/ir_nonir_ratio_analysis"
            flags = []
            for name in ("baseline_like_overlap_three_class_summary.tsv",
                         "baseline_like_overlap_three_class_summary_control.tsv", "control_rbp_only_summary.tsv"):
                flags += ["--summary", require_file(ratio / name)]
            commands.append(python_command("plot_ir_nonir_ratio_analysis.py", *flags, "--out_dir", ratio))
        commands += [python_command(name) for name in PLOTS]
    if args.dry_run:
        for command in commands:
            print(subprocess.list2cmdline(command))
        print("DRY RUN: no commands executed or outputs written.")
        return
    if out:
        if out.exists() and (not out.is_dir() or any(out.iterdir())):
            raise ValueError(f"Output directory must be new or empty: {out}. Choose --output-dir for a new run.")
        out.mkdir(parents=True, exist_ok=True)
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        (out / "run_commands.json").write_text(json.dumps(commands, indent=2), encoding="utf-8")
    for index, command in enumerate(commands, 1):
        print(f"[{index}/{len(commands)}] {subprocess.list2cmdline(command)}", flush=True)
        subprocess.run(command, cwd=ROOT, check=True)
    for path in expected:
        require_file(path)
    if datasets:
        (out / "datasets.txt").write_text("".join(path.relative_to(out).as_posix() + "\n" for path in datasets), encoding="utf-8")
    if out:
        (out / "PIPELINE_COMPLETE").write_text(args.command + "\n", encoding="utf-8")
    if args.command == "preprocess" and args.example:
        print("BED example complete. Full --manifest preprocessing is required to create datasets.txt and model inputs.")
    elif args.command == "interpret" and not args.tf_db:
        print("IG and motif conversion complete. Tomtom was omitted; supply both database options to include it.")
    else:
        print("Pipeline complete.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"[ERROR] {error}")
