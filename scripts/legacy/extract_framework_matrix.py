# extract_framework_matrix.py
# Multi-backend PDF extraction pipeline for the Agroecological Ontology DSS.
# Runs all 4 PDF backends (PyMuPDF, pdfplumber, pypdf, Docling) on every framework PDF,
# compares term-match quality across backends, and writes the best-result to the main output.
# Now with refined acronym handling (UN, WHO) and noise filtering.

import json
import os
import re
import time
from collections import defaultdict
import pandas as pd

FRAMEWORKS_DIR     = "Frameworks"
ONTOLOGY_FILE      = "principles_indicators/Ontology_index.json"
OUTPUT_MATRIX_CSV  = "principles_indicators/framework_principle_matrix.csv"
OUTPUT_TERMS_JSON  = "principles_indicators/extracted_framework_terms.json"
COMPARE_CSV        = "principles_indicators/backend_comparison_report.csv"
COMPARE_TXT        = "principles_indicators/backend_comparison_report.txt"

# Terms that MUST match case (acronyms)
ACRONYMS = {"un", "who"}

# ── Word-boundary term counter ────────────────────────────────────────────────
def count_term_in_text(text, raw_text, label):
    # text is lowercase, raw_text is original case
    count = 0
    start = 0
    llen  = len(label)
    
    is_acronym = label.lower() in ACRONYMS
    
    while True:
        pos = text.find(label.lower(), start)
        if pos == -1:
            break
        
        # Word boundary check
        before_ok = (pos == 0 or not text[pos - 1].isalnum())
        after_ok  = (pos + llen >= len(text) or not text[pos + llen].isalnum())
        
        if before_ok and after_ok:
            if is_acronym:
                # For acronyms like UN or WHO, check if they are uppercase in the raw text
                orig_snippet = raw_text[pos : pos + llen]
                if orig_snippet == label.upper():
                    count += 1
            else:
                count += 1
        
        start = pos + 1
    return count

# ── Backend 1: PyMuPDF ────────────────────────────────────────────────────────
def extract_pymupdf(pdf_path):
    try:
        import fitz
        parts = []
        doc   = fitz.open(pdf_path)
        for page in doc:
            blocks = page.get_text("blocks", flags=fitz.TEXT_DEHYPHENATE)
            blocks = sorted(blocks, key=lambda b: (round(b[1] / 20), b[0]))
            for b in blocks:
                if b[6] == 0:
                    parts.append(b[4])
        doc.close()
        return " ".join(parts), None
    except Exception as e:
        return "", str(e)

# ── Backend 2: pdfplumber ─────────────────────────────────────────────────────
def extract_pdfplumber(pdf_path):
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text(x_tolerance=2, y_tolerance=2)
                if t:
                    parts.append(t)
        return " ".join(parts), None
    except Exception as e:
        return "", str(e)

