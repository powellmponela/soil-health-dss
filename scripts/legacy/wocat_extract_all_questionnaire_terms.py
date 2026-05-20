import fitz
import os
import re
import json

MEDIA_LIBRARY = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\media_library"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\raw_questionnaire_terms.json"

# Focus on the core questionnaires first
QUESTIONNAIRES = [
    "Questionnaire_on_SLM_Technologies_-_English_FINAL.pdf",
    "QA_Core_EN__35mYmGh.pdf",
    "WOCAT_Tenure_Module_final_draft_questionnaire_14.10.2022_mit_Wasserzeichen.pdf",
    "Inventory_QA_E.pdf",
    "Inventory_QT_E2_tB1AayL.pdf"
]

def clean_term(text):
    # Remove checkbox/radio symbols
    text = text.replace('', '').replace('', '').replace('', '').strip()
    # Remove "Specify:", "Remarks:", etc.
    text = re.sub(r'\(?specify\)?[:\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Remarks[:\s]*', '', text, flags=re.IGNORECASE)
    # Remove trailing dots
    text = text.strip('. ')
    return text

def extract_from_pdf(filename):
    fpath = os.path.join(MEDIA_LIBRARY, filename)
    print(f"Extracting from: {filename}")
    terms = []
    try:
        doc = fitz.open(fpath)
        for page in doc:
            text = page.get_text()
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                # If it starts with a symbol or looks like a categorical option
                if '' in line or '' in line or re.match(r'^[A-Z][a-z]+ [a-z]+', line):
                    cleaned = clean_term(line)
                    if cleaned and len(cleaned) > 3 and len(cleaned) < 100:
                        terms.append(cleaned)
        doc.close()
    except Exception as e:
        print(f"Error: {e}")
    return terms

def main():
    all_raw_terms = []
    for q in QUESTIONNAIRES:
        if os.path.exists(os.path.join(MEDIA_LIBRARY, q)):
            all_raw_terms.extend(extract_from_pdf(q))
            
    # Deduplicate
    unique_terms = sorted(list(set(all_raw_terms)))
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique_terms, f, indent=4)
        
    print(f"Extracted {len(unique_terms)} raw terms from questionnaires.")

if __name__ == "__main__":
    main()
