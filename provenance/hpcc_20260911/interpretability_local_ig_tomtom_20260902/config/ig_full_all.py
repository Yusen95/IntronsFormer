#!/usr/bin/env python3
"""
全量 IG score(全部样本版)—— 旧线方法,全部样本,不做任何 prob 选样。

与 ig_full.py(top-10% 版)的区别:
  - 不做类别内 top-10% 选样,每个类别的【所有】样本都跑 IG
  - 仍按真实 label 分 pos(IR)/ neg(nonIR)两套输出
  - 跑一次 inference 把每条 prob 存进 ig_full_meta.csv(仅作记录/追溯,不参与选样)
  - 断点续跑:每条算完立即 append 写出,.done 记录已完成 orig_idx,重启自动跳过

方法学保持不变:
  - 在 x = norm2(g_emb + comb + pos) 上跑普通 IntegratedGradients(signal/位置烘焙在内)
  - baseline = zeros_like(x)
  - per-3mer -> per-base scatter-add (sum)
  - STEPS=50

注意:全量 ~224k 条,比 top-10% 版(~22k)大一个量级,跑很久。务必用断点续跑。

输出(pos / neg 各一套,逐行对应):
  ig_all_pos_sequence.csv / ig_all_pos_score.csv
  ig_all_neg_sequence.csv / ig_all_neg_score.csv
  ig_full_meta.csv  (orig_idx, label, prob —— 全部样本)
"""

import os
import csv
import math
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.amp import autocast
from performer_pytorch import SelfAttention
from captum.attr import IntegratedGradients

# ===================== 配置 =====================
OLD_CKPT       = "best_2conv_auc.pt"
K_MER          = 3
TOP_FRAC       = 0.10
STEPS          = 50
INTERNAL_BATCH = 10
INFER_BATCH    = 32
DEVICE         = "cuda" if torch.cuda.is_available() else "cpu"
SAVE_EVERY     = 50          # 每完成多少条 flush 一次进度文件

FILE_PATHS = [
    "Project1/Dataset/group_K562_raw.npz",
    "Project1/Dataset/group_GM12878_raw.npz",
    "Project1/Dataset/group_IMR-90_raw.npz",
    "Project1/Dataset/group_HepG2_raw.npz",
    "Project1/Dataset/group_H1_raw.npz",
    "Project1/Dataset/group_GM23248_raw.npz",
    "Project1/Dataset/group_HeLa-S3_raw.npz",
    "Project1/Dataset/group_SK-N-SH_raw.npz",
]

SELECTION_NPZ = "selection_all.npz"   # 全量分组(含 all_probs)
OUT = {
    "pos": {"seq": "ig_all_pos_sequence.csv", "score": "ig_all_pos_score.csv",
            "done": "ig_all_pos.done"},
    "neg": {"seq": "ig_all_neg_sequence.csv", "score": "ig_all_neg_score.csv",
            "done": "ig_all_neg.done"},
}
# ================================================


def set_random_seed(seed=42):
    import random
    random.seed(seed); np.random.seed(seed)
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)


def tokenize_kmer(arr, k):
    L = len(arr)
    if L < k:
        return torch.tensor([], dtype=torch.long)
    a = np.array(arr, copy=False)
    n_kmer = L - k + 1
    windows = np.lib.stride_tricks.as_strided(
        a, shape=(n_kmer, k), strides=(a.strides[0], a.strides[0]))
    weights = 4 ** np.arange(k - 1, -1, -1)
    tokens = (windows - 1).dot(weights) + 1
    return torch.tensor(tokens, dtype=torch.long)


def load_data_with_bedinfo(file_path):
    data = np.load(file_path, allow_pickle=True)
    y_array, bed_info_list, pairs = None, None, []
    for key in data.files:
        if key == 'y':
            y_array = data[key]
        elif key == 'bed_info':
            bed_info_list = data[key]
        elif key.startswith('arr_'):
            pairs.append((int(key.split('_')[1]), data[key]))
    pairs.sort(key=lambda x: x[0])
    return [arr for _, arr in pairs], y_array, bed_info_list


