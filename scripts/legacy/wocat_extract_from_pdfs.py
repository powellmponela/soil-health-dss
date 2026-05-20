import os
import json
import re
import fitz  # PyMuPDF
from collections import defaultdict

# Add the scripts directory to path to import pipeline_1
import sys
sys.path.append(r'c:\SOIL HEALTH\scripts')
from pipeline_1_build_ontology import is_relevant

MEDIA_LIBRARY = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\media_library"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\wocat_extracted_terms.json"

PRINCIPLES = [
    "Participation", "Fairness", "Co-creation of Knowledge", 
    "Social Values and Diets", "Connectivity", "Land Governance",
    "Economic Diversification", "Recycling", "Synergy", "Biodiversity",
    "Soil Health", "Animal Health", "Input Reduction"
]

# Regex patterns for WOCAT terms
PATTERNS = [
    re.compile(r"SLM technology:\s*(.*)", re.IGNORECASE),
    re.compile(r"SLM approach:\s*(.*)", re.IGNORECASE),
    re.compile(r"Common name of SLM Technology:\s*(.*)", re.IGNORECASE),
    re.compile(r"Local name:\s*(.*)", re.IGNORECASE),
    re.compile(r"Technology name:\s*(.*)", re.IGNORECASE)
]

def clean_term(term):
    # Remove page numbers, special characters like , etc.
    term = re.sub(r'\s*\d+$', '', term)  # Trailing numbers (often page numbers)
    term = term.encode('ascii', 'ignore').decode('ascii')  # Remove non-ascii
    term = term.replace('_', ' ').strip()
    # Remove common artifacts seen in OCR/Extraction
    term = re.sub(r'\s{2,}', ' ', term)
    return term

def extract_terms_from_pdf(pdf_path):
    filename = os.path.basename(pdf_path)
    print(f"  Extracting from: {filename}")
    terms_found = []
    
    try:
        doc = fitz.open(pdf_path)
        # For very large files, we might want to skip or limit, but fitz is usually fast.
        # However, for the 849MB file, let's be careful.
        is_huge = os.path.getsize(pdf_path) > 100 * 1024 * 1024
        
        for i, page in enumerate(doc):
            if is_huge and i > 500: # Limit huge files to first 500 pages for now
                print(f"    Truncating huge file at 500 pages.")
                break
                
            text = page.get_text()
            lines = text.split('\n')
            
            for line in lines:
                for pattern in PATTERNS:
                    match = pattern.search(line)
                    if match:
                        name = clean_term(match.group(1))
                        if name and len(name) > 5: # Avoid very short artifacts
                            # Map to principles
                            principles_for_term = []
                            for p in PRINCIPLES:
                                if is_relevant(name, p, threshold=1):
                                    principles_for_term.append(p)
                            
                            terms_found.append({
                                "term": name,
                                "principles": principles_for_term,
                                "uri": f"wocat:{filename.replace('.pdf', '')}_p{i}",
                                "source": "WOCAT_PDF"
                            })
        doc.close()
    except Exception as e:
        print(f"    Error processing {filename}: {e}")
        
    return terms_found

def main():
    print("=== WOCAT PDF Term Extraction Start ===")
    all_extracted_terms = []
    seen_names = set()
    
    files = [f for f in os.listdir(MEDIA_LIBRARY) if f.lower().endswith('.pdf')]
    
    for filename in sorted(files):
        fpath = os.path.join(MEDIA_LIBRARY, filename)
        terms = extract_terms_from_pdf(fpath)
        
        for t in terms:
            if t['term'].lower() not in seen_names:
                all_extracted_terms.append(t)
                seen_names.add(t['term'].lower())
    
    # Sort by name
    all_extracted_terms.sort(key=lambda x: x['term'])
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_extracted_terms, f, indent=4)
        
    print(f"\nExtraction complete. Found {len(all_extracted_terms)} unique terms.")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
