import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"

PURGE_STARTS_WITH = [
    r"^is ", r"^name of", r"^level of", r"^if ", r"^how can", r"^state if", 
    r"^the ", r"^what ", r"^who ", r"^how ", r"^to ", r"^as part of", 
    r"^assessment of", r"^its ", r"^their ", r"^all ", r"^also ", r"^and "
]

PURGE_EXACT = [
    "choose one or two", "type of approach", "yes                no", 
    "no      yes", "none", "taken", "increased", "reduced", "decreased",
    "its impacts", "and", "even", "the", "their", "to"
]

PURGE_SUBSTRINGS = [
    "incr.        decreased", "incr.        reduced", "increased        decreased",
    "increased        reduced", "other existing documentation", 
    "other gradual climate change", "other measures", "other purpose",
    "other \u2026\u2026\u2026\u2026\u2026  enabling", "ies   in which the"
]

QUALITATIVE_SCALES = [
    r"^slightly positive", r"^very negative", r"^very positive", r"^negative", r"^positive"
]

def clean_term(term):
    term_low = term.lower().strip()
    if term_low in PURGE_EXACT:
        return None
    for sub in PURGE_SUBSTRINGS:
        if sub in term_low:
            return None
    for pattern in PURGE_STARTS_WITH + QUALITATIVE_SCALES:
        if re.search(pattern, term_low):
            return None
    # Strip footnotes
    term = re.sub(r'(\w+)\d+$', r'\1', term).strip()
    return term

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    raw_practices = data["Practices_and_Indicators"]
    final_practices = []
    
    for t in raw_practices:
        cleaned = clean_term(t)
        if cleaned:
            if len(cleaned) > 2:
                final_practices.append(cleaned)
                
    final_practices = sorted(list(set(final_practices)))
    data["Practices_and_Indicators"] = final_practices
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Final Purge complete. Remaining high-signal terms: {len(final_practices)}")

if __name__ == "__main__":
    main()
