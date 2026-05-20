import fitz  # PyMuPDF
import os
import json
import re

WOCAT_DIR = r"principles_indicators\offline_storage\wocat\media_library"
OUTPUT_FILE = "principles_indicators/wocat_extracted_indicators.json"

# Keywords for "Practices" (Technologies)
PRACTICE_KEYWORDS = [
    "Stone bunds", "Mulching", "Contour", "Terrace", "Agroforestry", 
    "Conservation agriculture", "Cover crop", "Irrigation", "Manure", 
    "Compost", "Windbreak", "Check dam", "Gully", "Intercropping"
]

# Keywords for "Indicators/Criteria" (Methodological)
INDICATOR_KEYWORDS = [
    "Social capital", "Tenure", "Gender", "Participation", "Labour", 
    "Income", "Food security", "Biodiversity", "Soil organic matter", 
    "Erosion", "Water quality", "Yield", "Cost", "Efficiency"
]

def extract_from_pdf(filepath):
    print(f"Extracting from {os.path.basename(filepath)}...")
    text = ""
    try:
        doc = fitz.open(filepath)
        # Just extract first 50 pages to be efficient
        for page in doc[:50]:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return text

def process_wocat_library():
    all_practices = set()
    all_indicators = set()
    
    files = [f for f in os.listdir(WOCAT_DIR) if f.endswith('.pdf')]
    
    for filename in files:
        filepath = os.path.join(WOCAT_DIR, filename)
        content = extract_from_pdf(filepath)
        
        # 1. Extract "Practices" (usually titles or list items)
        # Heuristic: Find lines that match practice keywords
        for p in PRACTICE_KEYWORDS:
            if p.lower() in content.lower():
                # Find the sentence containing the keyword
                matches = re.findall(r'([^.!?]*' + re.escape(p) + r'[^.!?]*[.!?])', content, re.IGNORECASE)
                for m in matches[:10]: # Limit to 10
                    all_practices.add(m.strip())
        
        # 2. Extract "Indicators" (Questions or Criteria)
        for i in INDICATOR_KEYWORDS:
            if i.lower() in content.lower():
                matches = re.findall(r'([^.!?]*' + re.escape(i) + r'[^.!?]*[.!?])', content, re.IGNORECASE)
                for m in matches[:10]:
                    all_indicators.add(m.strip())

    result = {
        "WOCAT_Technologies_Practices": sorted(list(all_practices)),
        "WOCAT_Social_Environmental_Indicators": sorted(list(all_indicators))
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4)
    
    print(f"\nExtraction Complete.")
    print(f"Total Practices: {len(all_practices)}")
    print(f"Total Indicators: {len(all_indicators)}")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_wocat_library()
