import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\raw_questionnaire_terms.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"

# Patterns to extract the core noun phrase from questions
QUESTION_PATTERNS = [
    (r"^[Ii]s (.*) practiced\??", r"\1"),
    (r"^[Ii]s (.*) practised\??", r"\1"),
    (r"^[Ii]s (.*) a problem\??", r"\1"),
    (r"^[Dd]o (.*) have access to (.*)\??", r"\2"),
    (r"^[Dd]o (.*) enjoy (.*)\??", r"\2"),
    (r"^[Dd]o (.*) (.*)\??", r"\2"),
    (r"^[Dd]oes (.*) (.*)\??", r"\2"),
    (r"^[Ww]hat is (.*)\??", r"\1"),
    (r"^[Ww]hich (.*)\??", r"\1"),
    (r"^[Aa]re (.*) normally resolved\??", r"\1"),
    (r"^[Aa]re (.*) (.*)\??", r"\1")
]

STOP_PHRASES = [
    r"^choose from", r"^select one", r"^go to", r"^if yes", r"^if no", r"^tick ",
    r"^one answer", r"^maximal ", r"^for definitions", r"^give name", r"^date of",
    r"^address ", r"^first name", r"^last name", r"^remarks", r"^explanation", 
    r"^supported file", r"^please read", r"^fill in", r"^summarize", r"^provide ", 
    r"^indicate ", r"^how to ", r"^was ", r"^were ", r"^did ", r"^does ",
    r"^the licensor", r"^supported file types", r"^filename of"
]

METRIC_PATTERNS = [
    r'\d+', r' ha$', r' mm$', r' m a\.s\.l', r'\%', r' USD', r'pH'
]

def flatten_question(term):
    term_clean = term.strip()
    for pattern, replacement in QUESTION_PATTERNS:
        if re.search(pattern, term_clean, re.IGNORECASE):
            flattened = re.sub(pattern, replacement, term_clean, flags=re.IGNORECASE).strip()
            if flattened and len(flattened) > 2:
                return flattened
    return term_clean

def is_metric(term):
    for pattern in METRIC_PATTERNS:
        if re.search(pattern, term):
            return True
    return False

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        terms = json.load(f)
        
    final_practices = []
    final_metrics = []
    
    for t in terms:
        # 1. Skip dotted lines
        if re.match(r'^[.\s\u2026\u00b7\u2022\uf0d8\uf0b0\uf0e0\uf0b1\u2610]+$', t):
            continue
            
        # 2. Skip stop phrases (unless it's a specific term like Annual budget)
        if any(re.search(p, t.lower()) for p in STOP_PHRASES) and "annual budget" not in t.lower():
            continue
            
        # 3. Handle Metrics
        if is_metric(t):
            final_metrics.append(t)
            continue
            
        # 4. Flatten Questions
        t = flatten_question(t)
        
        # 5. Clean Brackets
        t = re.sub(r'\(.*?\)', '', t).strip()
        t = re.sub(r'[A-Z][0-9]', '', t).strip()
        
        # 6. Specific splits for Communal ownership and Compost pits
        if "Communal ownership:" in t:
            final_practices.extend(["Communal ownership", "property rights"])
            continue
        if "Compost production pits;" in t:
            final_practices.extend(["Compost production pits", "reshaping of surface"])
            continue
            
        # 7. General Splits
        parts = re.split(r'\s\+\s|/|&| and |(?<=[a-z]),\s|(?<=[a-z]);\s', t)
        for p in parts:
            p = p.strip('. ,:; \u2026')
            if p and len(p) > 2 and not p.lower() in ['yes', 'no', 'other', 'specify']:
                final_practices.append(p)
                
    # Deduplicate and sort
    final_practices = sorted(list(set(final_practices)))
    final_metrics = sorted(list(set(final_metrics)))
    
    output_data = {
        "Practices_and_Indicators": final_practices,
        "Metrics_and_Scales": final_metrics
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Final Granular List: {len(final_practices)} practices, {len(final_metrics)} metrics.")

if __name__ == "__main__":
    main()
