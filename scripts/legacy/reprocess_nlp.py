import os
import sys
import json
import sqlite3
import datetime

# Add api directory to path so we can import logic and migrate
sys.path.append(os.path.join(os.getcwd(), "api"))

try:
    from migrate import extract_pdf_text
    from logic import nlp_cluster_analysis
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

DB_PATH = "db/soil_health.sqlite"
FW_DIR = "Frameworks"
OUTPUT_PATH = "api/analysis/current_clusters.json"

def reprocess_nlp():
    print("=== Starting NLP Reprocessing Pipeline ===")
    
    # 1. Reset database
    print("Step 1: Resetting document statuses...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE documents SET status = 'pending', extracted_text = NULL")
    conn.commit()
    print(f"  Reset {cursor.rowcount} documents to pending.")
    
    # 2. Re-extract text
    print("Step 2: Re-extracting text from PDFs...")
    cursor.execute("SELECT id, filename FROM documents WHERE status = 'pending'")
    pending = cursor.fetchall()
    
    success_count = 0
    for doc_id, fname in pending:
        fpath = os.path.join(FW_DIR, fname)
        if os.path.exists(fpath):
            try:
                text = extract_pdf_text(fpath)
                cursor.execute(
                    "UPDATE documents SET extracted_text = ?, status = 'processed', processed_at = datetime('now') WHERE id = ?",
                    (text, doc_id)
                )
                success_count += 1
                if success_count % 10 == 0:
                    print(f"  Processed {success_count}/{len(pending)}...")
            except Exception as e:
                print(f"  Error extracting {fname}: {e}")
                cursor.execute("UPDATE documents SET status = 'error' WHERE id = ?", (doc_id,))
        else:
            print(f"  File not found: {fpath}")
            cursor.execute("UPDATE documents SET status = 'missing' WHERE id = ?", (doc_id,))
    
    conn.commit()
    print(f"  Successfully extracted text from {success_count}/{len(pending)} PDFs.")
    
    # 3. Run Clustering
    print("Step 3: Running NLP Clustering...")
    try:
        # We need to close the connection so logic.py (which uses its own execute_query) can work without locking issues
        conn.close()
        
        # Trigger the clustering logic
        clusters = nlp_cluster_analysis()
        
        if clusters.get("status") == "success":
            print("  Clustering complete.")
            
            # 4. Save results to current_clusters.json
            print(f"Step 4: Saving results to {OUTPUT_PATH}...")
            # We use UTF-8 for the output file
            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                json.dump(clusters, f, indent=2)
            
            print("\n=== NLP Pipeline Summary ===")
            for c in clusters.get("framework_clusters", []):
                print(f"Cluster {c['group']}: {c['theme']}")
                print(f"  Frameworks: {', '.join(c['frameworks'][:5])}{' ...' if len(c['frameworks']) > 5 else ''}")
        else:
            print(f"  Clustering Error: {clusters.get('message')}")
            
    except Exception as e:
        print(f"  Unexpected Error during clustering: {e}")

if __name__ == "__main__":
    reprocess_nlp()
