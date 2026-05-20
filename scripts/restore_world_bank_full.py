import json
import os
import re

# Paths
WB_TERMS = r"c:\SOIL HEALTH\principles_indicators\offline_storage\world_bank\terms.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\world_bank\world_bank_ontology_compact.json"

# Relevance Logic (from pipeline_1)
FORBIDDEN_KEYWORDS = [
    "facility", "hospital", "medical", "anaesthesia", "surgery", "patient", "clinical",
    "fiat", "ice", "geological", "volcano", "crater", "oceanic", "benthopelagic",
    "bicycle", "currency", "devaluation", "post-anesthesia", "care unit", "rod",
    "driveway", "booth", "monsoon", "restaurant", "slum", "wildfire", "carbohydrate",
    "cation", "potassium", "haber-bosch", "biosolids", "bone meal",
    "economic recovery", "disaster recovery", "balance of payments", "balance of trade",
    "balance sheet", "balance organs", "customs duties", "customs unions", "blood groups",
    "adolescent fertility", "Goal 3", "Goal 6", "Goal 8", "Goal 9", "Goal 11", "Goal 14", "Goal 15",
    "semen", "preservation", "frozen", "sperm", "artificial insemination"
]

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

HIGH_NOISE = ["9. Social Values & Diets", "13. Participation", "10. Fairness", "7. Economic Diversification", "1. Recycling", "11. Connectivity"]

def is_relevant(label, principle):
    if not label or len(label) < 3: return False
    label_lower = label.lower()
    
    if any(k in label_lower for k in FORBIDDEN_KEYWORDS):
        return False
    
    if principle in CONTEXT_MAP:
        hits = sum(1 for k in CONTEXT_MAP[principle] if k in label_lower)
        threshold = 2 if principle in HIGH_NOISE else 1
        
        # Exact keyword match overrides threshold
        if hits == 1 and any(label_lower == k for k in CONTEXT_MAP[principle]):
            threshold = 1
            
        if hits < threshold:
            return False
            
    return True

def main():
    if not os.path.exists(WB_TERMS):
        print("Error: terms.json not found.")
        return

    with open(WB_TERMS, "r", encoding="utf-8") as f:
        terms = json.load(f)

    wb_data = {p: {"key_terms": [], "indicators": []} for p in CONTEXT_MAP.keys()}
    total_found = 0

    for item in terms:
        label = item.get("label")
        uri = item.get("uri")
        if not label: continue

        for p in CONTEXT_MAP.keys():
            if is_relevant(label, p):
                wb_data[p]["indicators"].append({
                    "label": label,
                    "source": "WORLD_BANK",
                    "uri": uri
                })
                total_found += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(wb_data, f, indent=4)
    
    print(f"Restored World Bank: {total_found} indicators -> {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
