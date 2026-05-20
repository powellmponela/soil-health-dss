import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\raw_questionnaire_terms.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\cleaned_questionnaire_terms.json"

STOP_PHRASES = [
    r"^choose from", r"^select one", r"^go to", r"^if yes", r"^if no", r"^tick ",
    r"^one answer", r"^maximal ", r"^for definitions", r"^give name", r"^date of",
    r"^name of", r"^contact ", r"^address ", r"^first name", r"^last name",
    r"^remarks", r"^specify", r"^remarks", r"^explanation", r"^supported file",
    r"^please read", r"^fill in", r"^summarize", r"^provide ", r"^indicate ",
    r"^how to ", r"^was ", r"^were ", r"^did ", r"^does ", r"^do ", r"^is ", r"^are ",
    r"^which ", r"^what ", r"^who ", r"^where ", r"^when ", r"^why ",
    r"^yes$", r"^no$", r"^maybe$", r"^not applicable$", r"^other$", r"^specify$"
]

def is_stop_word(term):
    term = term.lower().strip()
    # Remove if just dots or special characters
    if re.match(r'^[.\s\u2026\u00b7\u2022\uf0d8\uf0b0\uf0e0\uf0b1\u2610]+$', term):
        return True
    # Remove if too short (unless it's a known metric like pH)
    if len(term) < 3 and term.lower() != 'ph':
        return True
    # Remove based on patterns
    for pattern in STOP_PHRASES:
        if re.search(pattern, term):
            return True
    return False

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        terms = json.load(f)
        
    cleaned = []
    for t in terms:
        if not is_stop_word(t):
            # Basic cleaning of the term itself
            t = re.sub(r'\(?specify\)?[:\s]*', '', t, flags=re.IGNORECASE)
            t = t.strip('. :; \u2026')
            if t:
                cleaned.append(t)
                
    # Deduplicate
    cleaned = sorted(list(set(cleaned)))
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, indent=4)
        
    print(f"Cleaned {len(terms)} terms down to {len(cleaned)} high-signal terms.")

if __name__ == "__main__":
    main()
