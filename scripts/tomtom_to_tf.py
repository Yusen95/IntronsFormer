#!/usr/bin/env python3
"""
把 TomTom 结果 (tomtom.tsv) 的 Target_ID 翻译成 TF 名,输出去重、按显著性排序的 TF list。

motif->TF 映射从 CIS-BP 的 .meme 文件里取(行格式: MOTIF <ID> <TF名>)。
TF 名可能是:
  (TFAP2D)_(Mus_musculus)_(DBD_0.80)   -> 取括号里第一个 = TFAP2D
  SNAI2                                  -> 裸名 = SNAI2

用法:
  python tomtom_to_tf.py --meme CIS-BP/Homo_sapiens_2.0.meme \
      --tomtom full_ir_tomtom/tomtom.tsv --out tf_list_ir.csv --qthresh 0.05
"""

import argparse
import csv
import re
from pathlib import Path


def load_meme_map(meme_path):
    """建 motif_ID -> TF名 映射。"""
    mapping = {}
    with open(meme_path) as f:
        for line in f:
            if not line.startswith("MOTIF"):
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            motif_id = parts[1]
            raw_name = parts[2]
            # 形如 (TFAP2D)_(Mus_musculus)_(DBD_0.80) -> 取第一个括号内容
            m = re.match(r"\(([^)]+)\)", raw_name)
            tf = m.group(1) if m else raw_name
            mapping[motif_id] = tf
    return mapping


def parse_tomtom(tomtom_path, tf_map, qthresh):
    """
    返回 dict: TF名 -> 该 TF 出现过的最小 q-value(用于排序)。
    同时返回未能映射的 Target_ID 集合。
    """
    tf_best_q = {}
    unmapped = set()
    with open(tomtom_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            target = (row.get("Target_ID") or "").strip()
            if not target or target.startswith("#"):
                continue
            qval = row.get("q-value")
            if qval is None:
                continue
            try:
                q = float(qval)
            except (ValueError, TypeError):
                continue
            if q > qthresh:
                continue
            tf = tf_map.get(target)
            if tf is None:
                unmapped.add(target)
                continue
            if tf not in tf_best_q or q < tf_best_q[tf]:
                tf_best_q[tf] = q
    return tf_best_q, unmapped


# 低复杂度 consensus 的粗筛(单一碱基或双碱基重复),用于标注可疑
def flag_low_complexity_targets(tomtom_path):
    """返回那些 Query_consensus 是低复杂度串的 motif 对应的 TF 不在这里处理,
    这里只做提示:统计有多少行的 consensus 是单/双碱基主导。"""
    low = 0
    total = 0
    with open(tomtom_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            tid = (row.get("Target_ID") or "")
            if not tid or tid.startswith("#"):
                continue
            cons = row.get("Query_consensus") or ""
            if not cons:
                continue
            total += 1
            # 若 consensus 里只有 1-2 种碱基,视为低复杂度
            if len(set(cons)) <= 2:
                low += 1
    return low, total


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--meme", required=True, help="CIS-BP .meme 文件")
    p.add_argument("--tomtom", required=True, help="tomtom.tsv")
    p.add_argument("--out", required=True, help="输出 TF list csv")
    p.add_argument("--qthresh", type=float, default=0.05, help="q-value 阈值")
    args = p.parse_args()

    tf_map = load_meme_map(args.meme)
    print(f"meme 映射: {len(tf_map)} 个 motif ID")

    tf_best_q, unmapped = parse_tomtom(args.tomtom, tf_map, args.qthresh)
    tf_sorted = sorted(tf_best_q.items(), key=lambda x: x[1])  # q 升序

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="") as out:
        w = csv.writer(out)
        w.writerow(["TF_Name", "Best_qvalue"])
        for tf, q in tf_sorted:
            w.writerow([tf, f"{q:.4g}"])

    print(f"[+] {args.out}: {len(tf_sorted)} 个唯一 TF (q<={args.qthresh})")
    if unmapped:
        print(f"    {len(unmapped)} 个 Target_ID 在 meme 里找不到名字: "
              f"{sorted(unmapped)[:10]}{' ...' if len(unmapped) > 10 else ''}")

    low, total = flag_low_complexity_targets(args.tomtom)
    if total:
        print(f"    提示: {low}/{total} 行的 Query_consensus 是低复杂度串(<=2种碱基),"
              f"这些匹配的 TF 可能只是序列组成偏好,需谨慎解读")

    # 同时打印 TF 名清单(逗号分隔),方便直接复制
    print("\nTF list:")
    print(", ".join(tf for tf, _ in tf_sorted))


if __name__ == "__main__":
    main()
