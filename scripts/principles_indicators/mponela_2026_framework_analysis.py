#!/usr/bin/env python3
"""Framework and agroecological-indicator analysis.

Python counterpart to ``Mponela et al 2026.txt``. The script cleans a long
framework-indicator table, creates indicator/principle matrices, calculates
pathway high-order construct (HOC) scores and an agroecology index, classifies
soil-health indicators, and writes publication-ready heatmaps and tables.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import zscore


REMOVE_INDICATORS = {
    "resource", "matching", "alignment", "health", "soil", "price",
    "sustainable", "practices", "knowledge", "human", "quality",
}

INDICATOR_RENAMES = {
    "emissions": "emission", "cover crops": "cover crop",
    "non-crop plants": "non-crop plant", "shade trees": "shade tree",
    "natural enemies": "natural enemy", "hedgerows": "hedgerow",
    "zai pits": "zai pit", "pollinators": "pollinator",
    "flower strips": "flower strip", "diversified diets": "diversified diet",
    "seed banks": "seed bank", "insects": "insect",
    "on-farm trials": "on-farm trial", "exchange visits": "exchange visit",
    "crop residues": "crop residue",
}

SOIL_PATTERNS = {
    "Biological": r"earthworm|\bworm\b|nematode|microb|macro-?organism|mycorrh|fungi|bacteria|fauna|flora|community|diversity|food web|enzyme|respirat|biomass|mineraliz|potentially mineralizable nitrogen|\bpmn\b|decomposition|soil proteins|root pathogen|weed seed bank",
    "Chemical": r"\bph\b|electrical conductivity|\bec\b|salinit|sodicit|alkalin|acid|exchangeable acidity|cation exchange capacity|\bcec\b|base saturation|active carbon|reactive carbon|total organic carbon|\btoc\b|particulate organic matter|\bpom\b|organic matter|\bom\b|\bc/n\b|carbon and nitrogen|nitrate nitrogen|ammonium|\bno3\b|\bnh4\b|phosphor|available p|olsen|bray|potassium|\bk\b|calcium|magnesium|manganese|iron|zinc|aluminium|aluminum|copper|heavy metals|soil quality|organic",
    "Physical": r"aggregate stability|aggregate size|slake|structure|macroporosity|bulk density|penetration resistance|hardpan|hardness|crusting|compaction|porosity|texture|soil depth|root depth|infiltration|hydraulic conductivity|erosion rating|water holding capacity|pawc|\bfc\b|pwp|soil cover",
    "Management": r"cover crop|crop residue|\bresidue\b|mulch|manure|compost|vermicompost|biochar|contour planting|terrace|\bband\b|minimum till|no-?till|reduced till|tillage|rotation|soil amendment|organic farming|agroforestry|permaculture|hand weeding|nutrient cycling|forest litter",
}

PRINCIPLE_GROUPS = {
    "co-creation of knowledge": "Co-creation & participation",
    "participation": "Co-creation & participation",
    "fairness": "Fairness, connectivity & governance",
    "connectivity": "Fairness, connectivity & governance",
    "land and natural resource governance": "Fairness, connectivity & governance",
    "land and nr governance": "Fairness, connectivity & governance",
    "economic diversification": "Economic diversification & social values",
    "social values and diets": "Economic diversification & social values",
    "input reduction": "Biophysical functioning", "synergy": "Biophysical functioning",
    "recycling": "Biophysical functioning", "biodiversity": "Biophysical functioning",
}


def squish(value: object) -> str:
    """Lowercase, trim and collapse ordinary/non-breaking whitespace."""
    return re.sub(r"\s+", " ", str(value).replace("\u00a0", " ").replace("\u2007", " ").replace("\u202f", " ")).strip().lower()


def clean_data(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path, encoding="latin1")
    data.columns = [squish(c).replace(" ", "_") for c in data.columns]
    required = {"principle", "pathway", "indicator", "pdf_name"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    data = data.drop(columns=["proximity_text"], errors="ignore").copy()
    for col in required:
        data[col] = data[col].fillna("").map(squish)
    data = data.loc[~data["indicator"].isin(REMOVE_INDICATORS)].copy()
    data["indicator"] = data["indicator"].replace(INDICATOR_RENAMES)
    data["pdf_name"] = data["pdf_name"].replace({
        "posthumus et al 2023 food systems decision support toolkit.pdf": "posthumus-fsdst.pdf",
        "check and add soil health1.pdf": "covind-dus.pdf",
    })
    data["principle"] = data["principle"].replace(
        {"land and natural resource governance": "land and nr governance"}
    )
    return data


def save_clustermap(matrix: pd.DataFrame, path: Path, title: str, z_center: bool = False) -> None:
    if matrix.empty or min(matrix.shape) < 2:
        return
    values = matrix.replace([np.inf, -np.inf], np.nan).fillna(0)
    g = sns.clustermap(values, cmap="RdBu_r", center=0 if z_center else None,
                       figsize=(max(8, values.shape[1] * .38), max(8, values.shape[0] * .22)),
                       xticklabels=True, yticklabels=True)
    g.fig.suptitle(title, y=1.01)
    g.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(g.fig)


def zscore_columns(matrix: pd.DataFrame) -> pd.DataFrame:
    out = matrix.astype(float).apply(lambda s: pd.Series(zscore(s, nan_policy="omit"), index=s.index))
    return out.replace([np.inf, -np.inf], np.nan).fillna(0)


def classify_soil_indicator(text: str) -> str:
    for category, pattern in SOIL_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            return category
    return "Unclassified"


def run(input_csv: Path, output_dir: Path, clusters_csv: Path | None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    data = clean_data(input_csv)
    data.to_csv(output_dir / "cleaned_framework_indicators.csv", index=False)

    counts = data.groupby(["pdf_name", "pathway", "principle", "indicator"]).size().rename("count").reset_index()
    hierarchical = counts.pivot_table(index="pdf_name", columns=["pathway", "principle", "indicator"], values="count", fill_value=0)
    hierarchical.to_excel(output_dir / "indicator_matrix_hierarchical.xlsx")

    for principle, subset in data.groupby("principle", dropna=False):
        matrix = subset.groupby(["pdf_name", "indicator"]).size().unstack(fill_value=0)
        label = re.sub(r"[^a-z0-9]+", "_", principle).strip("_") or "missing"
        save_clustermap(matrix, output_dir / f"indicators_{label}.png", f"Indicators: {principle}")

    principle_matrix = data.groupby(["pdf_name", "principle"]).size().unstack(fill_value=0)
    principle_matrix.to_csv(output_dir / "principle_matrix.csv")
    principle_z = zscore_columns(principle_matrix)
    principle_z.to_csv(output_dir / "principle_matrix_zscore.csv")
    save_clustermap(principle_z, output_dir / "principle_heatmap_zscore.png",
                    "Z-score-normalized principles by framework", z_center=True)

    principle_pathway = data[["principle", "pathway"]].drop_duplicates()
    conflicts = principle_pathway.groupby("principle")["pathway"].nunique()
    if (conflicts > 1).any():
        names = ", ".join(conflicts[conflicts > 1].index)
        raise ValueError(f"Principles assigned to multiple pathways: {names}")
    mapping = principle_pathway.set_index("principle")["pathway"]
    hoc = pd.DataFrame(index=principle_z.index)
    for pathway, principles in mapping.groupby(mapping).groups.items():
        valid = [p for p in principles if p in principle_z.columns]
        hoc[pathway] = principle_z[valid].mean(axis=1)
    hoc.index.name = "framework"
    hoc["agroecology_index"] = hoc.mean(axis=1)
    hoc.to_csv(output_dir / "agroecology_index_by_framework.csv")
    save_clustermap(hoc.drop(columns="agroecology_index"), output_dir / "pathway_hoc_heatmap_clustered.png",
                    "Pathway high-order construct scores", z_center=True)

    soil = data.loc[data["principle"].eq("soil health"), ["pdf_name", "indicator"]].drop_duplicates()
    soil["class"] = soil["indicator"].map(classify_soil_indicator)
    soil.to_csv(output_dir / "soil_health_indicator_classes.csv", index=False)

    data["principle_cluster"] = data["principle"].map(PRINCIPLE_GROUPS)
    if clusters_csv:
        clusters = pd.read_csv(clusters_csv)
        if "framework" in clusters and "pdf_name" not in clusters:
            clusters = clusters.rename(columns={"framework": "pdf_name"})
        needed = {"pdf_name", "cluster"}
        if not needed.issubset(clusters.columns):
            raise ValueError("clusters CSV must contain pdf_name (or framework) and cluster")
        clusters["pdf_name"] = clusters["pdf_name"].map(squish)
        joined = data.merge(clusters[list(needed)], on="pdf_name", how="inner")
        pathway_cluster = joined.groupby(["principle_cluster", "cluster"], dropna=False).size().unstack(fill_value=0)
        pathway_cluster.to_csv(output_dir / "pathway_by_cluster.csv")
        soil_joined = soil.merge(clusters[list(needed)], on="pdf_name", how="inner")
        soil_wide = soil_joined.groupby(["cluster", "class"]).size().unstack(fill_value=0)
        soil_wide.to_csv(output_dir / "soil_health_by_cluster_wide.csv")

    print(f"Processed {len(data):,} rows from {data['pdf_name'].nunique():,} frameworks")
    print(f"Outputs: {output_dir.resolve()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/data0526.csv"), help="Long-format input CSV")
    parser.add_argument("--output-dir", type=Path, default=Path("Results"), help="Output directory")
    parser.add_argument("--clusters", type=Path, help="Optional CSV with pdf_name/framework and cluster")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.input, args.output_dir, args.clusters)