# ── Backend 3: pypdf ──────────────────────────────────────────────────────────
def extract_pypdf(pdf_path):
    try:
        import pypdf
        text = ""
        with open(pdf_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + " "
        return text, None
    except Exception as e:
        return "", str(e)

# ── Backend 4: Docling ────────────────────────────────────────────────────────
def extract_docling(pdf_path):
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result    = converter.convert(pdf_path)
        text      = result.document.export_to_text()
        return text, None
    except Exception as e:
        return "", str(e)

# ── Score text against ontology ───────────────────────────────────────────────
def score_text(raw_text, all_labels, metadata_map):
    found_terms    = []
    principle_scores = defaultdict(int)
    source_counts    = defaultdict(int)

    if not raw_text.strip():
        return found_terms, dict(principle_scores), dict(source_counts)

    text_lower = raw_text.lower()

    for label in all_labels:
        count = count_term_in_text(text_lower, raw_text, label)
        if count > 0:
            meta = metadata_map[label]
            found_terms.append({
                "term": label, "count": count,
                "principle": meta["principle"], "source": meta["source"]
            })
            principle_scores[meta["principle"]] += count
            source_counts[meta["source"]]       += count

    return found_terms, dict(principle_scores), dict(source_counts)

# ── Ontology loader ───────────────────────────────────────────────────────────
def load_ontology():
    print("Loading Master Ontology...")
    with open(ONTOLOGY_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    term_metadata = {}

    def collect(nodes, principle):
        for n in nodes:
            label  = n['label'].strip()
            source = n.get('source', 'AGROVOC')
            if len(label) >= 2 and label.lower() not in term_metadata:
                term_metadata[label.lower()] = {"principle": principle, "source": source, "orig_label": label}
            if n.get('sub_concepts'):
                collect(n['sub_concepts'], principle)

    for p, content in data.items():
        collect(content.get('sub_concepts', []), p)

    all_labels = sorted(term_metadata.keys(), key=len, reverse=True)
    print(f"  {len(term_metadata):,} unique ontology terms loaded")
    return term_metadata, all_labels

# ── Main ──────────────────────────────────────────────────────────────────────
BACKENDS = [
    ("PyMuPDF",    extract_pymupdf),
    ("pdfplumber", extract_pdfplumber),
    ("pypdf",      extract_pypdf),
    ("Docling",    extract_docling),
]

def analyze_frameworks():
    metadata_map, all_labels = load_ontology()

    framework_files = sorted(
        f for f in os.listdir(FRAMEWORKS_DIR) if f.lower().endswith('.pdf')
    )
    print(f"\nRunning 4-backend extraction on {len(framework_files)} frameworks...\n")
    print(f"  {'Backend':<12} | {'Terms':>6} | {'Principles':>10} | {'Chars':>9} | {'Time(s)':>7}")
    print(f"  {'-'*12}-+-{'-'*6}-+-{'-'*10}-+-{'-'*9}-+-{'-'*7}")

    best_results = {}
    matrix_data  = []
    comparison_rows = []

    for filename in framework_files:
        fpath         = os.path.join(FRAMEWORKS_DIR, filename)
        framework_name = filename.replace(".pdf", "").replace(".PDF", "")
        print(f"\n[{framework_name}]")

        backend_scores = {}

        for backend_name, extractor in BACKENDS:
            t0   = time.time()
            raw_text, err = extractor(fpath)
            elapsed   = time.time() - t0

            if err:
                print(f"  {backend_name:<12} | ERROR: {err[:60]}")
                backend_scores[backend_name] = {
                    "terms_found": [], "principle_scores": {},
                    "source_counts": {}, "chars": 0, "time": elapsed, "error": err
                }
                comparison_rows.append({
                    "Framework": framework_name, "Backend": backend_name,
                    "Chars": 0, "UniqueTerms": 0, "TotalMatches": 0,
                    "PrinciplesCovered": 0, "Time_s": round(elapsed, 2), "Error": err[:80]
                })
                continue

            found, p_scores, s_counts = score_text(raw_text, all_labels, metadata_map)
            total_matches = sum(t['count'] for t in found)

            print(f"  {backend_name:<12} | {len(found):>6} | {len(p_scores):>10} | {len(raw_text):>9,} | {elapsed:>7.2f}s")

            backend_scores[backend_name] = {
                "terms_found": found,
                "principle_scores": p_scores,
                "source_counts": s_counts,
                "chars": len(raw_text),
                "time": elapsed,
                "error": None
            }
            comparison_rows.append({
                "Framework": framework_name, "Backend": backend_name,
                "Chars": len(raw_text), "UniqueTerms": len(found),
                "TotalMatches": total_matches, "PrinciplesCovered": len(p_scores),
                "Time_s": round(elapsed, 2), "Error": ""
            })

        best_name = max(
            backend_scores.keys(),
            key=lambda b: (len(backend_scores[b]["terms_found"]), backend_scores[b]["chars"])
        )
        best = backend_scores[best_name]
        print(f"  >> Best: {best_name}  ({len(best['terms_found'])} unique terms)")

        best_results[framework_name] = {
            "best_backend": best_name,
            "principle_scores": best["principle_scores"],
            "source_distribution": best["source_counts"],
            "terms_found": best["terms_found"],
            "backend_summary": {
                bn: {
                    "unique_terms": len(bs["terms_found"]),
                    "total_matches": sum(t["count"] for t in bs["terms_found"]),
                    "chars": bs["chars"],
                    "time_s": round(bs["time"], 2),
                    "error": bs.get("error")
                }
                for bn, bs in backend_scores.items()
            }
        }

        row = {"Framework": framework_name, "BestBackend": best_name}
        row.update({f"P_{p}": s for p, s in best["principle_scores"].items()})
        row.update({f"S_{s}": c for s, c in best["source_counts"].items()})
        matrix_data.append(row)

    with open(OUTPUT_TERMS_JSON, 'w', encoding='utf-8') as f:
        json.dump(best_results, f, indent=2, ensure_ascii=False)

    df_matrix = pd.DataFrame(matrix_data).fillna(0)
    df_matrix.to_csv(OUTPUT_MATRIX_CSV, index=False)

    df_cmp = pd.DataFrame(comparison_rows)
    df_cmp.to_csv(COMPARE_CSV, index=False)

    with open(COMPARE_TXT, 'w', encoding='utf-8') as f:
        f.write("=== PDF Backend Comparison Report ===\n")
        f.write(f"Frameworks: {len(framework_files)} | Backends: {len(BACKENDS)}\n\n")
        f.write(f"{'Framework':<30} {'Backend':<12} {'UniqueTerms':>12} {'TotalHits':>10} {'Chars':>10} {'Time':>7}\n")
        f.write("-" * 85 + "\n")
        for row in comparison_rows:
            f.write(
                f"{row['Framework']:<30} {row['Backend']:<12} "
                f"{row['UniqueTerms']:>12} {row['TotalMatches']:>10} "
                f"{row['Chars']:>10,} {row['Time_s']:>7.2f}s"
            )
            if row['Error']:
                f.write(f"  [ERR: {row['Error'][:40]}]")
            f.write("\n")

        f.write("\n=== Winner Tally (best backend per framework) ===\n")
        winner_tally = defaultdict(int)
        for fw, data in best_results.items():
            winner_tally[data["best_backend"]] += 1
        for name, cnt in sorted(winner_tally.items(), key=lambda x: -x[1]):
            f.write(f"  {name:<12}: {cnt} frameworks\n")

    print(f"\n{'='*60}")
    print("Multi-Source Extraction complete!")
    print(f"  Main results  : {OUTPUT_TERMS_JSON}")
    print(f"  Matrix CSV    : {OUTPUT_MATRIX_CSV}")
    print(f"  Compare CSV   : {COMPARE_CSV}")
    print(f"  Compare TXT   : {COMPARE_TXT}")

if __name__ == "__main__":
    analyze_frameworks()
