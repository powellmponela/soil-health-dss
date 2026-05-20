"""
Figure 3: Z-score Heatmap of Agroecological Principles
Python port of:  "dynamic tree cut  3-5.R"

Pipeline (identical to R):
  1. Z-score normalise columns (scale())
  2. Clip to [-3, 3]
  3. hclust: euclidean distance, complete linkage
  4. cutreeDynamic hybrid (deepSplit=2, minClusterSize=3 rows / 2 cols)
  5. merge_to_k: merge dynamic clusters -> exactly k=5 row / k=3 col groups
     via centroid hierarchical clustering (same dist/linkage)
  6. pheatmap-style plot with annotation bars and gap lines
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']
plt.rcParams['font.family'] = 'sans-serif'
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, leaves_list, dendrogram, fcluster
import dynamicTreeCut

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PRINCIPLE_MATRIX_PATH = os.path.join(BASE_PATH, "principles_indicators", "principle_matrix.xlsx")
OUTPUT_PATH = os.path.join(BASE_PATH, "api", "results", "figure3_heatmap.png")

# ── Domain Metadata (Matches R and logic.py) ──────────────────────────────
DOMAIN_ORDER = [1, 2, 3, 4, 5]
DOMAIN_INFO = {
    1: {"label": "Domain 1: Diagnostics (Soil-health Assessment)", "color": "#f4a261"},
    2: {"label": "Domain 2: Stewardship (Soil Management)", "color": "#e63946"},
    3: {"label": "Domain 3: Safeguards (Agroecological & Ecosystem)", "color": "#2a9d8f"},
    4: {"label": "Domain 4: Embedding (Integrated Landscape & Livelihood)", "color": "#457b9d"},
    5: {"label": "Domain 5: Iterative Learning (Policy & Outcome)", "color": "#6d597a"},
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def dynamic_cut(hc_linkage, dist_mat, deep_split=2, min_cluster_size=3):
    """Run cutreeDynamic hybrid and return labels array (0 = unassigned)."""
    res = dynamicTreeCut.cutreeHybrid(
        hc_linkage, distM=dist_mat,
        deepSplit=deep_split, minClusterSize=min_cluster_size, pamStage=True
    )
    if isinstance(res, dict):
        labels = np.array(res["labels"])
    elif hasattr(res, "labels"):
        labels = np.array(res.labels)
    else:
        labels = np.array(res)
    return labels


def merge_to_k(mat, cl, k, hc_linkage=None, dist_metric="euclidean", link_method="complete"):
    """
    Port of R merge_to_k():
    If dynamic cut produced > k groups: cluster centroids and merge down.
    If <= k groups: relabel 1..n as-is (same as R factor() call).
    NaN/0 labels treated as NA -> stay 0 after merge.
    """
    valid_ids = sorted(set(cl[~np.isnan(cl.astype(float))]) - {0})
    n = len(valid_ids)

    if n == 0:
        # Fallback: use fcluster directly on the linkage if provided, otherwise all 1s
        if hc_linkage is not None:
            return fcluster(hc_linkage, k, criterion="maxclust")
        return np.ones(mat.shape[0], dtype=int)

    if n <= k:
        # R: as.integer(factor(cl, levels = cl_ids))
        id_map = {old: (i + 1) for i, old in enumerate(valid_ids)}
        return np.array([id_map.get(c, 0) for c in cl])

    # Compute centroids
    centroids = np.vstack([
        mat[cl == g].mean(axis=0) for g in valid_ids
    ])

    # Cluster centroids
    d_c = pdist(centroids, metric=dist_metric)
    hc_c = linkage(d_c, method=link_method)
    map_new = fcluster(hc_c, k, criterion="maxclust")          # 1..k

    id_to_new = {old: int(map_new[i]) for i, old in enumerate(valid_ids)}
    return np.array([id_to_new.get(c, 0) for c in cl])


# ── Main ──────────────────────────────────────────────────────────────────────
def generate_figure3():
    print("Generating Figure 3 (R-equivalent pipeline)...")

    # 1. Load
    df = pd.read_excel(PRINCIPLE_MATRIX_PATH)
    first_col = df.columns[0]
    if first_col != "pdf_name":
        df = df.rename(columns={first_col: "pdf_name"})

    # 2. Build matrix (rows = frameworks, cols = principles)
    df["pdf_name_clean"] = df["pdf_name"].str.lower().str.strip().str.replace(r"\.pdf$", "", regex=True)
    df = df.dropna(subset=["pdf_name_clean"])
    df = df[df["pdf_name_clean"] != ""]
    
    # ── Map labels to Author-Date (Abbreviation) ──────────────────────────
    import json
    META_PATH = os.path.join(BASE_PATH, "data", "framework_metadata.json")
    label_map = {}
    if os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            meta_data = json.load(f)
            for item in meta_data:
                fname = item["filename"].lower().replace(".pdf", "")
                author_date = item.get("name", "Unknown").replace('‐', '-')
                # Extract abbreviation from filename if it contains a hyphen
                if "-" in fname:
                    abbr = fname.split("-")[-1].upper()
                else:
                    abbr = fname.upper()
                label_map[fname] = f"{author_date} ({abbr})"
    
    # Apply mapping, fallback to original name if missing
    row_labels = [label_map.get(n, n) for n in df["pdf_name_clean"].values]
    
    mat_raw = df.iloc[:, 1:14].copy()
    mat_raw.index = row_labels

    # Fill NaN with column mean (consistent with R which uses complete cases per column in scale())
    for col in mat_raw.columns:
        mat_raw[col] = mat_raw[col].fillna(mat_raw[col].mean())

    mat_raw = mat_raw.astype(float)

    # 3. Z-score (column-wise, as R scale())
    col_mean = mat_raw.mean()
    col_std  = mat_raw.std().replace(0, 1)
    mat_z    = (mat_raw - col_mean) / col_std

    # 4. Clip to [-3, 3]
    mat_plot = mat_z.clip(-3, 3)

    # 5. Hierarchical clustering  (euclidean + complete, as R)
    dist_row = pdist(mat_plot.values, metric="euclidean")
    dist_col = pdist(mat_plot.values.T, metric="euclidean")
    row_hc   = linkage(dist_row, method="complete")
    col_hc   = linkage(dist_col, method="complete")

    # 6. Dynamic Tree Cut
    distM_row = squareform(dist_row)
    distM_col = squareform(dist_col)
    row_cl0 = dynamic_cut(row_hc, distM_row, deep_split=2, min_cluster_size=3)
    col_cl0 = dynamic_cut(col_hc, distM_col, deep_split=2, min_cluster_size=2)

    # Replace 0 with NaN (unassigned) as R does
    row_cl0 = row_cl0.astype(float); row_cl0[row_cl0 == 0] = np.nan
    col_cl0 = col_cl0.astype(float); col_cl0[col_cl0 == 0] = np.nan

    # 7. merge_to_k  (k_row=5, k_col=3)
    k_row, k_col = 5, 3
    row_cl5 = merge_to_k(mat_plot.values, row_cl0, k=k_row, hc_linkage=row_hc)
    col_cl3 = merge_to_k(mat_plot.values.T, col_cl0, k=k_col, hc_linkage=col_hc)

    # ── Print audit (mirrors R cat() output) ──────────────────────────────
    print(f"Framework domain levels (should be {k_row}): "
          f"{sorted(set(row_cl5[row_cl5 > 0]))}")
    print(f"Principle groups: {sorted(set(col_cl3[col_cl3 > 0]))}")
    print(f"Frameworks plotted: {mat_plot.shape[0]} | "
          f"Principles plotted: {mat_plot.shape[1]}")

    # ── Reorder rows & cols by dendrogram leaves ──────────────────────────
    row_order = leaves_list(row_hc)   # row dendrogram order
    col_order = leaves_list(col_hc)

    mat_reordered    = mat_plot.iloc[row_order, :].iloc[:, col_order]
    row_cl_reordered = row_cl5[row_order]
    col_cl_reordered = col_cl3[col_order]
    row_names        = mat_plot.index[row_order]
    col_names        = mat_plot.columns[col_order]

    # ── Gap positions (where cluster label changes in dendrogram order) ───
    def gap_positions(labels):
        gaps = []
        for i in range(1, len(labels)):
            if labels[i] != labels[i - 1]:
                gaps.append(i)
        return gaps

    gaps_row = gap_positions(row_cl_reordered)
    gaps_col = gap_positions(col_cl_reordered)

    # ── Annotation bar colours ─────────────────────────────────────────────
    # Map dynamic cluster IDs (1-5) to the specified colours
    cluster_to_color = {cid: DOMAIN_INFO[cid]["color"] for cid in DOMAIN_ORDER}
    cluster_to_color[0] = "#d3d3d3"

    row_bar_colors = [cluster_to_color.get(c, "lightgrey") for c in row_cl_reordered]

    col_palette = sns.color_palette("muted", k_col) # Changed to muted for better contrast
    col_cluster_ids = sorted(set(col_cl_reordered[col_cl_reordered > 0]))
    col_to_color = {cid: col_palette[i] for i, cid in enumerate(col_cluster_ids)}
    col_to_color[0] = (0.85, 0.85, 0.85)
    col_bar_colors = [col_to_color.get(c, (0.85, 0.85, 0.85)) for c in col_cl_reordered]
    
    # ── Principle Group Names ──────────────────────────────────────────
    PRINCIPLE_GROUP_NAMES = {
        1: "Environmental/Ecological",
        2: "Socio-Economic/Governance",
        3: "Institutional/Knowledge"
    }

    # ── Plot (pheatmap-style via seaborn clustermap) ──────────────────────
    # Clear Series names to prevent seaborn from adding small automatic labels that overlap
    row_colors_series = pd.Series(row_bar_colors, index=row_names, name="")
    col_colors_series = pd.Series(col_bar_colors, index=col_names, name="")

    g = sns.clustermap(
        mat_reordered,
        row_cluster=True,           # Enable row clustering as requested
        col_cluster=True,           # Show principle dendrogram
        row_colors=row_colors_series,
        col_colors=col_colors_series,
        cmap=sns.diverging_palette(240, 10, as_cmap=True),
        center=0, vmin=-3, vmax=3,
        figsize=(26, 36),           # Balanced width
        yticklabels=True,
        xticklabels=True,
        dendrogram_ratio=(0.15, 0.1), 
        colors_ratio=0.02,
        cbar_pos=(1.12, 0.45, 0.03, 0.12), # Aligned with legends
        linewidths=0.5,
        linecolor='white'
    )

    ax = g.ax_heatmap

    # Draw gap lines between row clusters
    for gap in gaps_row:
        ax.axhline(y=gap, color="white", linewidth=2, zorder=3)

    # Draw gap lines between col clusters
    for gap in gaps_col:
        ax.axvline(x=gap, color="white", linewidth=2, zorder=3)

    # Tick aesthetics
    g.ax_heatmap.yaxis.set_ticks_position('right')
    
    # Sanitize tick labels for hyphen/whitespace issues
    y_labels = [label.get_text().replace('‐', '-').replace('\xa0', ' ') for label in g.ax_heatmap.get_yticklabels()]
    x_labels = [label.get_text().replace('‐', '-').replace('\xa0', ' ') for label in g.ax_heatmap.get_xticklabels()]
    
    g.ax_heatmap.set_yticklabels(y_labels, rotation=0, fontsize=18, fontfamily="sans-serif", fontweight='medium')
    g.ax_heatmap.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=24, fontweight='bold')

    # ── Text Annotations for Color Bars ──────────────────────────────────
    # Principle group label at the far right of the top color bar
    g.ax_col_colors.text(mat_reordered.shape[1] + 0.2, 0.5, 'Principle Group', 
                         va='center', ha='left', fontsize=18, fontweight='bold')
    
    # Framework domain label at the TOP of the left color bar
    g.ax_row_colors.text(0.5, -0.2, 'Framework Domain', 
                         va='bottom', ha='center', fontsize=18, fontweight='bold', rotation=90)

    # ── Title ─────────────────────────────────────────────────────────────
    g.fig.suptitle(
        "Figure 3: Z-score Heatmap of Agroecological Principles (n=64)",
        fontsize=38, y=1.03, fontweight='bold'
    )

    # ── Legends on the far right ──────────────────────────────────────────
    # 1. Principle Group Legend (Top Right)
    principle_patches = [
        mpatches.Patch(color=col_to_color[cid], label=PRINCIPLE_GROUP_NAMES.get(cid, f"Group {cid}"))
        for cid in col_cluster_ids
    ]
    leg1 = g.fig.legend(
        handles=principle_patches, title="Principle Group",
        bbox_to_anchor=(1.12, 0.95), loc="upper left", # Aligned left edge
        fontsize=22, title_fontsize=26, frameon=True,
        shadow=True, borderpad=1.5,
        labelspacing=1.2,
        handlelength=2.5,
        handleheight=2.0,
        framealpha=0.98
    )
    leg1.get_title().set_fontweight('bold')

    # Calculate domain counts dynamically
    unique_ids, counts = np.unique(row_cl5, return_counts=True)
    domain_counts = dict(zip(unique_ids, counts))

    # 2. Framework Domain Legend (Below Principle Legend)
    framework_patches = [
        mpatches.Patch(color=DOMAIN_INFO[cid]["color"], 
                      label=f"{DOMAIN_INFO[cid]['label']} (n={domain_counts.get(cid, 0)})") 
        for cid in DOMAIN_ORDER
    ]
    leg2 = g.fig.legend(
        handles=framework_patches, title="Framework Domain",
        bbox_to_anchor=(1.12, 0.78), loc="upper left", # Aligned left edge
        fontsize=22, title_fontsize=26, frameon=True,
        shadow=True, borderpad=1.5,
        labelspacing=1.2,
        handlelength=2.5,
        handleheight=2.0,
        framealpha=0.98
    )
    leg2.get_title().set_fontweight('bold')

    # ── Colorbar label (SD) on the right ──────────────────────────────────
    g.ax_cbar.set_ylabel("Z-score (SD)", fontsize=24, labelpad=25, fontweight='bold')
    g.ax_cbar.yaxis.set_label_position("right") # Label on the right side of the bar
    g.ax_cbar.set_yticks([-3, -2, -1, 0, 1, 2, 3])
    g.ax_cbar.set_yticklabels(["-3 SD", "-2 SD", "-1 SD", "Mean (0)", "+1 SD", "+2 SD", "+3 SD"], fontsize=20)
    g.ax_cbar.tick_params(axis='y', length=12, width=2.5)

    # ── Save ──────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    g.savefig(OUTPUT_PATH, dpi=200, bbox_inches="tight")
    print(f"Figure 3 saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_figure3()
