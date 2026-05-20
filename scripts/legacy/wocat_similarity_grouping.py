import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\wocat_similarity_groups.json"

CLUSTERS = {
    "Soil & Erosion": ["soil", "erosion", "fertility", "compaction", "topsoil", "organic matter", "salinity", "acidity", "degradation", "sheet erosion", "interrill erosion", "siltation"],
    "Water & Hydrology": ["water", "hydrology", "irrigation", "rainfall", "groundwater", "aquifer", "runoff", "flooding", "drainage", "water harvesting"],
    "Trees & Forestry": ["tree", "forest", "wood", "nursery", "timber", "agroforestry", "species", "acacia", "eucalyptus", "terminalia", "bamboo"],
    "Crops & Agronomy": ["crop", "tillage", "rotation", "varieties", "seed", "maize", "rice", "wheat", "intercropping", "relay cropping", "cover cropping"],
    "Livestock & Grazing": ["livestock", "animal", "grazing", "pasture", "fodder", "stall feeding", "zero grazing", "herd"],
    "Structural Measures": ["terrace", "bund", "check dam", "gabion", "diversion", "channel", "stables"],
    "Land Rights & Governance": ["tenure", "rights", "ownership", "legal", "statutory", "customary", "administration", "land use", "governance", "dispute", "conflict"],
    "Social & Household": ["women", "gender", "youth", "widowed", "family", "household", "literacy", "leadership", "community", "social"],
    "Economic & Resources": ["budget", "costs", "market", "income", "credit", "financial", "production", "wealth", "resource", "specialist", "technical adviser"]
}

def map_term_to_cluster(term):
    term_low = term.lower()
    matched = []
    for cluster, keywords in CLUSTERS.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', term_low) for kw in keywords):
            matched.append(cluster)
    return matched

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    terms = data["Practices_and_Indicators"]
    grouped = {c: [] for c in CLUSTERS.keys()}
    grouped["Miscellaneous"] = []
    
    for t in terms:
        matched_clusters = map_term_to_cluster(t)
        if matched_clusters:
            for c in matched_clusters:
                grouped[c].append(t)
        else:
            grouped["Miscellaneous"].append(t)
            
    # Sort and deduplicate
    for c in grouped:
        grouped[c] = sorted(list(set(grouped[c])))
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(grouped, f, indent=4)
        
    print(f"Similarity grouping complete. Created {len(CLUSTERS)} technical clusters.")
    for c, tlist in grouped.items():
        print(f" - {c}: {len(tlist)} terms")

if __name__ == "__main__":
    main()
