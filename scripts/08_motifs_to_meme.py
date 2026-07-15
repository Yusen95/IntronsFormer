#!/usr/bin/env python3

import argparse
import csv
import sys


csv.field_size_limit(sys.maxsize)

ONEHOT = {
    "A": "1.00 0.00 0.00 0.00\n",
    "C": "0.00 1.00 0.00 0.00\n",
    "G": "0.00 0.00 1.00 0.00\n",
    "T": "0.00 0.00 0.00 1.00\n",
}


def create_meme_file(input_file, meme_output_file):
    with open(input_file, newline="") as infile, open(meme_output_file, "w") as outfile:
        reader = csv.reader(infile)
        next(reader)

        outfile.write("MEME version 4\n\n")
        outfile.write("ALPHABET= ACGT\n\n")
        outfile.write("strands: + -\n\n")
        outfile.write("Background letter frequencies (from uniform background):\n")
        outfile.write("A 0.25 C 0.25 G 0.25 T 0.25\n\n")

        motif_count = 0
        skipped = 0
        for row in reader:
            if len(row) < 3:
                continue

            motif = row[1].strip().upper()
            try:
                occurrences = int(row[2])
            except ValueError:
                occurrences = 1

            if not motif or any(base not in ONEHOT for base in motif):
                skipped += 1
                continue

            motif_count += 1
            outfile.write(f"MOTIF motif_{motif_count}\n")
            outfile.write(
                f"letter-probability matrix: alength= 4 w= {len(motif)} "
                f"nsites= {occurrences} E= 0.0\n"
            )
            for base in motif:
                outfile.write(ONEHOT[base])
            outfile.write("\n")

    print(f"Wrote {motif_count} motifs to {meme_output_file}")
    if skipped:
        print(f"Skipped {skipped} motifs containing non-ACGT characters")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="input_file", required=True, help="Motif CSV.")
    parser.add_argument("--out", dest="meme_output_file", required=True, help="Output .meme file.")
    args = parser.parse_args()
    create_meme_file(args.input_file, args.meme_output_file)
