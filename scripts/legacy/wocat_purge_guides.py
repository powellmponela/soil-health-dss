import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"

PURGE_PATTERNS = [
    r"\.\.\.\.\.", r"\d+ years", r"question \d", r"years? ago", 
    r"max\. \d", r"per year", r"specify", r"indicat", r"summarize",
    r"average annual rainfall", r"implementing agencies", r"long term", r"short term"
]

GENERIC_WORDS = ["input", "high", "low", "total", "average", "other", "remarks", "details"]

def should_purge(term):
    term_low = term.lower().strip()
    # 1. Check patterns
    for p in PURGE_PATTERNS:
        if re.search(p, term_low):
            return True
    # 2. Check hyper-generic single words
    if term_low in GENERIC_WORDS:
        return True
    # 3. Check if it's just a number or year range
    if re.match(r'^[\d\s\-]+$', term_low):
        return True
    return False

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    raw_practices = data["Practices_and_Indicators"]
    refined_practices = []
    
    for t in raw_practices:
        if not should_purge(t):
            # Final trim of any remaining dots
            t = t.strip('. ,:; \u2026')
            if t and len(t) > 3: # Longer than 3 chars to catch 'input', 'high' etc
                refined_practices.append(t)
                
    # Deduplicate and sort
    refined_practices = sorted(list(set(refined_practices)))
    
    data["Practices_and_Indicators"] = refined_practices
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Purged guides. Remaining technical terms: {len(refined_practices)}")

if __name__ == "__main__":
    main()
