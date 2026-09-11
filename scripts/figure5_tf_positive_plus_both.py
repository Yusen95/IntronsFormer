import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from pathlib import Path

# ----------------------------
# Load and prepare data
# ----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
kd_path = PROJECT_ROOT / 'outputs/figure5_original_style/knockdown_results_download_snapshot.csv'
kd = pd.read_csv(kd_path)

df = kd.rename(columns={
    'Regulator': 'regulator',
    'Regulator_Type': 'type',
    'Candidate_Group': 'group',
    'Cell_Line': 'cell_line',
    'iDiffIR_Down': 'downregulated_ir',
    'iDiffIR_Up': 'upregulated_ir',
}).copy()

def map_group(x):
    s = str(x).strip().lower()
    if s.startswith('positive'): return 'P'
    if s.startswith('negative'): return 'N'
    if s.startswith('both'): return 'B'
    if s.startswith('uncat') or s == 'nan': return 'U'
    return str(x).strip().upper()[:1]

df['group'] = df['group'].apply(map_group)
df['type'] = df['type'].astype(str).str.upper()
df['downregulated_ir'] = pd.to_numeric(df['downregulated_ir'], errors='coerce').fillna(0).astype(int)
df['upregulated_ir'] = pd.to_numeric(df['upregulated_ir'], errors='coerce').fillna(0).astype(int)
df['total'] = df['downregulated_ir'].abs() + df['upregulated_ir'].abs()

tf = df[df['type'] == 'TF'].copy()
tf_positive = tf[tf['group'] == 'P'].sort_values('total', ascending=False).copy()
tf_both_top = tf[tf['group'] == 'B'].sort_values('total', ascending=False).head(6).copy()
tf_top = pd.concat([tf_positive, tf_both_top], ignore_index=True)
rbp_top = df[
    (df['type'] == 'RBP')
    & (df['cell_line'].astype(str).str.upper() == 'K562')
    & (df['group'].isin(['P', 'B', 'N']))
].copy()
rbp_top['_sort_value'] = rbp_top['downregulated_ir'] - rbp_top['upregulated_ir']

# ----------------------------
# Style
# ----------------------------
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.linewidth': 0.9,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 8.5,
    'legend.fontsize': 9,
    'legend.frameon': False,
    'figure.dpi': 180,
    'savefig.dpi': 450,
    'savefig.bbox': 'tight',
    'savefig.facecolor': 'white',
})

GROUP_COLORS = {
    'P': '#4C78A8',  # blue
    'B': '#EBC34C',  # yellow-gold
    'N': '#E45756',  # red
    'U': '#9E9E9E',  # gray
}
GROUP_NAMES = {
    'P': 'P = Positive-only',
    'B': 'B = Both',
    'N': 'N = Negative-only',
    'U': 'U = Uncategorized',
}

out_dir = PROJECT_ROOT / 'outputs' / 'figure5_tf_positive_plus_both'
out_dir.mkdir(parents=True, exist_ok=True)


def draw_panel(ax, sub, title, panel_label, group_blocks=None, section_labels=None, show_cell_line=True):
    if group_blocks:
        sub = sub.assign(_group_order=sub['group'].map(group_blocks).fillna(-1))
        sort_col = '_sort_value' if '_sort_value' in sub.columns else 'total'
        sub = sub.sort_values(['_group_order', sort_col], ascending=[True, True]).copy()
    else:
        sub = sub.sort_values('total', ascending=True).copy()
    y = np.arange(len(sub))
    labels = []
    for _, r in sub.iterrows():
        cell = r.get('cell_line', '')
        if show_cell_line and pd.notna(cell) and str(cell).strip() and str(cell).strip().lower() != 'nan':
            name = f"{r['regulator']} ({cell})"
        else:
            name = str(r['regulator'])
        labels.append(f"{name} [{r['group']}]")

    # Draw bars: same group color, direction encoded by hatch pattern
    for yi, (_, r) in enumerate(sub.iterrows()):
        c = GROUP_COLORS.get(r['group'], '#9E9E9E')
        # Down-regulated: plain fill
        ax.barh(
            yi, -r['downregulated_ir'], color=c, edgecolor='black',
            linewidth=0.8, zorder=2
        )
        # Up-regulated: same color + hatch
        ax.barh(
            yi, r['upregulated_ir'], color=c, edgecolor='black',
            linewidth=0.8, hatch='///', zorder=2
        )

    ax.axvline(0, color='black', lw=0.9, zorder=1)
    if group_blocks:
        groups = sub['group'].tolist()
        for idx in range(1, len(groups)):
            if groups[idx] != groups[idx - 1]:
                ax.axhline(idx - 0.5, color='black', lw=0.8, alpha=0.45, zorder=1)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)

    max_val = max(sub['downregulated_ir'].max(), sub['upregulated_ir'].max(), 1)
    lim = np.ceil(max_val / 100.0) * 100
    ax.set_xlim(-lim * 1.08, lim * 1.08)

    if group_blocks and section_labels:
        groups = sub['group'].tolist()
        start = 0
        for idx in range(1, len(groups) + 1):
            if idx == len(groups) or groups[idx] != groups[start]:
                group = groups[start]
                if group in section_labels:
                    ax.text(
                        lim * 0.98, (start + idx - 1) / 2, section_labels[group],
                        color=GROUP_COLORS.get(group, 'black'), fontsize=9,
                        fontweight='bold', ha='right', va='center',
                        bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': 0.85, 'pad': 2.0},
                        zorder=4
                    )
                start = idx

    ticks = ax.get_xticks()
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(int(abs(t))) for t in ticks])

    ax.set_xlabel('Number of differential IR events (left: down-regulated; right: up-regulated)')
    if title:
        ax.set_title(title, pad=10)
    ax.text(-0.10, 1.06, panel_label, transform=ax.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='left', clip_on=False)


