#!/usr/bin/env python3
"""Cluster a framework-by-principle matrix and draw the Figure 2 heatmap.

This is a transparent Python analogue of the R Dynamic Tree Cut workflow.
SciPy does not implement dynamicTreeCut's hybrid algorithm exactly, so an
adaptive inconsistency cut is used first; cluster centroids are then merged or
the original hierarchy is cut to obtain exactly the requested group count.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import fcluster, leaves_list, linkage
from scipy.spatial.distance import pdist
from scipy.stats import zscore


DOMAIN_NAMES = {
    1: "Soil health assess", 2: "AE-ecosystem", 3: "Landscape-livelihood",
    4: "Soil steward", 5: "Policy-outcome",
}
DOMAIN_COLORS = {
    "Soil steward": "orange", "Soil health assess": "green",
    "AE-ecosystem": "red", "Landscape-livelihood": "purple",
    "Policy-outcome": "blue",
}


def adaptive_exact_clusters(matrix: np.ndarray, k: int, method: str, metric: str, min_size: int) -> tuple[np.ndarray, np.ndarray]:
    """Adaptive tree cut followed by deterministic reduction to exactly k groups."""
    if len(matrix) < k:
        raise ValueError(f"Cannot create {k} clusters from only {len(matrix)} observations")
    tree = linkage(pdist(matrix, metric=metric), method=method)
    adaptive = fcluster(tree, t=max(1.0, 2.0 - 0.15 * min_size), criterion="inconsistent")
    unique = np.unique(adaptive)
    if len(unique) > k:
        centroids = np.vstack([matrix[adaptive == group].mean(axis=0) for group in unique])
        centroid_tree = linkage(pdist(centroids, metric=metric), method=method)
        reduced = fcluster(centroid_tree, t=k, criterion="maxclust")
        mapping = dict(zip(unique, reduced))
        labels = np.array([mapping[x] for x in adaptive])
    elif len(unique) < k:
        labels = fcluster(tree, t=k, criterion="maxclust")
    else:
        labels = adaptive
    return labels.astype(int), tree


def read_matrix(path: Path, id_column: str) -> pd.DataFrame:
    frame = pd.read_excel(path) if path.suffix.lower() in {".xlsx", ".xls"} else pd.read_csv(path)
    if id_column not in frame.columns:
        if frame.columns[0].lower().startswith("unnamed"):
            frame = frame.rename(columns={frame.columns[0]: id_column})
        else:
            raise ValueError(f"ID column '{id_column}' not found")
    frame[id_column] = frame[id_column].astype("string").str.strip().str.lower()
    frame = frame.dropna(subset=[id_column]).loc[lambda x: x[id_column].ne("")]
    numeric = frame.drop(columns=id_column).apply(pd.to_numeric, errors="coerce")
    numeric = numeric.loc[:, numeric.notna().any()]
    if numeric.shape[1] < 2:
        raise ValueError("Input must contain at least two numeric principle columns")
    numeric = numeric.fillna(0)
    numeric.index = frame[id_column]
    return numeric


def run(input_path: Path, output: Path, assignments: Path, id_column: str,
        row_groups: int, column_groups: int, metric: str, method: str) -> None:
    raw = read_matrix(input_path, id_column)
    z = raw.apply(lambda col: pd.Series(zscore(col, nan_policy="omit"), index=raw.index))
    z = z.replace([np.inf, -np.inf], np.nan).fillna(0).clip(-3, 3)
    row_labels, row_tree = adaptive_exact_clusters(z.to_numpy(), row_groups, method, metric, 3)
    col_labels, col_tree = adaptive_exact_clusters(z.to_numpy().T, column_groups, method, metric, 2)

    row_order = leaves_list(row_tree)
    col_order = leaves_list(col_tree)
    shown = z.iloc[row_order, col_order]
    ordered_row_labels = row_labels[row_order]
    ordered_col_labels = col_labels[col_order]
    domain_labels = [DOMAIN_NAMES.get(int(x), f"Domain {x}") for x in row_labels]

    assignments.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({id_column: z.index, "framework_domain_code": row_labels,
                  "framework_domain": domain_labels}).to_csv(assignments, index=False)
    pd.DataFrame({"principle": z.columns, "principle_group": col_labels}).to_csv(
        assignments.with_name(assignments.stem + "_principles.csv"), index=False)

    output.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(max(9, shown.shape[1] * .55), max(10, shown.shape[0] * .27)))
    sns.heatmap(shown, cmap="RdBu_r", center=0, vmin=-3, vmax=3, ax=ax,
                cbar_kws={"label": "Z-score (SD from principle mean)"})
    ax.set_xlabel("Agroecological principle")
    ax.set_ylabel("Framework")
    ax.tick_params(axis="x", rotation=90, labelsize=8)
    ax.tick_params(axis="y", labelsize=7)
    for boundary in np.flatnonzero(np.diff(ordered_row_labels)) + 1:
        ax.axhline(boundary, color="black", linewidth=1.3)
    for boundary in np.flatnonzero(np.diff(ordered_col_labels)) + 1:
        ax.axvline(boundary, color="black", linewidth=1.3)
    present = list(dict.fromkeys(domain_labels))
    handles = [Patch(facecolor=DOMAIN_COLORS.get(name, "grey"), label=name) for name in present]
    ax.legend(handles=handles, title="Framework domain", loc="upper left", bbox_to_anchor=(1.17, 1))
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Frameworks plotted: {z.shape[0]} | Principles plotted: {z.shape[1]}")
    print(f"Heatmap: {output.resolve()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="CSV/XLSX framework-by-principle matrix")
    parser.add_argument("--output", type=Path, default=Path("Results/principle_heatmap_zscore.png"))
    parser.add_argument("--assignments", type=Path, default=Path("Results/framework_domain_assignments.csv"))
    parser.add_argument("--id-column", default="author_abbreviation")
    parser.add_argument("--row-groups", type=int, default=5)
    parser.add_argument("--column-groups", type=int, default=3)
    parser.add_argument("--metric", default="euclidean")
    parser.add_argument("--method", default="complete", choices=["single", "complete", "average", "weighted", "centroid", "median", "ward"])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.input, args.output, args.assignments, args.id_column,
        args.row_groups, args.column_groups, args.metric, args.method)
