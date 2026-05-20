import json
import os
import re

EXTRACTED_JSON = "principles_indicators/wocat_extracted_indicators.json"
CLEAN_PRACTICES = "principles_indicators/wocat_practices_clean.txt"
CLEAN_INDICATORS = "principles_indicators/wocat_indicators_clean.txt"

# Mapping logic for WOCAT groups to HLPE Principles
PRINCIPLE_MAP = {
    "Recycling": ["compost", "manure", "residue", "nutrient cycle", "waste management"],
    "Input Reduction": ["resource-saving", "low cost", "minimum tillage", "reduced tillage", "biopesticide"],
    "Soil Health": ["soil organic matter", "erosion", "bund", "terrace", "gully", "soil structure", "fertility"],
    "Animal Health": ["livestock", "manure", "fodder", "grazing", "pasture"],
    "Biodiversity": ["agroforestry", "intercropping", "native species", "habitats", "biodiversity"],
    "Synergy": ["integrated", "synergy", "multipurpose", "crop-livestock"],
    "Economic Viability": ["income", "cost", "benefit", "market", "enterprise", "profit"],
    "Social Values": ["traditional", "cultural", "aesthetics", "beliefs", "norms"],
    "Fairness": ["gender", "tenure", "equity", "land rights", "access"],
    "Participation": ["community-led", "participation", "training", "farmer", "mass mobilization"],
    "Land and Natural Resource Governance": ["policy", "institutional", "infrastructure", "governance"],
    "Resilience": ["climate change", "resilience", "adaptation", "drought", "water harvesting"],
    "Connectivity": ["dissemination", "extension", "uptake", "knowledge management"]
}

def clean_term(text):
    # Remove junk characters, bullets, and excessive whitespace
    text = re.sub(r'[\u0007\u2713\ufb01\uf0b7]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # If it's a long sentence, just try to extract the main noun phrase
    # (Simple heuristic: first 5-8 words)
    words = text.split(' ')
    if len(words) > 10:
        return ' '.join(words[:8])
    return text

def main():
    if not os.path.exists(EXTRACTED_JSON): return

    with open(EXTRACTED_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    raw_practices = data.get("WOCAT_Technologies_Practices", [])
    raw_indicators = data.get("WOCAT_Social_Environmental_Indicators", [])

    clean_p = set()
    for rp in raw_practices:
        cleaned = clean_term(rp)
        if cleaned and len(cleaned) > 3:
            clean_p.add(cleaned)

    clean_i = set()
    for ri in raw_indicators:
        cleaned = clean_term(ri)
        if cleaned and len(cleaned) > 3:
            clean_i.add(cleaned)

    # Save clean lists
    with open(CLEAN_PRACTICES, 'w', encoding='utf-8') as f:
        f.write("\n".join(sorted(list(clean_p))))
    
    with open(CLEAN_INDICATORS, 'w', encoding='utf-8') as f:
        f.write("\n".join(sorted(list(clean_i))))

    # Create Mapped Summary
    mapped_summary = {}
    for p_name in PRINCIPLE_MAP.keys():
        mapped_summary[p_name] = []

    all_terms = list(clean_p) + list(clean_i)
    for term in all_terms:
        for p_name, keywords in PRINCIPLE_MAP.items():
            for kw in keywords:
                if kw.lower() in term.lower():
                    mapped_summary[p_name].append(term)
                    break

    print("\n=== WOCAT HLPE Principle Mapping Summary ===")
    for p_name, terms in mapped_summary.items():
        print(f"{p_name}: {len(set(terms))} unique terms found")

    # Save mapping for future merge
    with open("principles_indicators/wocat_mapped_principles.json", 'w', encoding='utf-8') as f:
        json.dump(mapped_summary, f, indent=4)

if __name__ == "__main__":
    main()
