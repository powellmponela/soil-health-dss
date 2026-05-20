import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"

QUESTION_FLATTEN_PATTERNS = [
    (r"^[Hh]as (.*) changed due to (.*)\??", r"\1 change"),
    (r"^[Hh]as (.*) increased\??", r"\1 increase"),
    (r"^[Hh]ave (.*) been established or strengthened\??", r"\1 strengthening"),
    (r"^[Hh]as the (.*) been modified recently to adapt to (.*)\??", r"adaptation to \2"),
    (r"^[Gg]eneral information regarding (.*)", r"\1"),
    (r"^[Gg]oal of the (.*)", r"\1 goal")
]

STOP_PHRASES = [
    r"^further specification", r"^general comments", r"^general regarding",
    r"^give further", r"^good photos are", r"^help us to improve",
    r"^indicate ", r"^summarize", r"^provide ", r"^fill in", r"^how to",
    r"^date and", r"^filename of"
]

def flatten_more(term):
    term_clean = term.strip()
    for pattern, replacement in QUESTION_FLATTEN_PATTERNS:
        if re.search(pattern, term_clean, re.IGNORECASE):
            flattened = re.sub(pattern, replacement, term_clean, flags=re.IGNORECASE).strip()
            if flattened and len(flattened) > 2:
                return flattened
    return term_clean

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    raw_practices = data["Practices_and_Indicators"]
    refined_practices = []
    
    for t in raw_practices:
        # 1. Skip stop phrases
        if any(re.search(p, t.lower()) for p in STOP_PHRASES):
            continue
            
        # 2. Flatten specific "Has..." and "Goal..." patterns
        t = flatten_more(t)
        
        # 3. Clean Colon Splits (Keep prefix)
        if ":" in t:
            t = t.split(":")[0].strip()
        
        # 4. Final Cleanup
        t = t.strip('. ,:; \u2026')
        if t and len(t) > 2 and not t.lower() in ['yes', 'no', 'other', 'specify', 'general information']:
            refined_practices.append(t)
                
    # Deduplicate and sort
    refined_practices = sorted(list(set(refined_practices)))
    
    data["Practices_and_Indicators"] = refined_practices
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Deep flattening complete. Remaining terms: {len(refined_practices)}")

if __name__ == "__main__":
    main()
