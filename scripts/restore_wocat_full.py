import json
import os

# Paths
WOCAT_TERMS = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\terms.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\wocat_ontology_compact.json"

# Relevance Logic (from pipeline_1)
CONTEXT_MAP = {
    "13. Participation": ["participation", "stakeholder", "community", "governance", "collective", "empowerment", "inclusive", "decision", "farmer", "producer", "association", "organization"],
    "10. Fairness": ["fair", "equity", "equitable", "justice", "rights", "poverty", "gender", "labour", "employment", "wage", "decent", "protection", "social"],
    "8. Co-creation of Knowledge": ["knowledge", "learning", "education", "research", "farmer", "indigenous", "traditional", "wisdom", "sharing", "extension", "participatory"],
    "9. Social Values & Diets": ["diet", "nutrition", "culture", "cultural", "food system", "healthy", "consumption", "heritage", "traditional", "values"],
    "11. Connectivity": ["market", "network", "trade", "value chain", "consumer", "producer", "connection", "linkage", "transparency", "short chain"],
    "12. Land & Natural Resource Governance": ["land", "tenure", "property", "reform", "common", "policy", "governance", "resource", "rights"],
    "7. Economic Diversification": ["income", "livelihood", "diversification", "employment", "entrepreneurship", "off-farm", "on-farm", "rural", "value addition"],
    "1. Recycling": ["recycling", "waste", "biomass", "nutrient", "circular", "reuse", "recovery", "compost", "water", "wastewater", "manure", "mulch", "biochar", "vermicompost", "residue", "urine", "dung"],
    "6. Synergy": ["synergy", "integration", "integrated", "agroecological", "agroecology", "redesign", "ecological", "intercropping", "mixed", "agroforestry", "intercrop", "agroforest"],
    "5. Biodiversity": ["biodiversity", "species", "diversity", "nature", "conservation", "genetic", "wildlife", "variety", "agrobiodiversity"],
    "3. Soil Health": ["soil", "fertility", "organic", "microbial", "structure", "erosion", "conservation", "health", "terrace", "bund", "tillage", "cover crop", "mulch"],
    "4. Animal Health": ["animal welfare", "livestock health", "veterinary services", "resilient breeds", "health", "disease"],
    "2. Input Reduction": ["reduction", "efficiency", "pesticide", "fertilizer", "biological", "input", "sustainable", "organic", "tillage", "irrigation", "drip", "low-input", "no-till", "minimum-till"]
}

def is_relevant(label, principle):
    if not label: return False
    label_lower = label.lower()
    if principle in CONTEXT_MAP:
        return any(k in label_lower for k in CONTEXT_MAP[principle])
    return False

def main():
    if not os.path.exists(WOCAT_TERMS):
        print("Error: terms.json not found.")
        return

    with open(WOCAT_TERMS, "r", encoding="utf-8") as f:
        terms = json.load(f)

    wocat_data = {p: {"key_terms": [], "indicators": []} for p in CONTEXT_MAP.keys()}
    total_found = 0

    for item in terms:
        label = item.get("label")
        uri = item.get("uri")
        if not label: continue

        matched = False
        for p in CONTEXT_MAP.keys():
            if is_relevant(label, p):
                wocat_data[p]["indicators"].append({
                    "label": label,
                    "source": "WOCAT",
                    "uri": uri
                })
                total_found += 1
                matched = True
        
        # If no match, put in a general category or discard? 
        # For restoration, we keep only relevant ones to match previous state.
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(wocat_data, f, indent=4)
    
    print(f"Restored WOCAT: {total_found} indicators -> {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
