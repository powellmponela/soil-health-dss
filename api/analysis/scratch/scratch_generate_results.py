import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage
import dynamicTreeCut
import os
import re
import sqlite3

PRINCIPLE_MATRIX_PATH = os.path.join("c:\\SOIL HEALTH", "principles_indicators", "principle_matrix.xlsx")
DB_PATH = os.path.join("c:\\SOIL HEALTH", "db", "soil_health.sqlite")

def get_framework_name(filename, frameworks_list):
    if not filename:
        return "Unknown"
    sn = re.sub(r'\.pdf$', '', filename).lower().strip()
    for fw in frameworks_list:
        if fw['filename'] and re.sub(r'\.pdf$', '', fw['filename']).lower().strip() == sn:
            return fw['name']
    return filename

def run_study_analysis():
    # Load matrix
    try:
        df = pd.read_excel(PRINCIPLE_MATRIX_PATH)
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return

    data_mat = df.iloc[:, 1:14].copy()
    data_mat.index = df['pdf_name']
    
    # Standardize
    data_mat_std = (data_mat - data_mat.mean()) / data_mat.std()
    
    # Distance and linkage
    d = pdist(data_mat_std)
    hc = linkage(d, method='average')
    
    # Cut tree
    distM = squareform(d)
    # Use cutreeHybrid instead of cutreeDynamic
    try:
        clusters = dynamicTreeCut.cutreeHybrid(hc, distM=distM, deepSplit=2, pamStage=True)
        # Note: some versions of the library return a dict or an object with 'labels'
        if hasattr(clusters, 'labels'):
            cluster_ids = clusters.labels
        elif isinstance(clusters, dict):
            cluster_ids = clusters['labels']
        else:
            cluster_ids = clusters # Assuming it's already the list of IDs
    except Exception as e:
        print(f"Error in clustering: {e}")
        # Fallback to a simple cut if needed
        from scipy.cluster.hierarchy import fcluster
        cluster_ids = fcluster(hc, t=5, criterion='maxclust')

    # Get all frameworks for naming
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, filename FROM frameworks")
    all_fws = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Cluster Labels from the study
    cluster_labels = {
        1: "Agroecology & ecosystem",
        2: "Efficiency & soil management",
        3: "Policy/outcome & standards",
        4: "Soil-health assessment tools",
        5: "Integrated landscape & livelihoods"
    }
    
    print("# Results based on Study: Out 6. Integrated framework R4")
    print("\n## Framework Clustering Analysis (n=64)")
    print("\n| Cluster ID | Theme | Top Frameworks |")
    print("|------------|-------|----------------|")
    
    unique_clusters = np.unique(cluster_ids)
    for cl_id in unique_clusters:
        if cl_id == 0: continue # Unassigned
        sns = data_mat.index[cluster_ids == cl_id]
        names = []
        for sn in sns:
            names.append(get_framework_name(sn + ".pdf", all_fws))
        
        theme = cluster_labels.get(cl_id, "Other")
        print(f"| {cl_id} | {theme} | {', '.join(names[:3])}{' ...' if len(names) > 3 else ''} |")

    print("\n## Key Principles Alignment (Average Score %)")
    avg_scores = data_mat.mean().sort_values(ascending=False)
    print("\n| Principle | Avg Frequency/Score |")
    print("|-----------|---------------------|")
    for p, s in avg_scores.items():
        print(f"| {p.strip()} | {s:.1f} |")

if __name__ == "__main__":
    run_study_analysis()
