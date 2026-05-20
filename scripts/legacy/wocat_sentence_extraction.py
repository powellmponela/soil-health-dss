import os
import json
import re
import fitz  # PyMuPDF

MEDIA_LIBRARY = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\media_library"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\all_sentences.json"

def split_into_sentences(text):
    # Basic sentence splitter using regex
    # Looks for . ! ? followed by space and uppercase letter
    # Also handles some abbreviations like e.g., i.e.
    text = text.replace('\n', ' ').replace('\r', ' ')
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 10] # Filter out very short noise

def clean_sentence(s):
    # Remove non-printable characters and extra whitespace
    s = re.sub(r'[^\x20-\x7E]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def process_pdfs():
    print("=== WOCAT Sentence Extraction Start ===")
    all_data = []
    
    files = [f for f in os.listdir(MEDIA_LIBRARY) if f.lower().endswith('.pdf')]
    
    for filename in sorted(files):
        fpath = os.path.join(MEDIA_LIBRARY, filename)
        print(f"  Processing: {filename}")
        
        try:
            doc = fitz.open(fpath)
            is_huge = os.path.getsize(fpath) > 100 * 1024 * 1024
            
            for i, page in enumerate(doc):
                if is_huge and i > 1000: # Limit huge files to first 1000 pages for safety
                    print(f"    Truncating huge file at 1000 pages.")
                    break
                    
                text = page.get_text()
                if not text.strip():
                    continue
                    
                sentences = split_into_sentences(text)
                for s in sentences:
                    clean_s = clean_sentence(s)
                    if clean_s:
                        all_data.append({
                            "sentence": clean_s,
                            "source": filename,
                            "page": i + 1
                        })
            doc.close()
        except Exception as e:
            print(f"    Error processing {filename}: {e}")
            
        print(f"    Current total sentences: {len(all_data)}")

    # Save to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4)
        
    print(f"\nExtraction complete. Total sentences found: {len(all_data)}")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_pdfs()
