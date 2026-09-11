#!/usr/bin/env python3
"""
从 IG 碱基级 score 提取 motif。

适配新的输出格式:sequence 和 score 都是【逗号分隔、每行一条序列】
  - sequence 文件:每行 = 碱基编码 0..3,逗号分隔(由 csv.writer 自动加引号)
  - score 文件:   每行 = 碱基级 IG 分数,逗号分隔;第 i 个分数 ↔ 第 i 个碱基

direction:
  pos  -> 找正向高 IG 区域 (score > mean+std,只在正值上算阈值)   用于 IR 样本
  neg  -> 找负向高 IG 区域 (score < mean-std,只在负值上算阈值)   用于 nonIR 样本

输出:Motif_ID, Motif_Seq, Occurrences, Mean_Region_IG, Positions
"""

import argparse
import csv
import numpy as np
from collections import defaultdict

# 碱基编码 -> 核苷酸字母。!! 确认你的数据集编码与此一致 !!
# 若不是 A/C/G/T = 0/1/2/3,改这里;motif 会按此映射输出,直接喂 TomTom。
BASE_MAP = {0: "A", 1: "C", 2: "G", 3: "T"}


def _parse_float_row(row):
    """把一整行(可能被 csv 拆成多段、也可能含引号)重新合并后按逗号解析为 float 列表。"""
    raw = ",".join(row)
    return [float(v) for v in raw.split(",") if v != ""]


def _parse_base_row(row):
    """把一行碱基编码解析成核苷酸字符串,每个字符 = 一个碱基(与 score 一一对齐)。"""
    raw = ",".join(row)
    # 文件里碱基可能写成 '1.0' 这种浮点,先 float 再 round 成 int
    bases = [int(round(float(b))) for b in raw.split(",") if b != ""]
    return "".join(BASE_MAP[b] for b in bases)


def find_high_regions(scores, direction, min_len):
    """
    找高 IG 区域。direction='pos' 找正向,'neg' 找负向。
    返回 list[dict],每个含 start, end, ig_score(区域内 IG 均值)。
    """
    scores = np.squeeze(scores)

    if direction == "pos":
        filt = scores[scores > 0]
        if len(filt) == 0:
            return []
        thr = filt.mean() + filt.std()
        mask = scores > thr
    else:  # neg
        filt = scores[scores < 0]
        if len(filt) == 0:
            return []
        thr = filt.mean() - filt.std()
        mask = scores < thr

    regions = []
    start_idx = None
    for i, is_high in enumerate(mask):
        if is_high and start_idx is None:
            start_idx = i
        elif (not is_high) and (start_idx is not None):
            if i - start_idx >= min_len:
                region_scores = scores[start_idx:i]
                regions.append({
                    "start": start_idx,
                    "end": i,
                    "ig_score": float(region_scores.mean()),  # 用 mean,对不同长度公平
                })
            start_idx = None

    # 收尾:区域延伸到序列末尾
    if start_idx is not None and len(mask) - start_idx >= min_len:
        region_scores = scores[start_idx:len(mask)]
        regions.append({
            "start": start_idx,
            "end": len(mask),
            "ig_score": float(region_scores.mean()),
        })

    return regions


def extract_motifs(all_scores, sequences, direction, min_len):
    global_dict = defaultdict(lambda: {"count": 0, "positions": [], "ig_scores": []})
    for seq_index, seq_scores in enumerate(all_scores):
        regions = find_high_regions(seq_scores, direction, min_len)
        sequence = sequences[seq_index]
        intron_length = len(sequence)

        # 安全检查:score 长度应与碱基序列长度一致
        if len(np.squeeze(seq_scores)) != intron_length:
            raise ValueError(
                f"第 {seq_index} 行长度不一致: scores={len(np.squeeze(seq_scores))} "
                f"bases={intron_length} —— sequence 与 score 文件没对齐"
            )

        for region in regions:
            start, end = region["start"], region["end"]
            motif_seq = sequence[start:end]
            entry = global_dict[motif_seq]
            entry["count"] += 1
            entry["positions"].append({
                "seq_index": seq_index,
                "start": start,
                "end": end,
                "intron_length": intron_length,
            })
            entry["ig_scores"].append(region["ig_score"])
    return global_dict


def perform_motif_analysis(score_file, seq_file, output_file,
                           direction, min_motif_len, count_threshold):
    # 1) 读 score(逗号分隔浮点)
    all_scores = []
    with open(score_file, newline="") as f:
        for row in csv.reader(f):
            if not row:
                continue
            all_scores.append(_parse_float_row(row))

    # 2) 读 sequence(逗号分隔碱基 -> ACGT 串,字符与 score 对齐)
    sequences = []
    with open(seq_file, newline="") as f:
        for row in csv.reader(f):
            if not row:
                continue
            sequences.append(_parse_base_row(row))

    if len(all_scores) != len(sequences):
        raise ValueError(
            f"行数不一致: scores={len(all_scores)} sequences={len(sequences)}"
        )

    # 3) 提 motif
    global_dict = extract_motifs(all_scores, sequences, direction, min_motif_len)

    # 4) 写出
    with open(output_file, "w", newline="") as out:
        w = csv.writer(out)
        w.writerow(["Motif_ID", "Motif_Seq", "Occurrences", "Mean_Region_IG", "Positions"])
        for idx, (motif_seq, info) in enumerate(global_dict.items(), start=1):
            if info["count"] < count_threshold:
                continue
            mean_ig = float(np.mean(info["ig_scores"])) if info["ig_scores"] else 0.0
            pos_str = "; ".join(
                f"({o['start']}-{o['end']}, {o['intron_length']})"
                for o in info["positions"]
            )
            w.writerow([f"motif_{idx}", motif_seq, info["count"], mean_ig, pos_str])

    print(f"[+] motif 分析完成 -> {output_file}  (direction={direction})")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--direction", choices=["pos", "neg"], required=True,
                   help="pos=正向高IG(用于IR样本);neg=负向高IG(用于nonIR样本)")
    p.add_argument("--seq", required=True, help="sequence csv")
    p.add_argument("--score", required=True, help="score csv")
    p.add_argument("--out", required=True, help="输出 motif csv")
    p.add_argument("--min_len", type=int, default=5, help="最小 motif 长度")
    p.add_argument("--count", type=int, default=3, help="最小出现次数")
    args = p.parse_args()

    perform_motif_analysis(
        score_file=args.score,
        seq_file=args.seq,
        output_file=args.out,
        direction=args.direction,
        min_motif_len=args.min_len,
        count_threshold=args.count,
    )