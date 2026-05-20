import os
import json
import re
from pypdf import PdfReader

pdf_dir = r'c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\media_library'
pdfs_to_process = [
    'SLM_Compendium_India_2024.pdf',
    'SLM_in_Practice_E_Final_low.pdf'
]

output_path = r'c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\qcat_terms.json'

keywords = {
    "Input Reduction": [
        "reduce fertilizer", "reduced fertilizer", "minimum tillage", "zero tillage",
        "pesticide reduction", "reduce input", "save water", "water efficiency",
        "drip irrigation", "integrated pest management", "IPM"
    ],
    "Recycling": [
        "crop residue", "compost", "manure", "mulch", "biomass", 
        "nutrient cycling", "organic fertilizer", "green manure"
    ]
}

extracted_terms = []
seen_terms = set()

def extract_slm_practices():
    for pdf_name in pdfs_to_process:
        pdf_path = os.path.join(pdf_dir, pdf_name)
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
            continue
            
        print(f"Processing {pdf_name}...")
        try:
            reader = PdfReader(pdf_path)
            # Read first 100 pages to save time and memory, as compendiums have practices early on
            max_pages = min(100, len(reader.pages))
            
            for i in range(max_pages):
                page = reader.pages[i]
                text = page.extract_text()
                if not text:
                    continue
                
                # Split text into sentences or short paragraphs
                sentences = re.split(r'(?<=[.!?]) +', text.replace('\n', ' '))
                
                for sentence in sentences:
                    sentence_lower = sentence.lower()
                    mapped_principles = []
                    
                    for principle, kws in keywords.items():
                        if any(kw in sentence_lower for kw in kws):
                            mapped_principles.append(principle)
                            
                    if mapped_principles:
                        # Clean up the sentence to be a concise indicator
                        clean_sentence = sentence.strip()
                        # Only take reasonably sized definitions (e.g., 20 to 150 chars)
                        if 20 < len(clean_sentence) < 150 and clean_sentence not in seen_terms:
                            extracted_terms.append({
                                "uri": f"wocat:pdf_{pdf_name[:10]}_{len(extracted_terms)}",
                                "label": clean_sentence,
                                "principles": list(set(mapped_principles)),
                                "source": "WOCAT_PDF"
                            })
                            seen_terms.add(clean_sentence)
        except Exception as e:
            print(f"Error processing {pdf_name}: {e}")

    print(f"\nExtracted {len(extracted_terms)} SLM definitions/indicators.")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_terms, f, indent=4)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    extract_slm_practices()
