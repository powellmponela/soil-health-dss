import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\compendium_practices.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_practices.json"

SEPARATORS = [
    r'\s*\u2022\s*',      # Bullet points
    r'\s*\u25a0\s*',      # Square bullets
    r'\s+combined with\s+',
    r'\s+and\s+',         # Use with caution
    r'\s+with\s+',
    r'\s*/\s*',
    r'\s*;\s*'
]

def split_practice(name):
    # Initial candidates
    candidates = [name]
    
    # Split by bullets first as they are strongest separators
    new_candidates = []
    for cand in candidates:
        parts = re.split(r' \u2022 | \u25a0 | ; ', cand)
        new_candidates.extend(parts)
    candidates = new_candidates
    
    # Split by "combined with"
    new_candidates = []
    for cand in candidates:
        parts = re.split(r' combined with ', cand, flags=re.IGNORECASE)
        new_candidates.extend(parts)
    candidates = new_candidates

    # Split by " and " / " with " but ONLY if the parts are long enough to be practices
    # and not just "Stone and Soil"
    final_list = []
    for cand in candidates:
        # Check for " and " or " / "
        if " and " in cand.lower() or " / " in cand:
            parts = re.split(r' and | / ', cand, flags=re.IGNORECASE)
            # Only split if both parts look like independent practices (e.g., > 10 chars)
            if all(len(p.strip()) > 10 for p in parts):
                final_list.extend(parts)
            else:
                final_list.append(cand)
        else:
            final_list.append(cand)
            
    return [p.strip() for p in final_list if len(p.strip()) > 5]

def clean_granular(name):
    # Remove "Agronomic measures", "Vegetative measures", etc. if they are prefixes
    prefixes = ["Agronomic measures", "Vegetative measures", "Structural measures", "Management measures", "SLM technology", "SLM approach"]
    for pref in prefixes:
        if name.lower().startswith(pref.lower()):
            name = re.sub(f"^{pref}", "", name, flags=re.IGNORECASE).strip(": ")
    
    # Remove locations in brackets
    name = re.sub(r'\(.*\)', '', name).strip()
    return name

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    granular_list = []
    seen = set()
    
    for item in data:
        raw_name = item['name']
        parts = split_practice(raw_name)
        
        for p in parts:
            clean_p = clean_granular(p)
            if clean_p and clean_p.lower() not in seen:
                granular_list.append({
                    "name": clean_p,
                    "original_compound": raw_name,
                    "source": item['source']
                })
                seen.add(clean_p.lower())
                
    granular_list.sort(key=lambda x: x['name'])
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(granular_list, f, indent=4)
        
    print(f"Split {len(data)} compound practices into {len(granular_list)} granular practices.")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
