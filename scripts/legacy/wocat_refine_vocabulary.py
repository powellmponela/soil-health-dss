import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"

REMOVE_TERMS = [
    "About the WOCAT documentation of SLM practices",
    "Data captured through WOCAT questionnaires will be entered",
    "Data stored in the WOCAT database are open access",
    "Declaration on sustainability of the described Technology",
    "Detailed description of the Approach",
    "Description of an SLM Technology",
    "Describes why the Technology was introduced",
    "Describes why the Technology was adopted in the first place"
]

KEEP_TERMS = [
    "participate in the group discussion",
    "Annual budget"
]

def refine_term(term):
    # Specific split for Communal ownership
    if "Communal ownership:" in term:
        return ["Communal ownership", "property rights"]
    # Specific split for Compost production pits
    if "Compost production pits;" in term:
        return ["Compost production pits", "reshaping of surface"]
    # General cleaning of colon/semicolon suffixes
    if ":" in term and len(term.split(":")[0]) > 3:
        return [term.split(":")[0].strip()]
    if ";" in term and len(term.split(";")[0]) > 3:
        return [term.split(";")[0].strip()]
    return [term]

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    raw_practices = data["Practices_and_Indicators"]
    refined_practices = []
    
    for t in raw_practices:
        # Check removals
        if any(r in t for r in REMOVE_TERMS) and not any(k in t for k in KEEP_TERMS):
            continue
            
        # Apply specific splits and refinements
        sub_terms = refine_term(t)
        for st in sub_terms:
            st = st.strip('. ,:;')
            if st and len(st) > 2:
                refined_practices.append(st)
                
    # Ensure KEEP_TERMS are present
    for k in KEEP_TERMS:
        if k not in refined_practices:
            refined_practices.append(k)
            
    # Deduplicate and sort
    refined_practices = sorted(list(set(refined_practices)))
    
    data["Practices_and_Indicators"] = refined_practices
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Refined list to {len(refined_practices)} practices/indicators.")

if __name__ == "__main__":
    main()
