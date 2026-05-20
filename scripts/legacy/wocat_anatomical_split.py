import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"

def deep_clean(term):
    # 1. Remove all text in parentheses and brackets
    term = re.sub(r'\(.*?\)', '', term)
    term = re.sub(r'\[.*?\]', '', term)
    
    # 2. Specific split for Zero grazing / stall feeding
    if "Zero grazing" in term or "stall feeding" in term:
        # Split by / or +
        parts = re.split(r'/|\+', term)
        return [p.strip() for p in parts if p.strip()]
        
    # 3. Specific extraction for Resource persons
    if "Resource person" in term:
        # Extract specific roles mentioned
        roles = []
        if "land user" in term.lower(): roles.append("land user")
        if "slm specialist" in term.lower(): roles.append("SLM specialist")
        if "technical adviser" in term.lower(): roles.append("technical adviser")
        return roles
        
    # 4. Global Footnote/Number removal (e.g., wealth2, average1, groups3)
    # This matches a word followed by a digit at the end of a string or before punctuation
    term = re.sub(r'(\w+)\d+\b', r'\1', term).strip()
    
    # 5. General Splits (/, +)
    parts = re.split(r'/|\+', term)
    return [p.strip() for p in parts if p.strip()]

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    raw_practices = data["Practices_and_Indicators"]
    final_practices = []
    
    for t in raw_practices:
        sub_terms = deep_clean(t)
        for st in sub_terms:
            # Final polish: remove trailing dots/spaces
            st = st.strip('. ,:; \u2026')
            if st and len(st) > 2 and not st.lower() in ['other', 'n.a', 'specify']:
                final_practices.append(st)
                
    # Deduplicate and sort
    final_practices = sorted(list(set(final_practices)))
    
    data["Practices_and_Indicators"] = final_practices
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Anatomical Split complete. Final granular terms: {len(final_practices)}")

if __name__ == "__main__":
    main()