class GenomicDatasetBed(Dataset):
    def __init__(self, X_list, y_list, k_mer=3):
        self.X, self.y, self.k = X_list, y_list, k_mer
    def __len__(self): return len(self.X)
    def __getitem__(self, i):
        seq = tokenize_kmer(self.X[i][0] + 1, self.k)
        L = seq.size(0)
        s1 = torch.tensor(self.X[i][1][:L], dtype=torch.float32)
        s2 = torch.tensor(self.X[i][2][:L], dtype=torch.float32)
        s3 = torch.tensor(self.X[i][3][:L], dtype=torch.float32)
        lbl = torch.tensor(self.y[i], dtype=torch.float32)
        return seq, s1, s2, s3, lbl


# === 模型(2-conv,与 best_2conv_auc.pt 一致)===
class PositionalEncoding(nn.Module):
    def __init__(self, embed_dim):
        super().__init__(); self.embed_dim = embed_dim
    def forward(self, x):
        seq_len, d = x.size(1), self.embed_dim
        device = x.device
        pos = torch.arange(seq_len, device=device).unsqueeze(1).float()
        div = torch.exp(torch.arange(0, d, 2, device=device).float() * (-math.log(10000.0)/d))
        pe = torch.zeros(seq_len, d, device=device)
        pe[:, 0::2] = torch.sin(pos*div); pe[:, 1::2] = torch.cos(pos*div)
        return pe.unsqueeze(0)

class PerformerAttentionLayer(nn.Module):
    def __init__(self, embed_dim, num_heads, dropout_rate=0.1):
        super().__init__()
        self.self_attn = SelfAttention(dim=embed_dim, heads=num_heads, dropout=dropout_rate)
        self.norm = nn.LayerNorm(embed_dim); self.dropout = nn.Dropout(dropout_rate)
    def forward(self, x, src_mask=None):
        return self.norm(x + self.dropout(self.self_attn(x, mask=src_mask)))

class BERTLayer(nn.Module):
    def __init__(self, embed_dim, num_heads, dim_ff, dropout_rate=0.1):
        super().__init__()
        self.attn = PerformerAttentionLayer(embed_dim, num_heads, dropout_rate)
        self.ffn = nn.Sequential(nn.Linear(embed_dim, dim_ff), nn.ReLU(),
                                 nn.Dropout(dropout_rate), nn.Linear(dim_ff, embed_dim))
        self.norm = nn.LayerNorm(embed_dim)
    def forward(self, x, attention_mask=None):
        x = self.attn(x, src_mask=attention_mask)
        return self.norm(x + self.ffn(x))

class GenomicsBERTModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_layers, num_heads, output_dim, dropout_rate=0.1):
        super().__init__()
        self.embedding_genomics = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.signal1_proj = nn.Linear(1, embed_dim)
        self.signal2_proj = nn.Linear(1, embed_dim)
        self.signal3_proj = nn.Linear(1, embed_dim)
        self.pos_enc = PositionalEncoding(embed_dim)
        self.norm1 = nn.LayerNorm(embed_dim); self.norm2 = nn.LayerNorm(embed_dim)
        self.layers = nn.ModuleList([
            BERTLayer(embed_dim, num_heads, embed_dim*4, dropout_rate) for _ in range(num_layers)])
        self.conv_block = nn.Sequential(
            nn.Conv1d(embed_dim, embed_dim, kernel_size=13, padding=3, stride=2), nn.ReLU(),
            nn.Conv1d(embed_dim, embed_dim, kernel_size=7, padding=3, stride=1), nn.ReLU(),
            nn.MaxPool1d(kernel_size=2, stride=2))
        self.classifier = nn.Sequential(
            nn.Linear(embed_dim, embed_dim//2), nn.ReLU(),
            nn.Dropout(dropout_rate), nn.Linear(embed_dim//2, output_dim))
    def forward(self, genomics, s1, s2, s3, attention_mask=None):
        g_emb = self.embedding_genomics(genomics)
        p1 = self.signal1_proj(s1.unsqueeze(-1)); p2 = self.signal2_proj(s2.unsqueeze(-1))
        p3 = self.signal3_proj(s3.unsqueeze(-1))
        comb = self.norm1(p1+p2+p3)
        pos = self.pos_enc(g_emb+comb)
        x = self.norm2(g_emb+comb+pos)
        for layer in self.layers:
            x = layer(x, attention_mask)
        x = x.permute(0, 2, 1); x = self.conv_block(x); x = torch.max(x, dim=-1)[0]
        return self.classifier(x)


def collate_eval(batch):
    B = len(batch); maxL = max(b[0].shape[0] for b in batch)
    g = torch.zeros(B, maxL, dtype=torch.long)
    s1 = torch.zeros(B, maxL); s2 = torch.zeros(B, maxL); s3 = torch.zeros(B, maxL)
    m = torch.zeros(B, maxL, dtype=torch.bool); lab = []
    for i, (a, b1, b2, b3, l) in enumerate(batch):
        L = a.shape[0]; g[i,:L]=a; s1[i,:L]=b1; s2[i,:L]=b2; s3[i,:L]=b3; m[i,:L]=1; lab.append(l)
    return g, s1, s2, s3, m, torch.stack(lab)


def load_done(path):
    if not os.path.exists(path):
        return set()
    with open(path) as f:
        return set(int(x) for x in f.read().split() if x.strip())


def main():
    set_random_seed(42)
    print("device:", DEVICE)

    # ---- 加载全部样本(不分 split)----
    all_X, all_y = [], []
    for fp in FILE_PATHS:
        X, y, _ = load_data_with_bedinfo(fp)
        all_X.extend(X); all_y.extend(y)
    all_y = np.array(all_y).reshape(-1)
    N = len(all_X)
    print(f"全量样本: {N:,}  正例率={all_y.mean()*100:.1f}%")

    full_ds = GenomicDatasetBed(all_X, all_y, k_mer=K_MER)

    # ---- 加载模型 ----
    model = GenomicsBERTModel(vocab_size=4**K_MER+1, embed_dim=768, num_layers=6,
                              num_heads=6, output_dim=1, dropout_rate=0.1).to(DEVICE)
    sd = torch.load(OLD_CKPT, map_location=DEVICE)
    if isinstance(sd, dict) and "model_state_dict" in sd:
        sd = sd["model_state_dict"]
    miss, unexp = model.load_state_dict(sd, strict=False)
    if miss or unexp:
        print("[WARN] key mismatch -> missing:", miss, "| unexpected:", unexp)
    model.eval()

    # ---- 全量:不筛 prob,按真实 label 分 pos/neg 两组,各自全跑 ----
    #      仍跑一次 inference 把每条 prob 存盘(meta),供事后追溯/将来筛子集,
    #      但 IG 本身不依赖 prob、不做任何选样。
    if os.path.exists(SELECTION_NPZ):
        z = np.load(SELECTION_NPZ)
        pos_sel, neg_sel = z["pos_sel"], z["neg_sel"]
        print(f"载入已存分组: IR={len(pos_sel)}  nonIR={len(neg_sel)}")
    else:
        print("全量 inference 拿预测概率中(仅用于 meta 记录,不参与选样)...")
        loader = DataLoader(full_ds, batch_size=INFER_BATCH, shuffle=False,
                            collate_fn=collate_eval, num_workers=4, pin_memory=True)
        probs = []
        with torch.no_grad():
            for bi, (g, s1, s2, s3, m, _) in enumerate(loader):
                g, s1, s2, s3, m = [t.to(DEVICE) for t in (g, s1, s2, s3, m)]
                with autocast('cuda', dtype=torch.bfloat16):
                    out = model(g, s1, s2, s3, m)
                probs.append(torch.sigmoid(out.float()).squeeze(-1).cpu())
                if (bi+1) % 200 == 0:
                    print(f"  inference {bi+1}/{len(loader)} batches")
        all_probs = torch.cat(probs).numpy()
        labels = all_y

        # 全量:每个类别的所有样本都要(不按 prob 筛)
        pos_sel = np.where(labels == 1)[0]
        neg_sel = np.where(labels == 0)[0]
        np.savez(SELECTION_NPZ, pos_sel=pos_sel, neg_sel=neg_sel, all_probs=all_probs)

        # 单独存 prob meta(orig_idx, label, prob),供事后追溯
        with open("ig_full_meta.csv", "w", newline="") as mf:
            mw = csv.writer(mf)
            mw.writerow(["orig_idx", "label", "prob"])
            for i in range(N):
                mw.writerow([i, int(labels[i]), f"{all_probs[i]:.6f}"])
        print(f"全量分组完成: IR={len(pos_sel)}  nonIR={len(neg_sel)}  "
              f"total={len(pos_sel)+len(neg_sel)} (= 全部 {N} 条)")
        print("prob meta 已存 -> ig_full_meta.csv")

    # ---- IG ----
    def forward_func(x_in):
        out = x_in
        for layer in model.layers:
            out = layer(out)
        out = out.permute(0, 2, 1); out = model.conv_block(out); out = torch.max(out, dim=-1)[0]
        return model.classifier(out).squeeze(-1)

    ig = IntegratedGradients(forward_func)

    def run_one(seq, s1, s2, s3):
        g = seq.unsqueeze(0).to(DEVICE)
        s1 = s1.unsqueeze(0).to(DEVICE); s2 = s2.unsqueeze(0).to(DEVICE); s3 = s3.unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            g_emb = model.embedding_genomics(g)
            p1 = model.signal1_proj(s1.unsqueeze(-1)); p2 = model.signal2_proj(s2.unsqueeze(-1))
            p3 = model.signal3_proj(s3.unsqueeze(-1))
            comb = model.norm1(p1+p2+p3); pos = model.pos_enc(g_emb+comb)
            x = model.norm2(g_emb+comb+pos)
        at = ig.attribute(inputs=x, baselines=torch.zeros_like(x),
                          n_steps=STEPS, internal_batch_size=INTERNAL_BATCH)
        tok = at[0].sum(dim=-1).detach().float().cpu().numpy()
        L = tok.shape[0]
        base = np.zeros(L + K_MER - 1, dtype=np.float64)
        for off in range(K_MER):
            base[off:off+L] += tok
        return base

    # ---- 断点续跑:逐类别处理,append 写出 ----
    def process(sel, tag):
        o = OUT[tag]
        done = load_done(o["done"])
        todo = [int(i) for i in sel if int(i) not in done]
        print(f"[{tag}] 选中 {len(sel)},已完成 {len(done)},待跑 {len(todo)}")
        if not todo:
            print(f"[{tag}] 已全部完成,跳过"); return

        seq_fh = open(o["seq"], "a", newline="")
        score_fh = open(o["score"], "a", newline="")
        done_fh = open(o["done"], "a")
        seq_w, score_w = csv.writer(seq_fh), csv.writer(score_fh)

        try:
            for n, i in enumerate(todo):
                seq, s1, s2, s3, lbl = full_ds[i]
                base = run_one(seq, s1, s2, s3)
                raw = np.asarray(full_ds.X[i][0])
                if len(raw) != len(base):
                    raise ValueError(f"idx={i} bases={len(raw)} scores={len(base)} 不一致")
                seq_w.writerow([",".join(map(str, raw.tolist()))])
                score_w.writerow([",".join(f"{v:.6f}" for v in base)])
                done_fh.write(f"{i}\n")
                if (n+1) % SAVE_EVERY == 0:
                    seq_fh.flush(); score_fh.flush(); done_fh.flush()
                    print(f"  [{tag}] {n+1}/{len(todo)}")
        finally:
            seq_fh.close(); score_fh.close(); done_fh.close()
        print(f"[{tag}] 完成 -> {o['seq']} / {o['score']}")

    process(pos_sel, "pos")
    process(neg_sel, "neg")
    print("done.")


if __name__ == "__main__":
    main()
