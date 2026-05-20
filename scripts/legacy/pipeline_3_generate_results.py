import os
import json
import sqlite3
import pandas as pd
import sys

# Setup paths
BASE_PATH = os.getcwd()
DB_PATH = os.path.join(BASE_PATH, "db", "soil_health.sqlite")
OUTPUT_DIR = "principles_indicators"
MATRIX_CSV = os.path.join(OUTPUT_DIR, "framework_principle_matrix.csv")
GAP_REPORT = os.path.join(OUTPUT_DIR, "gap_analysis_report.txt")
EXTRACTED_TERMS_JSON = os.path.join(OUTPUT_DIR, "extracted_framework_terms.json")

# Add API to path for logic imports
sys.path.append(os.path.join(BASE_PATH, "api"))

def sync_to_db():
    print("=== Phase 3: Synchronizing Results to Database ===")
    if not os.path.exists(EXTRACTED_TERMS_JSON):
        print("Extracted terms not found. Run pipeline_2 first.")
        return

    with open(EXTRACTED_TERMS_JSON, 'r', encoding='utf-8') as f:
        best_results = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Simple sync: update document status if it exists
    success_count = 0
    for fw_name, data in best_results.items():
        filename = fw_name + ".pdf"
        cursor.execute("SELECT id FROM frameworks WHERE filename = ?", (filename,))
        res = cursor.fetchone()
        if res:
            fw_id = res[0]
            # Mark as processed in DB (actual text sync happens in detailed logic if needed)
            cursor.execute("UPDATE documents SET status = 'processed', processed_at = datetime('now') WHERE framework_id = ?", (fw_id,))
            success_count += 1
            
    conn.commit()
    conn.close()
    print(f"Updated {success_count} frameworks in database.")

def run_gap_analysis():
    print("=== Phase 4: Performing Thematic Gap Analysis ===")
    if not os.path.exists(MATRIX_CSV):
        print("Matrix CSV not found.")
        return

    df = pd.read_csv(MATRIX_CSV)
    p_cols = [c for c in df.columns if c.startswith("P_")]
    
    if not p_cols:
        print("No principle columns found in matrix.")
        return

    avg_scores = df[p_cols].mean().sort_values()
    coverage = (df[p_cols] > 0).mean() * 100
    
    with open(GAP_REPORT, 'w', encoding='utf-8') as f:
        f.write("=== Soil Health Research Framework: Thematic Gap Analysis ===\n")
        f.write(f"Analyzed {len(df)} frameworks across {len(p_cols)} principles.\n\n")
        
        f.write("A. Principles with LOWEST Alignment (Gaps):\n")
        for p, score in avg_scores.head(5).items():
            f.write(f"  - {p[2:]:<30}: {score:>8.2f} avg matches\n")
        
        f.write("\nB. Principles with HIGHEST Alignment (Strengths):\n")
        for p, score in avg_scores.tail(5).sort_values(ascending=False).items():
            f.write(f"  - {p[2:]:<30}: {score:>8.2f} avg matches\n")
            
        f.write("\nC. Coverage Distribution (% of frameworks addressing principle):\n")
        for p, pct in coverage.sort_values(ascending=False).items():
            f.write(f"  - {p[2:]:<30}: {pct:>6.1f}%\n")

    print(f"Gap analysis report generated: {GAP_REPORT}")

def refresh_nlp_clusters():
    print("=== Phase 5: Refreshing NLP Clusters ===")
    try:
        # Import the cluster analysis logic from the API
        from logic import nlp_cluster_analysis
        clusters = nlp_cluster_analysis()
        if clusters.get("status") == "success":
            print(f"NLP Clustering complete. {clusters.get('num_clusters')} clusters identified.")
        else:
            print(f"Clustering failed: {clusters.get('message')}")
    except Exception as e:
        print(f"Error during clustering: {e}")

if __name__ == "__main__":
    sync_to_db()
    run_gap_analysis()
    refresh_nlp_clusters()
