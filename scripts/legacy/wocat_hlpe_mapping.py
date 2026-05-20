import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\granular_questionnaire_vocabulary.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\wocat_master_ontology.json"

PRINCIPLES = {
    "Recycling": ["manure", "compost", "nutrient", "biomass", "trash lines", "recycling", "residue"],
    "Input Reduction": ["integrated pest", "integrated soil fertility", "zero tillage", "minimum tillage", "organic fertilizers"],
    "Soil Health": ["soil", "erosion", "fertility", "compaction", "terraces", "bunds", "mulching", "tillage", "contour", "ripping", "digging", "salinity", "acidity"],
    "Animal Health": ["animal", "livestock", "grazing", "pasture", "fodder", "veterinary", "herd", "stall feeding"],
    "Biodiversity": ["diversity", "species", "tree", "forest", "varieties", "nursery", "seed", "biodiversity", "bee", "flora", "fauna"],
    "Synergy": ["agroforestry", "integrated", "intercropping", "rotation", "mixed", "relay cropping", "silvopastoral"],
    "Economic Viability": ["budget", "income", "costs", "market", "credit", "financial", "employment", "investment", "production", "yield", "profit"],
    "Social Values": ["women", "gender", "youth", "equity", "equality", "wealth", "food security", "literacy", "culture", "tradition", "widowed", "family"],
    "Fairness": ["fairness", "justice", "labor", "workload", "remuneration", "working conditions"],
    "Connectivity": ["services", "infrastructure", "market access", "connectivity", "advisory", "extension", "training"],
    "Land and Natural Resource Governance": ["tenure", "rights", "ownership", "legal", "statutory", "customary", "administration", "policy", "governance", "dispute", "conflict"],
    "Participation": ["participation", "discussion", "involvement", "stakeholders", "community", "collaborative", "group"],
    "Co-creation of Knowledge": ["research", "innovations", "experiment", "learning", "knowledge", "observation", "monitoring", "evaluation"]
}

def map_term_to_principles(term):
    term_low = term.lower()
    matched = []
    for principle, keywords in PRINCIPLES.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', term_low) for kw in keywords):
            matched.append(principle)
    return matched

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    terms = data["Practices_and_Indicators"]
    ontology = {p: [] for p in PRINCIPLES.keys()}
    ontology["Unmapped"] = []
    
    for t in terms:
        matched_principles = map_term_to_principles(t)
        if matched_principles:
            for p in matched_principles:
                ontology[p].append(t)
        else:
            ontology["Unmapped"].append(t)
            
    # Sort and deduplicate each principle
    for p in ontology:
        ontology[p] = sorted(list(set(ontology[p])))
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(ontology, f, indent=4)
        
    print(f"Mapping complete. Grouped {len(terms)} terms across {len(PRINCIPLES)} principles.")
    for p, tlist in ontology.items():
        print(f" - {p}: {len(tlist)} terms")

if __name__ == "__main__":
    main()
