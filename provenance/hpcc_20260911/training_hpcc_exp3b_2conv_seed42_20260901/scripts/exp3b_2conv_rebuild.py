import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
from performer_pytorch import SelfAttention
from transformers import get_cosine_schedule_with_warmup
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, f1_score
import random
import pandas as pd
import torch.nn.functional as F
from torch.amp import autocast
from torch.cuda.amp import GradScaler
import math
import time

# === SET RANDOM SEED ===
def set_random_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

set_random_seed(42)

# === FOCAL LOSS ===
def focal_loss(logits, targets, alpha=0.25, gamma=2.0, reduction='mean'):
    bce = F.binary_cross_entropy_with_logits(logits, targets, reduction='none')
    pt = torch.exp(-bce)
    factor = (1 - pt) ** gamma
    alpha_t = targets * alpha + (1 - targets) * (1 - alpha)
    loss = alpha_t * factor * bce
    if reduction == 'mean':
        return loss.mean()
    elif reduction == 'sum':
        return loss.sum()
    return loss

# === DATA PREPARATION ===
def tokenize_kmer(arr, k):
    L = len(arr)
    if L < k:
        return torch.tensor([], dtype=torch.long)
    a = np.array(arr, copy=False)
    n_kmer = L - k + 1
    windows = np.lib.stride_tricks.as_strided(
        a, shape=(n_kmer, k), strides=(a.strides[0], a.strides[0])
    )
    weights = 4 ** np.arange(k - 1, -1, -1)
    tokens = (windows - 1).dot(weights) + 1
    return torch.tensor(tokens, dtype=torch.long)

def load_data_with_bedinfo(file_path):
    data = np.load(file_path, allow_pickle=True)
    X_list, y_array, bed_info_list = [], None, None
    pairs = []
    for key in data.files:
        if key == 'y':
            y_array = data[key]
        elif key == 'bed_info':
            bed_info_list = data[key]
        elif key.startswith('arr_'):
            idx = int(key.split('_')[1])
            pairs.append((idx, data[key]))
    pairs.sort(key=lambda x: x[0])
    X_list = [arr for _, arr in pairs]
    return X_list, y_array, bed_info_list

class GenomicDataset(Dataset):
    def __init__(self, X_list, y_list, k_mer=1):
        self.X_list, self.y_list, self.k_mer = X_list, y_list, k_mer

    def __len__(self):
        return len(self.X_list)

    def __getitem__(self, idx):
        seq = tokenize_kmer(self.X_list[idx][0] + 1, self.k_mer)
        L   = seq.size(0)
        s1  = torch.tensor(self.X_list[idx][1][:L], dtype=torch.float32)
        s2  = torch.tensor(self.X_list[idx][2][:L], dtype=torch.float32)
        s3  = torch.tensor(self.X_list[idx][3][:L], dtype=torch.float32)
        lbl = torch.tensor(self.y_list[idx], dtype=torch.float32)
        return seq, s1, s2, s3, lbl

def collate_fn(batch):
    batch.sort(key=lambda x: x[0].shape[0], reverse=True)
    B = len(batch); max_len = batch[0][0].shape[0]
    pad_g  = torch.zeros(B, max_len, dtype=torch.long)
    pad_s1 = torch.zeros(B, max_len)
    pad_s2 = torch.zeros(B, max_len)
    pad_s3 = torch.zeros(B, max_len)
    mask   = torch.zeros(B, max_len, dtype=torch.bool)
    labels = []
    for i, (g, s1, s2, s3, lbl) in enumerate(batch):
        L = g.shape[0]
        pad_g[i,:L]  = g
        pad_s1[i,:L] = s1
        pad_s2[i,:L] = s2
        pad_s3[i,:L] = s3
        mask[i,:L]   = 1
        labels.append(lbl)
    return {
        'genomics': pad_g,
        'signal1':  pad_s1,
        'signal2':  pad_s2,
        'signal3':  pad_s3,
        'attention_mask': mask,
        'labels': torch.stack(labels)
    }

# === MODEL COMPONENTS ===
class PositionalEncoding(nn.Module):
    def __init__(self, embed_dim):
        super().__init__()
        self.embed_dim = embed_dim
    def forward(self, x):
        seq_len, d = x.size(1), self.embed_dim
        device = x.device
        pos  = torch.arange(seq_len, device=device).unsqueeze(1).float()
        div  = torch.exp(torch.arange(0, d, 2, device=device).float() * (-math.log(10000.0)/d))
        pe   = torch.zeros(seq_len, d, device=device)
        pe[:,0::2] = torch.sin(pos * div)
        pe[:,1::2] = torch.cos(pos * div)
        return pe.unsqueeze(0)

class PerformerAttentionLayer(nn.Module):
    def __init__(self, embed_dim, num_heads, dropout_rate=0.1):
        super().__init__()
        self.self_attn = SelfAttention(dim=embed_dim, heads=num_heads, dropout=dropout_rate)
        self.norm      = nn.LayerNorm(embed_dim)
        self.dropout   = nn.Dropout(dropout_rate)
    def forward(self, x, src_mask=None):
        out = self.self_attn(x, mask=src_mask)
        return self.norm(x + self.dropout(out))

