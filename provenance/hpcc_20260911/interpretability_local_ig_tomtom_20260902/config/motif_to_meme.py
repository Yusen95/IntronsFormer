#!/usr/bin/env python3
"""
把 motif_extract.py 输出的 motif 表转成 MEME v4 格式,供 TomTom 比对。

输入列(来自 motif_extract.py):Motif_ID, Motif_Seq, Occurrences, Mean_Region_IG, Positions
  - row[1] = Motif_Seq(ACGT 串)
  - row[2] = Occurrences -> 写进 nsites
"""

import csv
import sys
import argparse

csv.field_size_limit(sys.maxsize)  # 允许超长字段

ONEHOT = {
    "A": "1.00 0.00 0.00 0.00\n",
    "C": "0.00 1.00 0.00 0.00\n",
    "G": "0.00 0.00 1.00 0.00\n",
    "T": "0.00 0.00 0.00 1.00\n",
}


def create_meme_file(input_file, meme_output_file):
    with open(input_file, newline="") as infile, open(meme_output_file, "w") as outfile:
        reader = csv.reader(infile)
        next(reader)  # 跳过表头

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

            # 只保留纯 ACGT 的 motif;含其它字符的跳过并计数
            if not motif or any(b not in ONEHOT for b in motif):
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

    print(f"[+] 写出 {motif_count} 条 motif 到 {meme_output_file}")
    if skipped:
        print(f"    跳过 {skipped} 条含非 ACGT 字符的 motif")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="input_file", required=True, help="motif csv (来自 motif_extract.py)")
    p.add_argument("--out", dest="meme_output_file", required=True, help="输出 .meme 文件")
    args = p.parse_args()
    create_meme_file(args.input_file, args.meme_output_file)
