import json
import os
import re
import time
from collections import defaultdict
import pandas as pd

# Configuration
FRAMEWORKS_DIR = "Frameworks"
ONTOLOGY_FILE = "principles_indicators/Ontology_index.json"
OUTPUT_DIR = "principles_indicators"
PROCESSED_DATA_DIR = os.path.join("data", "processed")

# Output Paths
OUTPUT_MATRIX_CSV = os.path.join(OUTPUT_DIR, "framework_principle_matrix.csv")
OUTPUT_TERMS_JSON = os.path.join(OUTPUT_DIR, "extracted_framework_terms.json")
BACKEND_REPORT_CSV = os.path.join(PROCESSED_DATA_DIR, "backend_comparison_report.csv")

# ── Extraction Backends ───────────────────────────────────────────────────────
def extract_pymupdf(pdf_path):
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = " ".join([page.get_text() for page in doc])
        doc.close()
        return text, None
    except Exception as e: return "", str(e)

def extract_pdfplumber(pdf_path):
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = " ".join([page.extract_text() or "" for page in pdf.pages])
        return text, None
    except Exception as e: return "", str(e)

def extract_pypdf(pdf_path):
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        text = " ".join([page.extract_text() or "" for page in reader.pages])
        return text, None
    except Exception as e: return "", str(e)

def extract_docling(pdf_path):
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        return result.document.export_to_text(), None
    except Exception as e: return "", str(e)

BACKENDS = [
    ("PyMuPDF", extract_pymupdf),
    ("pdfplumber", extract_pdfplumber),
    ("pypdf", extract_pypdf),
    # ("Docling", extract_docling),
]

# ── Matching Logic ───────────────────────────────────────────────────────────
def count_term(text, raw_text, label):
    count = 0
    start = 0
    llen = len(label)
    text_lower = text.lower()
    label_lower = label.lower()
    
    while True:
        pos = text_lower.find(label_lower, start)
        if pos == -1: break
        
        # Boundary check
        before_ok = (pos == 0 or not text_lower[pos-1].isalnum())
        after_ok = (pos + llen >= len(text_lower) or not text_lower[pos+llen].isalnum())
        
        if before_ok and after_ok:
            count += 1
        start = pos + 1
    return count

def score_text(raw_text, term_metadata, all_labels):
    found_terms = []
    principle_scores = defaultdict(int)
    text_lower = raw_text.lower()
    
    for label in all_labels:
        count = count_term(text_lower, raw_text, label)
        if count > 0:
            meta = term_metadata[label]
            found_terms.append({
                "term": label, "count": count,
                "principle": meta["principle"], "source": meta["source"]
            })
            principle_scores[meta["principle"]] += count
            
    return found_terms, dict(principle_scores)

def load_ontology():
    if not os.path.exists(ONTOLOGY_FILE):
        raise FileNotFoundError(f"Ontology file {ONTOLOGY_FILE} not found. Run pipeline_1 first.")
    
    with open(ONTOLOGY_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    term_metadata = {}
    for p, content in data.items():
        for n in content.get('sub_concepts', []):
            term_metadata[n['label'].lower()] = {"principle": p, "source": n.get('source', 'AGROVOC')}
            
    return term_metadata, sorted(term_metadata.keys(), key=len, reverse=True)

# ── Main Pipeline ────────────────────────────────────────────────────────────
def run_processing():
    print("=== Phase 2: Processing Frameworks (Extraction & Matching) ===")
    term_metadata, all_labels = load_ontology()
    
    framework_files = [f for f in os.listdir(FRAMEWORKS_DIR) if f.lower().endswith('.pdf')]
    print(f"Found {len(framework_files)} frameworks to analyze.")
    
    best_results = {}
    matrix_data = []
    comparison_data = []
    
    for filename in sorted(framework_files):
        fw_name = filename.replace(".pdf", "")
        fpath = os.path.join(FRAMEWORKS_DIR, filename)
        print(f"Processing: {fw_name}")
        
        backend_options = {}
        for b_name, extractor in BACKENDS:
            t0 = time.time()
            text, err = extractor(fpath)
            dt = time.time() - t0
            
            if err:
                print(f"  {b_name}: Error - {err[:50]}")
                continue
                
            found, p_scores = score_text(text, term_metadata, all_labels)
            backend_options[b_name] = {
                "text": text, "found": found, "p_scores": p_scores, "chars": len(text), "time": dt
            }
            comparison_data.append({
                "Framework": fw_name, "Backend": b_name, "UniqueTerms": len(found), "Chars": len(text), "Time_s": round(dt, 2)
            })

        if not backend_options:
            print(f"  !! No successful extraction for {fw_name}")
            continue
            
        # Select best backend based on unique terms found
        best_name = max(backend_options.keys(), key=lambda b: (len(backend_options[b]["found"]), backend_options[b]["chars"]))
        best = backend_options[best_name]
        print(f"  >> Best: {best_name} ({len(best['found'])} terms)")
        
        best_results[fw_name] = {
            "best_backend": best_name,
            "terms_found": best["found"],
            "principle_scores": best["p_scores"]
        }
        
        row = {"Framework": fw_name, "BestBackend": best_name}
        row.update({f"P_{p}": s for p, s in best["p_scores"].items()})
        matrix_data.append(row)

    # Save outputs
    with open(OUTPUT_TERMS_JSON, 'w', encoding='utf-8') as f:
        json.dump(best_results, f, indent=4)
        
    pd.DataFrame(matrix_data).fillna(0).to_csv(OUTPUT_MATRIX_CSV, index=False)
    pd.DataFrame(comparison_data).to_csv(BACKEND_REPORT_CSV, index=False)
    
    print(f"\nProcessing complete. Matrix saved to {OUTPUT_MATRIX_CSV}")

if __name__ == "__main__":
    run_processing()
