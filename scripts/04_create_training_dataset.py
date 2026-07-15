#!/usr/bin/env python3

import argparse
from pathlib import Path

import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="Create one IR/nonIR dataset npz.")
    parser.add_argument("--ir", required=True, help="IR raw matrix npz.")
    parser.add_argument("--non-ir", required=True, help="nonIR raw matrix npz.")
    parser.add_argument("--output", required=True, help="Output dataset npz.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed.")
    return parser.parse_args()


def load_arrays_and_bed_info(npz_file):
    data = np.load(npz_file, allow_pickle=True)
    keys = sorted(
        [key for key in data.files if key != "bed_info"],
        key=lambda key: int(key.split("_")[1]),
    )
    arrays = [data[key] for key in keys]
    bed_info = data["bed_info"]
    return arrays, bed_info


def main():
    args = parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    ir_data_arrays, ir_bed_info = load_arrays_and_bed_info(args.ir)
    non_ir_data_arrays, non_ir_bed_info = load_arrays_and_bed_info(args.non_ir)

    num_ir_samples = len(ir_data_arrays)
    num_nonir_total = len(non_ir_data_arrays)

    num_nonir_samples = num_ir_samples * 4
    if num_nonir_samples > num_nonir_total:
        num_nonir_samples = num_nonir_total

    chosen_indices = np.random.choice(num_nonir_total, num_nonir_samples, replace=False)
    sampled_nonir_arrays = [non_ir_data_arrays[i] for i in chosen_indices]
    sampled_nonir_bed_info = [non_ir_bed_info[i] for i in chosen_indices]

    print(f"Number of IR data samples: {num_ir_samples}")
    print(f"Number of total non-IR data samples: {num_nonir_total}")
    print(f"Number of sampled non-IR data samples: {num_nonir_samples}")

    ir_labels = np.ones((num_ir_samples, 1), dtype=np.float32)
    non_ir_labels = np.zeros((num_nonir_samples, 1), dtype=np.float32)

    x_list = ir_data_arrays + sampled_nonir_arrays
    y_list = np.concatenate((ir_labels, non_ir_labels), axis=0)
    bed_info_list = list(ir_bed_info) + sampled_nonir_bed_info

    indices = np.arange(len(x_list))
    np.random.shuffle(indices)

    x_list = [x_list[i] for i in indices]
    y_list = y_list[indices]
    bed_info_list = [bed_info_list[i] for i in indices]

    print(f"X data length: {len(x_list)}")
    print(f"Y data shape: {y_list.shape}")

    npz_dict = {}
    for i in range(len(x_list)):
        npz_dict[f"arr_{i}"] = x_list[i]
    npz_dict["y"] = y_list
    npz_dict["bed_info"] = np.array(bed_info_list, dtype=object)

    output_dataset_file = Path(args.output)
    output_dataset_file.parent.mkdir(parents=True, exist_ok=True)
    np.savez(output_dataset_file, **npz_dict)
    print(f"Dataset saved to {output_dataset_file}")


if __name__ == "__main__":
    main()
