import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"

PURGE_PATTERNS = [
    r"^data captured through", r"^data stored in", r"^declaration on", r"^describe ", 
    r"^describes ", r"^define ", r"^date$", r"^date and", r"^filename of",
    r"^accepting the conditions", r"^about the wocat", r"^the person who",
    r"^give name", r"^indicate ", r"^summarize", r"^provide ", r"^fill in",
    r"^supported file", r"^please read", r"^the following parameters",
    r"^the licensor", r"^supported file types", r"^lowest local administrative",
    r"^given the complexity", r"^it helps identify", r"^background information on",
    r"^discussion group", r"^compiler", r"^facilitator", r"^key informant",
    r"^first name", r"^last name", r"^contact details"
]

def should_purge(term):
    term_low = term.lower().strip()
    for pattern in PURGE_PATTERNS:
        if re.search(pattern, term_low):
            return True
    return False

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    raw_practices = data["Practices_and_Indicators"]
    purged_practices = []
    
    for t in raw_practices:
        if not should_purge(t):
            purged_practices.append(t)
                
    # Deduplicate and sort
    purged_practices = sorted(list(set(purged_practices)))
    
    data["Practices_and_Indicators"] = purged_practices
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Purged metadata. Remaining terms: {len(purged_practices)}")

if __name__ == "__main__":
    main()
