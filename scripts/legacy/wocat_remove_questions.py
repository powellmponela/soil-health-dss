import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"

QUESTION_WORDS = [
    r"^is ", r"^are ", r"^do ", r"^does ", r"^how ", r"^what ", r"^which ", r"^who ", 
    r"^when ", r"^why ", r"^was ", r"^were ", r"^can ", r"^could ", r"^should ", r"^has "
]

def is_question(term):
    term = term.lower().strip()
    # Ends with question mark
    if term.endswith('?'):
        return True
    # Starts with question word
    for pattern in QUESTION_WORDS:
        if re.search(pattern, term):
            return True
    return False

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    raw_practices = data["Practices_and_Indicators"]
    refined_practices = []
    
    for t in raw_practices:
        if not is_question(t):
            refined_practices.append(t)
                
    # Deduplicate and sort
    refined_practices = sorted(list(set(refined_practices)))
    
    data["Practices_and_Indicators"] = refined_practices
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Removed questions. Remaining terms: {len(refined_practices)}")

if __name__ == "__main__":
    main()
