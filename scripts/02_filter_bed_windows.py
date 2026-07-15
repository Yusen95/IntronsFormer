import sys

import pandas as pd


def main(input_bed, output_bed):
    df = pd.read_csv(
        input_bed,
        sep="\t",
        header=None,
        names=["chrom", "start", "end", "name", "score", "strand"],
        dtype={"chrom": str, "name": str, "score": str, "strand": str},
        low_memory=False,
    )

    df["start"] = pd.to_numeric(df["start"], errors="coerce")
    df["end"] = pd.to_numeric(df["end"], errors="coerce")
    df = df.dropna(subset=["start", "end"]).copy()

    df["start"] = df["start"].astype(int)
    df["end"] = df["end"].astype(int)

    df = df[(df["end"] - df["start"]).abs() <= 10000].copy()

    df["start"] = df["start"] - 100
    df["end"] = df["end"] + 100

    df.to_csv(output_bed, sep="\t", header=False, index=False)

    print(f"New BED file saved to {output_bed}: {len(df)} rows")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python scripts/02_filter_bed_windows.py <input.bed> <output.bed>"
        )

    main(sys.argv[1], sys.argv[2])
