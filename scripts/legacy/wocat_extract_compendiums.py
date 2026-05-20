import fitz
import os
import re
import json

MEDIA_LIBRARY = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\media_library"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\compendium_practices.json"

COMPENDIUMS = [
    "SLM_Compendium_India_2024.pdf",
    "Best_Practices_South_AFrica.pdf",
    "Bhutan_catalogue_of_SLM_Technologies_and_Approaches.pdf",
    "Tajikistan_wocat-collection2011_eng_final.pdf",
    "SLM_technologies_approaches_Central_Asia.pdf",
    "Ethiocat_book_final.pdf",
    "SLM_BOOK_FINAL.pdf",
    "FINAL_SLM_Booklet_En.pdf"
]

def clean_name(name):
    # Remove leading numbers/dots
    name = re.sub(r'^\d+\.?\s*', '', name)
    # Remove dots and symbols used for TOC alignment
    name = re.sub(r'[\.]{2,}.*$', '', name)
    # Remove underscores
    name = name.replace('_', '').strip()
    # Remove (QT ...) or (QA ...)
    name = re.sub(r'\(Q[TA]\s+\w+\s+\d+\)', '', name)
    # Remove (Timing/ frequency: ...)
    name = re.sub(r'\(Timing/ frequency:.*\)', '', name)
    # Clean up whitespace
    name = re.sub(r'\s{2,}', ' ', name)
    # Remove trailing symbols
    name = name.strip('\u25a0- :')
    # Remove trailing page numbers
    name = re.sub(r'\s\d+$', '', name)
    return name.strip()

def is_practice_start(line):
    # Pattern 1: Numbered list item "27. Hillside"
    if re.match(r'^\d+\.\s+[A-Z]', line):
        return True
    # Pattern 2: WOCAT ID "(QT " or "(QA "
    if "(QT " in line or "(QA " in line:
        return True
    # Pattern 3: Explicit label "SLM technology:"
    if "SLM technology:" in line.lower() or "SLM approach:" in line.lower():
        return True
    return False

def process_compendium(filename):
    fpath = os.path.join(MEDIA_LIBRARY, filename)
    print(f"Processing Compendium: {filename}")
    practices = []
    
    try:
        doc = fitz.open(fpath)
        full_text_lines = []
        for i in range(min(40, len(doc))): # Increased range for long TOCs
            text = doc[i].get_text()
            full_text_lines.extend(text.split('\n'))
            
        current_practice = ""
        
        for idx, line in enumerate(full_text_lines):
            line = line.strip()
            if not line: continue
            
            if is_practice_start(line):
                # Save previous
                if current_practice:
                    name = clean_name(current_practice)
                    # Limit length to avoid paragraph merging
                    if name and 8 < len(name) < 150:
                        practices.append({"name": name, "source": filename, "type": "Practice"})
                
                # Start new
                current_practice = line
            elif current_practice:
                # Merge if:
                # 1. Current practice is short
                # 2. Next line is not too long
                # 3. Next line doesn't look like a new section
                if len(current_practice) < 100 and len(line) < 100 and "Table of" not in line:
                    current_practice += " " + line
                else:
                    # Finalize current and stop merging
                    name = clean_name(current_practice)
                    if name and 8 < len(name) < 150:
                        practices.append({"name": name, "source": filename, "type": "Practice"})
                    current_practice = ""
        
        if current_practice:
            name = clean_name(current_practice)
            if name and 8 < len(name) < 150:
                practices.append({"name": name, "source": filename, "type": "Practice"})

        doc.close()
    except Exception as e:
        print(f"    Error processing {filename}: {e}")
        
    return practices

def main():
    all_practices = []
    seen = set()
    
    for comp in COMPENDIUMS:
        if os.path.exists(os.path.join(MEDIA_LIBRARY, comp)):
            found = process_compendium(comp)
            for p in found:
                if p['name'].lower() not in seen:
                    all_practices.append(p)
                    seen.add(p['name'].lower())
                    
    all_practices.sort(key=lambda x: x['name'])
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_practices, f, indent=4)
        
    print(f"\nRefined merge complete. Found {len(all_practices)} practices.")
    print(f"Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
