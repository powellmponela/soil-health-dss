import os
import pandas as pd
import numpy as np
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import pdist
import logging
import json
import re

try:
    import seaborn as sns
    import matplotlib.pyplot as plt
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_data(df):
    df.columns = [c.lower() for c in df.columns]
    
    for col in ['principle', 'pathway', 'indicator', 'pdf_name']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
            
    # Replicate R filter
    to_remove = ["resource", "matching", "alignment", "health", "soil", "price", "sustainable", "practices", "knowledge", "human", "quality"]
    df = df[~df['indicator'].isin(to_remove)]
    
    # Replicate replacements
    replacements = {
        "emissions": "emission",
        "cover crops": "cover crop",
        "non-crop plants": "non-crop plant",
        "shade trees": "shade tree",
        "natural enemies": "natural enemy",
        "hedgerows": "hedgerow",
        "zai pits": "zai pit",
        "pollinators": "pollinator",
        "flower strips": "flower strip",
        "diversified diets": "diversified diet",
        "seed banks": "seed bank",
        "insects": "insect",
        "on-farm trials": "on-farm trial",
        "exchange visits": "exchange visit",
        "crop residues": "crop residue"
    }
    df['indicator'] = df['indicator'].replace(replacements)
    
    df['pdf_name'] = df['pdf_name'].replace({
        "posthumus et al 2023 food systems decision support toolkit.pdf": "posthumus-fsdst",
        "check and add soil health1.pdf": "covind-dus"
    })
    
    if 'principle' in df.columns:
        df['principle'] = df['principle'].replace({"land and natural resource governance ": "land and nr governance"})
        df['principle'] = df['principle'].apply(lambda x: re.sub(r'[\u00A0\u2007\u202F]', ' ', x).strip())
        
    return df

def run_clustering():
    base_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_folder, "data", "data0526.csv")
    results_folder = os.path.join(base_folder, "api", "results")
    os.makedirs(results_folder, exist_ok=True)
    
    proximity_path = os.path.join(results_folder, "all_themes_proximity_results.csv")
    gen_matrix_path = os.path.join(results_folder, "principle_matrix_generated.csv")

    principle_matrix = None

    if os.path.exists(data_path):
        df = pd.read_csv(data_path, encoding='latin1')
        if 'proximity_text' in df.columns:
            df = df.drop(columns=['proximity_text'])
        df = clean_data(df)
        if 'pdf_name' in df.columns and 'principle' in df.columns:
            principle_matrix = df.groupby(['pdf_name', 'principle']).size().unstack(fill_value=0)
    elif os.path.exists(proximity_path):
        df = pd.read_csv(proximity_path)
        framework_col = "Framework" if "Framework" in df.columns else ("pdf_name" if "pdf_name" in df.columns else df.columns[0])
        theme_col = "theme_name" if "theme_name" in df.columns else ("principle" if "principle" in df.columns else df.columns[1])
        principle_matrix = df.groupby([framework_col, theme_col]).size().unstack(fill_value=0)
    elif os.path.exists(gen_matrix_path):
        principle_matrix = pd.read_csv(gen_matrix_path).set_index("pdf_name")

    if principle_matrix is None or principle_matrix.empty:
        logger.error("No valid dataset or generated matrix found for clustering.")
        return {"status": "error", "message": "No matrix or proximity data available"}

    # Z-score normalization
    principle_matrix_z = (principle_matrix - principle_matrix.mean()) / principle_matrix.std(ddof=0).replace(0, 1)
    principle_matrix_z = principle_matrix_z.fillna(0)

    # Pathway grouping mapping
    pathway_definitions = {
        "Improve Resource Efficiency": ["recycling", "input reduction"],
        "Strengthen Resilience": ["soil health", "animal health", "biodiversity", "synergy", "economic diversification"],
        "Secure Social Equity": ["co-creation of knowledge", "social values and diets", "fairness", "connectivity", "land and natural resource governance", "participation"]
    }

    hoc_scores = pd.DataFrame(index=principle_matrix_z.index)
    col_lookup = {str(c).lower().strip(): c for c in principle_matrix_z.columns}
    for pathway, p_list in pathway_definitions.items():
        matched_cols = [col_lookup[p] for p in p_list if p in col_lookup]
        if matched_cols:
            hoc_scores[pathway] = principle_matrix_z[matched_cols].mean(axis=1)
        else:
            hoc_scores[pathway] = 0.0

    hoc_scores['agroecology_index'] = hoc_scores.mean(axis=1)
    hoc_scores.reset_index().to_csv(os.path.join(results_folder, "agroecology_index_by_framework.csv"), index=False)

    # Plotting heatmaps
    if PLOTTING_AVAILABLE and not principle_matrix_z.empty:
        try:
            # 1. Z-score heatmap
            plt.figure(figsize=(10, 18))
            cg = sns.clustermap(
                principle_matrix_z, 
                cmap="RdBu_r", 
                metric="euclidean", 
                method="complete",
                figsize=(10, 15),
                cbar_kws={'label': 'Z-Score'}
            )
            cg.ax_heatmap.set_title("Z-score Normalized Heatmap of Principles by Framework")
            plt.savefig(os.path.join(results_folder, "principle_heatmap_zscore.jpeg"), dpi=300, bbox_inches='tight')
            plt.close('all')

            # 2. Agroecology Index Heatmap
            hoc_matrix = hoc_scores.drop(columns=['agroecology_index']).loc[hoc_scores.sort_values(by='agroecology_index', ascending=False).index]
            plt.figure(figsize=(6, 15))
            sns.heatmap(hoc_matrix, cmap="RdBu_r", annot=False)
            plt.title("Agroecology Index Heatmap")
            plt.savefig(os.path.join(results_folder, "agroecology_index_heatmap.jpeg"), dpi=300, bbox_inches='tight')
            plt.close('all')
            logger.info("Successfully generated heatmaps: principle_heatmap_zscore.jpeg and agroecology_index_heatmap.jpeg")

        except Exception as e:
            logger.error(f"Error generating plots: {e}")

    return {"status": "success", "message": "Clustering complete", "heatmaps_generated": PLOTTING_AVAILABLE}

if __name__ == "__main__":
    run_clustering()

