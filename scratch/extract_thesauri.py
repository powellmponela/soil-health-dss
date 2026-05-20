import fitz  # PyMuPDF
import json
import os
import re

UNESCO_PDF = "principles_indicators/offline_storage/unesco_thesaurus/Unesco_thesaurus.pdf"
OECD_PDF = "principles_indicators/offline_storage/oecd_macrothesaurus/oecd_macrothesaurus.pdf"
OUTPUT_JSON = "principles_indicators/thesauri_extracted_terms.json"

# Heuristic Mapping for General Thesauri
MAPPING_RULES = {
    "Social Values and Diets": ["culture", "traditional", "beliefs", "norms", "values", "ethics", "religion", "diets", "nutrition", "food habits"],
    "Co-creation of Knowledge": ["indigenous knowledge", "traditional knowledge", "research", "scientific", "education", "literacy", "humanities"],
    "Participation": ["community", "participation", "social change", "empowerment", "civil society", "democracy"],
    "Fairness": ["equity", "equality", "gender", "poverty", "human rights", "justice", "labor", "employment"],
    "Economic Diversification": ["economy", "income", "market", "trade", "enterprise", "industry", "rural development"],
    "Land Governance": ["governance", "policy", "land law", "land reform", "administration", "public policy"]
}

def extract_terms_from_pdf(pdf_path, source_name):
    print(f"Processing {source_name}: {pdf_path}...")
    if not os.path.exists(pdf_path): return []
    
    extracted_data = []
    doc = fitz.open(pdf_path)
    
    # We only scan for words that look like 'Subject Headings' or 'Terms'
    # Typically capitalized at start or in bold (hard to detect in raw text, so we use length and capital filters)
    
    term_pattern = re.compile(r'^[A-Z][A-Z\s\-]{3,30}$') # Rough guess for capitalized terms
    
    # To speed up, we'll only process every 2nd page or look for specific indices if possible
    # But since we want "Indicators", we'll scan all but limit the search space
    
    page_count = 0
    for page in doc:
        text = page.get_text()
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # If it's a short, capitalized line, it's likely a term
            if 3 < len(line) < 40 and any(kw in line.lower() for kw in sum(MAPPING_RULES.values(), [])):
                # Map to Principle
                matched_principles = []
                for p, kws in MAPPING_RULES.items():
                    if any(kw in line.lower() for kw in kws):
                        matched_principles.append(p)
                
                if matched_principles:
                    extracted_data.append({
                        "label": line,
                        "source": source_name,
                        "principles": matched_principles
                    })
        
        page_count += 1
        if page_count % 50 == 0:
            print(f"  Scanned {page_count} pages...")
            if page_count > 1000: break # Safety limit for now
            
    doc.close()
    return extracted_data

def main():
    all_extracted = []
    
    # 1. UNESCO
    unesco_terms = extract_terms_from_pdf(UNESCO_PDF, "UNESCO")
    all_extracted.extend(unesco_terms)
    
    # 2. OECD
    oecd_terms = extract_terms_from_pdf(OECD_PDF, "OECD")
    all_extracted.extend(oecd_terms)
    
    # Deduplicate
    unique_data = {}
    for item in all_extracted:
        label = item['label'].lower()
        if label not in unique_data:
            unique_data[label] = item
    
    print(f"\nExtracted {len(unique_data)} unique terms from Thesauri.")
    
    # Group by Principle
    final_mapping = {}
    for item in unique_data.values():
        for p in item['principles']:
            if p not in final_mapping: final_mapping[p] = []
            final_mapping[p].append({
                "label": item['label'],
                "source": item['source']
            })
            
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(final_mapping, f, indent=4)

if __name__ == "__main__":
    main()