class BERTLayer(nn.Module):
    def __init__(self, embed_dim, num_heads, dim_ff, dropout_rate=0.1):
        super().__init__()
        self.attn = PerformerAttentionLayer(embed_dim, num_heads, dropout_rate)
        self.ffn  = nn.Sequential(
            nn.Linear(embed_dim, dim_ff),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(dim_ff, embed_dim)
        )
        self.norm = nn.LayerNorm(embed_dim)
    def forward(self, x, attention_mask=None):
        x = self.attn(x, src_mask=attention_mask)
        return self.norm(x + self.ffn(x))

class GenomicsBERTModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_layers, num_heads, output_dim, dropout_rate=0.1):
        super().__init__()
        self.embedding_genomics = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.signal1_proj       = nn.Linear(1, embed_dim)
        self.signal2_proj       = nn.Linear(1, embed_dim)
        self.signal3_proj       = nn.Linear(1, embed_dim)
        self.pos_enc = PositionalEncoding(embed_dim)
        self.norm1   = nn.LayerNorm(embed_dim)
        self.norm2   = nn.LayerNorm(embed_dim)
        self.layers = nn.ModuleList([
            BERTLayer(embed_dim, num_heads, embed_dim*4, dropout_rate)
            for _ in range(num_layers)
        ])
        self.conv_block = nn.Sequential(
            nn.Conv1d(embed_dim, embed_dim, kernel_size=13, padding=3, stride=2),
            nn.ReLU(),
            nn.Conv1d(embed_dim, embed_dim, kernel_size=7, padding=3, stride=1),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2, stride=2)
        )
        self.classifier = nn.Sequential(
            nn.Linear(embed_dim, embed_dim//2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(embed_dim//2, output_dim)
        )

    def forward(self, genomics, s1, s2, s3, attention_mask=None):
        g_emb = self.embedding_genomics(genomics)
        p1    = self.signal1_proj(s1.unsqueeze(-1))
        p2    = self.signal2_proj(s2.unsqueeze(-1))
        p3    = self.signal3_proj(s3.unsqueeze(-1))
        comb  = self.norm1(p1 + p2 + p3)
        pos   = self.pos_enc(g_emb + comb)
        x     = self.norm2(g_emb + comb + pos)
        for layer in self.layers:
            x = layer(x, attention_mask)
        x = x.permute(0, 2, 1)
        x = self.conv_block(x)
        x = torch.max(x, dim=-1)[0]
        return self.classifier(x)

# === EVALUATION ===
def evaluate(model, loader, device, alpha=0.25, gamma=2.0):
    model.eval()
    total_loss, all_logits, all_labels = 0.0, [], []
    with torch.no_grad():
        for batch in loader:
            g    = batch['genomics'].to(device)
            s1   = batch['signal1'].to(device)
            s2   = batch['signal2'].to(device)
            s3   = batch['signal3'].to(device)
            mask = batch['attention_mask'].to(device)
            lbl  = batch['labels'].to(device)
            with autocast('cuda', dtype=torch.bfloat16):
                out  = model(g, s1, s2, s3, mask)
                loss = focal_loss(out.view(-1), lbl.view(-1), alpha, gamma)
            total_loss += loss.item()
            all_logits.append(out.cpu())
            all_labels.append(lbl.cpu())

    logits = torch.cat(all_logits).float()
    labels = torch.cat(all_labels).float()
    preds  = torch.sigmoid(logits).numpy().flatten()
    lab_np = labels.flatten().numpy()
    preds  = np.nan_to_num(preds, nan=0.5)
    roc    = roc_auc_score(lab_np, preds)
    p, r, _= precision_recall_curve(lab_np, preds)
    pr     = auc(r, p)

    best_f1, best_t = 0.0, 0.5
    for t in np.arange(0.2, 0.8, 0.02):
        f = f1_score(lab_np, (preds>t).astype(int), zero_division=0)
        if f > best_f1: best_f1, best_t = f, t

    return total_loss/len(loader), roc, pr, best_f1, best_t

# === MAIN TRAINING LOOP ===
def main():
    k_mer = 3
    file_paths = [
        "/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/outputs/model_inputs/group_K562_model_input_seed1.npz",
        "/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/outputs/model_inputs/group_GM12878_model_input_seed1.npz",
        "/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/outputs/model_inputs/group_IMR-90_model_input_seed1.npz",
        "/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/outputs/model_inputs/group_HepG2_model_input_seed1.npz",
        "/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/outputs/model_inputs/group_H1_model_input_seed1.npz",
        "/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/outputs/model_inputs/group_GM23248_model_input_seed1.npz",
        "/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/outputs/model_inputs/group_HeLa-S3_model_input_seed1.npz",
        "/rhome/yzhan677/bigdata/IntronsFormer_full_rebuild_20260830/outputs/model_inputs/group_SK-N-SH_model_input_seed1.npz"
    ]
    all_X, all_y, bed = [], [], []

    print("Loading data...")
    for fp in file_paths:
        X, y, info = load_data_with_bedinfo(fp)
        all_X.extend(X); all_y.extend(y); bed.extend(info)
    all_y = np.array(all_y).reshape(-1, 1)

    groups = [f"chr{b[0]}_{b[1]}_{b[2]}_{b[3]}" for b in bed]
    df     = pd.DataFrame({'group': groups, 'index': range(len(all_X)), 'label': all_y.flatten()})
    print(f"  Samples: {len(df):,}  Positive: {df.label.mean()*100:.1f}%")

    uniq   = df['group'].unique()
    random.shuffle(uniq)
    splits = np.split(uniq, [int(0.7*len(uniq)), int(0.85*len(uniq))])
    split_map = {g:'train' for g in splits[0]}
    split_map.update({g:'val'  for g in splits[1]})
    split_map.update({g:'test' for g in splits[2]})
    df['split'] = df['group'].map(split_map)

    train_ds = GenomicDataset([all_X[i] for i in df[df.split=='train'].index],
                              all_y[df.split=='train'], k_mer=k_mer)
    val_ds   = GenomicDataset([all_X[i] for i in df[df.split=='val'].index],
                              all_y[df.split=='val'], k_mer=k_mer)
    test_ds  = GenomicDataset([all_X[i] for i in df[df.split=='test'].index],
                              all_y[df.split=='test'], k_mer=k_mer)

    train_loader = DataLoader(train_ds, batch_size=16, shuffle=True,  collate_fn=collate_fn, num_workers=4, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=16, shuffle=False, collate_fn=collate_fn, num_workers=4, pin_memory=True)
    test_loader  = DataLoader(test_ds,  batch_size=16, shuffle=False, collate_fn=collate_fn, num_workers=4, pin_memory=True)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    num_epochs      = 15
    steps_per_epoch = len(train_loader)
    total_steps     = num_epochs * steps_per_epoch
    warmup_steps    = int(0.1 * total_steps)

    vocab_size = 4**k_mer + 1
    model = GenomicsBERTModel(
        vocab_size, embed_dim=768, num_layers=6, num_heads=6, output_dim=1, dropout_rate=0.1
    ).to(device)

    n_params = sum(p.numel() for p in model.parameters())
    print(f"Params: {n_params/1e6:.1f}M")
    print(f"改动: BF16 + 两层conv (原始1层+新增kernel=7层)")

    optimizer   = torch.optim.AdamW(model.parameters(), lr=1e-5, weight_decay=1e-3)
    scheduler   = get_cosine_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )
    scaler      = GradScaler()

    best_val = float('inf')
    best_auc = 0.0
    accumulation_steps = 4

    for epoch in range(num_epochs):
        t0 = time.time()
        model.train()
        epoch_loss = 0.0
        optimizer.zero_grad()

        for i, batch in enumerate(train_loader):
            g    = batch['genomics'].to(device)
            s1   = batch['signal1'].to(device)
            s2   = batch['signal2'].to(device)
            s3   = batch['signal3'].to(device)
            mask = batch['attention_mask'].to(device)
            lbl  = batch['labels'].to(device)

            with autocast('cuda', dtype=torch.bfloat16):
                out  = model(g, s1, s2, s3, mask)
                loss = focal_loss(out.view(-1), lbl.view(-1)) / accumulation_steps

            scaler.scale(loss).backward()

            if (i + 1) % accumulation_steps == 0:
                scaler.unscale_(optimizer)
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                scaler.step(optimizer)
                scaler.update()
                scheduler.step()
                optimizer.zero_grad()

            epoch_loss += loss.item() * accumulation_steps

        ep_sec = time.time() - t0
        val_loss, val_auc, val_pr, val_f1, val_t = evaluate(model, val_loader, device)
        lr_now = optimizer.param_groups[0]['lr']
        eta = (num_epochs - epoch - 1) * ep_sec / 60

        print(f"Epoch {epoch+1:02d}/{num_epochs}  lr={lr_now:.2e}  "
              f"Train={epoch_loss/len(train_loader):.4f}  "
              f"Val={val_loss:.4f}  AUC={val_auc:.4f}  PR={val_pr:.4f}  F1={val_f1:.4f}")
        print(f"  ⏱ {ep_sec:.0f}s  ETA≈{eta:.0f}min")

        if val_loss < best_val:
            best_val = val_loss
            torch.save(model.state_dict(), 'best_2conv_loss.pt')
            print(f"  → Saved (best loss)")
        if val_auc > best_auc:
            best_auc = val_auc
            best_auc_t = val_t
            torch.save(model.state_dict(), 'best_2conv_auc.pt')
            print(f"  → Saved (best AUC={val_auc:.4f})")

    print("\n" + "="*60)
    print("FINAL TEST")
    print("="*60)

    for tag, ckpt in [('BestLoss', 'best_2conv_loss.pt'), ('BestAUC', 'best_2conv_auc.pt')]:
        model.load_state_dict(torch.load(ckpt, map_location=device))
        tl, tauc, tpr, tf1, tt = evaluate(model, test_loader, device)
        print(f"\n[{tag}]  AUC={tauc:.4f}  PR={tpr:.4f}  F1={tf1:.4f}")

if __name__ == "__main__":
    main()
