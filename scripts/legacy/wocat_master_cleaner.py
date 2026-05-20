import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\raw_questionnaire_terms.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"

PURGE_PHRASES = [
    r"^very negative", r"^very positive", r"^slightly negative", r"^slightly positive",
    r"^negative", r"^positive", r"^is ", r"^are ", r"^do ", r"^does ", r"^how ", 
    r"^what ", r"^which ", r"^who ", r"^when ", r"^why ", r"^name of", r"^level of",
    r"^if ", r"^how can", r"^state if", r"^the ", r"^to ", r"^as part of", 
    r"^assessment of", r"^its ", r"^their ", r"^all ", r"^also ", r"^and ",
    r"^choose ", r"^type of approach", r"^yes ", r"^no ", r"^none$", r"^taken$",
    r"^short term", r"^long term", r"^average annual rainfall", r"^implementing agencies",
    r"^tenure opportunities", r"^total cost", r"^usually one", r"^several answers",
    r"^data captured", r"^data stored", r"^declaration on", r"^describe", r"^defines?",
    r"^help us to improve", r"^indicate", r"^provide", r"^fill in", r"^summarize",
    r"^the next", r"^the following", r"ies in which the",
    r"weakened\s+strengthened", r"worsened\s+improved", r"yes\s+no", r"no\s+yes",
    r"^whether", r"^is a", r"^is a set of",
    r"qcat\.wocat\.net", r"^recurrent activities", r"^programme based", r"^project$",
    r"^origin and composition", r"^per technology area",
    # NEW PURGES FROM USER LIST
    r"^tick ", r"^only one answer", r"^one answer per question", r"^maximal \d",
    r"^for definitions", r"^questionnaire on", r"^refer to questions", r"^reference to",
    r"^references", r"^filename of", r"^first name", r"^explanation of terms",
    r"^diagnosis phase", r"^testing phase", r"^did the approach", r"^differentiate ",
    r"^during the discussion", r"^main aims", r"^main categories", r"^maintain confidentiality",
    r"^may require", r"^one or a", r"^only one tick", r"^researchable issues",
    r"^introduction to the questionnaire", r"^they also provide", r"^they are commonly",
    r"^use the slm measures", r"^changes due to", r"^comments", r"^description of",
    r"^detailed description", r"^for tropics", r"^for which", r"^general comments",
    r"^has land use changed", r"^has the technology", r"^have institutions",
    r"fields do landholders have", r"date of data collection"
]

GENERIC_WORDS = [
    "input", "high", "low", "total", "average", "other", "remarks", "details", 
    "yes", "no", "the", "and", "for", "their", "this", "that", "with", "from",
    "water", "land", "soil", "project", "improve", "heavy", "group", "groups",
    "good", "excess", "evaluation", "deep", "cover", "codes", "a little",
    "quality", "monitoring", "on average", "country", "date", "dates", "list",
    "exposure", "following"
]

def master_clean(term):
    # 1. Normalize Whitespace
    term = re.sub(r'\s+', ' ', term).strip()
    
    # 2. Strip parenthetical content
    term = re.sub(r'\(.*?\)', '', term).strip()
    term = re.sub(r'\[.*?\]', '', term).strip()
    
    term_low = term.lower().strip('. ,:; \u2026')
    
    # 3. Check for Resource Persons
    if "resource person" in term_low:
        roles = []
        if "land user" in term_low: roles.append("land user")
        if "slm specialist" in term_low: roles.append("SLM specialist")
        if "technical adviser" in term_low: roles.append("technical adviser")
        return roles
        
    # 4. Skip if matches purge phrases
    for pattern in PURGE_PHRASES:
        if re.search(pattern, term_low):
            return []
            
    # 5. Skip generic single words
    if term_low in GENERIC_WORDS:
        return []
        
    # 6. STRIP SUFFIXES AND PREFIXES
    term = re.sub(r'\s*\d+\s*$', '', term)
    term = re.sub(r'(\w+)\d+\b', r'\1', term)
    term = re.sub(r'^[a-z0-9][\.\)]\s*', '', term, flags=re.IGNORECASE)
    term = re.sub(r'^[•\-\*]\s*', '', term)
    
    # 7. Split by / , + and ,
    if "sheet and interrill erosion" in term_low:
        return ["sheet erosion", "interrill erosion"]
    if "small-scale" in term_low and "large-scale" in term_low:
        return ["small-scale", "medium-scale", "large-scale"]

    parts = re.split(r'/|\+|\s\&\s|\sund\s|(?<=[a-z]),\s| and ', term)
    
    cleaned_parts = []
    for p in parts:
        p = re.sub(r'\s+', ' ', p).strip('. ,:; \u2026')
        p_low = p.lower()
        if p and len(p) > 3 and not p_low in GENERIC_WORDS:
            # Check if it starts with a purge phrase after split
            is_stop = False
            for pattern in PURGE_PHRASES:
                if re.search(pattern, p_low):
                    is_stop = True
                    break
            if not is_stop:
                if ":" in p: p = p.split(":")[0].strip()
                # Remove if ends in fragment like (incl or similar
                p = re.sub(r'\(.*$', '', p).strip()
                if p and len(p) > 3 and not p.lower() in GENERIC_WORDS:
                    cleaned_parts.append(p)
            
    return cleaned_parts

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        terms = json.load(f)
        
    final_practices = []
    for t in terms:
        processed = master_clean(t)
        final_practices.extend(processed)
                
    final_practices = sorted(list(set(final_practices)))
    
    output_data = {
        "Practices_and_Indicators": final_practices,
        "Metrics_and_Scales": []
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Master Clean complete. Final technical terms: {len(final_practices)}")

if __name__ == "__main__":
    main()