def add_side_legends(fig, present_groups):
    # Candidate group legend on the left bottom
    group_handles = [
        Patch(facecolor=GROUP_COLORS[g], edgecolor='none', label=GROUP_NAMES[g])
        for g in ['P', 'B', 'N', 'U'] if g in present_groups
    ]
    # Direction legend on the right bottom
    direction_handles = [
        Patch(facecolor='white', edgecolor='black', linewidth=1.0, label='Down-regulated IR events'),
        Patch(facecolor='white', edgecolor='black', linewidth=1.0, hatch='///', label='Up-regulated IR events'),
    ]

    leg1 = fig.legend(
        handles=group_handles, title='Candidate group', frameon=False,
        loc='lower left', bbox_to_anchor=(0.12, 0.01), ncol=2,
        handlelength=2.0, columnspacing=1.6
    )
    leg2 = fig.legend(
        handles=direction_handles, title='Direction', frameon=False,
        loc='lower right', bbox_to_anchor=(0.88, 0.01), ncol=1,
        handlelength=2.0, columnspacing=1.2
    )
    fig.add_artist(leg1)
    fig.add_artist(leg2)


def save_single_panel(
    sub, title, panel_label, fname, height, group_blocks=None,
    section_labels=None, show_cell_line=True
):
    fig, ax = plt.subplots(figsize=(10.6, height))
    draw_panel(
        ax, sub, title, panel_label, group_blocks=group_blocks,
        section_labels=section_labels, show_cell_line=show_cell_line
    )
    add_side_legends(fig, set(sub['group']))
    fig.subplots_adjust(left=0.20, right=0.98, top=0.90, bottom=0.20)
    fig.savefig(out_dir / f'{fname}.pdf')
    fig.savefig(out_dir / f'{fname}.png')
    plt.close(fig)


# Separate panels
tf_group_blocks = {'B': 0, 'P': 1}
rbp_group_blocks = {'N': 0, 'B': 1, 'P': 2}
save_single_panel(
    tf_top,
    '',
    'a',
    'Figure5A_TF_knockdown_all_positive_top_both',
    5.4,
    group_blocks=tf_group_blocks,
)
save_single_panel(
    rbp_top,
    '',
    'b',
    'Figure5B_RBP_knockdown_K562_direction_mixed',
    6.5,
    group_blocks=rbp_group_blocks,
    show_cell_line=False,
)

# Combined figure
fig, axes = plt.subplots(
    2, 1, figsize=(11.0, 11.2), gridspec_kw={'height_ratios': [0.90, 1.10], 'hspace': 0.55}
)
draw_panel(
    axes[0],
    tf_top,
    '',
    'a',
    group_blocks=tf_group_blocks,
)
draw_panel(
    axes[1],
    rbp_top,
    '',
    'b',
    group_blocks=rbp_group_blocks,
    show_cell_line=False,
)
add_side_legends(fig, set(pd.concat([tf_top, rbp_top])['group']))
fig.subplots_adjust(left=0.16, right=0.98, top=0.96, bottom=0.14)
fig.savefig(out_dir / 'Figure5_knockdown_color_hatch_combined_tf_positive_plus_both.pdf')
fig.savefig(out_dir / 'Figure5_knockdown_color_hatch_combined_tf_positive_plus_both.png')
plt.close(fig)

# Save code copy with the figure outputs
print('TF selected rows:')
print(tf_top.sort_values(['group', 'total'], ascending=[False, False])[
    ['regulator', 'group', 'downregulated_ir', 'upregulated_ir', 'total']
].to_string(index=False))
print('\nRBP selected rows:')
print(rbp_top.sort_values(['group', 'total'], ascending=[False, False])[
    ['regulator', 'cell_line', 'group', 'downregulated_ir', 'upregulated_ir', '_sort_value', 'total']
].to_string(index=False))
print('Done.')
