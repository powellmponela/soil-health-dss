import json
import os

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\all_sentences.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\wocat_all_sentences.txt"

def main():
    if not os.path.exists(INPUT_FILE):
        print("Input file not found. Run wocat_sentence_extraction.py first.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} sentences.")
    
    # Filter out common noise if needed, but for "all words" we keep most
    # Let's at least remove very short fragments and duplicate sentences
    seen = set()
    clean_count = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for item in data:
            s = item['sentence'].strip()
            if not s:
                continue
                
            # Basic cleaning: remove lines that are just numbers or single words
            if len(s.split()) < 3:
                continue
                
            # Deduplicate
            if s.lower() not in seen:
                f.write(s + "\n")
                seen.add(s.lower())
                clean_count += 1
                
    print(f"Saved {clean_count} unique sentences to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
