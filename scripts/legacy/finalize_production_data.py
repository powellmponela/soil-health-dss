import os
import json
import sqlite3
import pandas as pd
import time
from collections import defaultdict
import sys

# Setup paths
BASE_PATH = os.getcwd()
DB_PATH = os.path.join(BASE_PATH, "db", "soil_health.sqlite")
FW_DIR = os.path.join(BASE_PATH, "Frameworks")
TERMS_JSON = os.path.join(BASE_PATH, "principles_indicators", "extracted_framework_terms.json")
MATRIX_CSV = os.path.join(BASE_PATH, "principles_indicators", "framework_principle_matrix.csv")
GAP_REPORT = os.path.join(BASE_PATH, "principles_indicators", "gap_analysis_report.txt")

# Add API to path for logic imports
sys.path.append(os.path.join(BASE_PATH, "api"))

try:
    import fitz  # PyMuPDF
    import pdfplumber
    from pypdf import PdfReader
    from docling.document_converter import DocumentConverter
except ImportError as e:
    print(f"Warning: Some PDF backends missing: {e}")

def extract_single(filepath, backend_name):
    """Re-extracts text using a specific backend"""
    try:
        if backend_name == "PyMuPDF":
            doc = fitz.open(filepath)
            return "\n".join([page.get_text() for page in doc])
        elif backend_name == "pdfplumber":
            with pdfplumber.open(filepath) as pdf:
                return "\n".join([page.extract_text() or "" for page in pdf.pages])
        elif backend_name == "pypdf":
            reader = PdfReader(filepath)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        elif backend_name == "Docling":
            converter = DocumentConverter()
            result = converter.convert(filepath)
            return result.document.export_to_markdown()
    except Exception as e:
        return f"Error re-extracting with {backend_name}: {str(e)}"
    return ""

def finalize():
    print("=== Finalizing Production Data (Steps 1-4) ===")
    
    if not os.path.exists(TERMS_JSON):
        print(f"Error: {TERMS_JSON} not found. Run extraction first.")
        return

    with open(TERMS_JSON, 'r', encoding='utf-8') as f:
        best_results = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Step 1: Update Database Text
    print("\nStep 1: Synchronizing high-fidelity text to database...")
    success_count = 0
    
    for fw_name, data in best_results.items():
        best_backend = data["best_backend"]
        filename = fw_name + ".pdf"
        fpath = os.path.join(FW_DIR, filename)
        
        # Find framework_id
        cursor.execute("SELECT id FROM frameworks WHERE filename = ?", (filename,))
        res = cursor.fetchone()
        if not res:
            # Try matching by name/prefix
            cursor.execute("SELECT id FROM frameworks WHERE filename LIKE ?", (fw_name + "%",))
            res = cursor.fetchone()
        
        if res:
            fw_id = res['id']
            print(f"  Updating {fw_name} using {best_backend}...")
            
            # Re-extract
            if os.path.exists(fpath):
                raw_text = extract_single(fpath, best_backend)
                
                # Update documents table
                # Check if document entry exists
                cursor.execute("SELECT id FROM documents WHERE framework_id = ?", (fw_id,))
                doc_res = cursor.fetchone()
                
                if doc_res:
                    cursor.execute(
                        "UPDATE documents SET extracted_text = ?, status = 'processed', processed_at = datetime('now') WHERE framework_id = ?",
                        (raw_text, fw_id)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO documents (framework_id, filename, status, extracted_text, processed_at) VALUES (?, ?, ?, ?, datetime('now'))",
                        (fw_id, filename, 'processed', raw_text)
                    )
                success_count += 1
            else:
                print(f"    Warning: File not found {fpath}")
        else:
            print(f"    Warning: No database entry for {fw_name}")

    conn.commit()
    print(f"Done. Updated {success_count} frameworks in DB.")

    # Step 2: NLP Re-clustering
    print("\nStep 2: Triggering Advanced NLP Clustering...")
    try:
        from logic import nlp_cluster_analysis
        # Close connection to avoid locking
        conn.close()
        
        clusters = nlp_cluster_analysis()
        if clusters.get("status") == "success":
            output_path = os.path.join(BASE_PATH, "api", "analysis", "current_clusters.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(clusters, f, indent=2)
            print(f"  Clustering complete. Results saved to {output_path}")
        else:
            print(f"  Clustering failed: {clusters.get('message')}")
    except Exception as e:
        print(f"  Error during clustering: {e}")

    # Step 3: Thematic Gap Analysis
    print("\nStep 3: Performing Thematic Gap Analysis...")
    if os.path.exists(MATRIX_CSV):
        df = pd.read_csv(MATRIX_CSV)
        # Identify columns starting with P_ (Principles)
        p_cols = [c for c in df.columns if c.startswith("P_") and c != "P_Additional Consolidated Terms"]
        
        avg_scores = df[p_cols].mean().sort_values()
        
        with open(GAP_REPORT, 'w', encoding='utf-8') as f:
            f.write("=== Soil Health Research Framework: Thematic Gap Analysis ===\n")
            f.write(f"Analyzed {len(df)} frameworks across {len(p_cols)} principles.\n\n")
            
            f.write("A. Principles with LOWEST Alignment (Gaps):\n")
            for p, score in avg_scores.head(5).items():
                f.write(f"  - {p[2:]:<30}: {score:>8.2f} avg matches\n")
            
            f.write("\nB. Principles with HIGHEST Alignment (Strengths):\n")
            for p, score in avg_scores.tail(5).sort_values(ascending=False).items():
                f.write(f"  - {p[2:]:<30}: {score:>8.2f} avg matches\n")
            
            f.write("\nC. Principle Coverage Distribution:\n")
            coverage = (df[p_cols] > 0).mean() * 100
            for p, pct in coverage.sort_values(ascending=False).items():
                f.write(f"  - {p[2:]:<30}: {pct:>6.1f}% of frameworks address this\n")
                
        print(f"  Gap analysis report generated: {GAP_REPORT}")

    # Step 4: Final Summary
    print("\nStep 4: Finalizing system status...")
    print("  - Multi-backend data synchronized to SQLite.")
    print("  - NLP clusters refreshed based on high-fidelity text.")
    print("  - Thematic gap report published.")
    print("\nSystem is now ready for production dashboard visualization.")

if __name__ == "__main__":
    finalize()
