import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\cleaned_questionnaire_terms.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"

METRIC_PATTERNS = [
    r'\d+', r' ha$', r' mm$', r' m a\.s\.l', r'\%', r' USD', r'pH'
]

def clean_brackets(text):
    # Remove everything in parentheses
    text = re.sub(r'\(.*?\)', '', text).strip()
    # Remove specific WOCAT codes like (A2), (QT 3.1)
    text = re.sub(r'[A-Z][0-9]', '', text).strip()
    return text

def split_term(term):
    # Split by common separators
    parts = re.split(r'\s\+\s|/|&| and |(?<=[a-z]),\s', term)
    return [p.strip() for p in parts if p.strip()]

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
        if is_metric(t):
            final_metrics.append(t)
            continue
            
        # Clean brackets first
        t_clean = clean_brackets(t)
        
        # Split compounds
        parts = split_term(t_clean)
        for p in parts:
            p = p.strip('. ,')
            if p and len(p) > 2:
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
        
    print(f"Generated {len(final_practices)} practices/indicators and {len(final_metrics)} metrics.")

if __name__ == "__main__":
    main()
