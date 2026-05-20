import json
import re

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\wocat_conceptual_ontology.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\wocat_agroecological_ontology.json"

PRINCIPLES = {
    "1. Recycling": ["compost", "manure", "residue", "recycling", "biomass", "waste management"],
    "2. Input Reduction": ["minimum tillage", "conservation agriculture", "reduced tillage", "zero tillage", "input reduction", "biocides", "pesticides", "herbicides", "fertilizer"],
    "3. Soil Health": ["soil", "texture", "depth", "acidity", "crusting", "accumulation", "erosion", "fertility", "moisture", "organic matter", "siltation", "degradation", "topsoil", "soil life", "annual rainfall", "altitudinal zone"],
    "4. Animal Health": ["animal", "livestock", "cattle", "poultry", "fish", "bee", "honey", "stall feeding", "animal breeds", "fodder quality"],
    "5. Biodiversity": ["biodiversity", "variety", "species", "tree", "forest", "grass", "flora", "fauna", "shrub", "bush", "acacia", "eucalyptus", "evergreen", "deciduous", "nature conservation", "habitat diversity"],
    "6. Synergy": ["agroforestry", "silviculture", "silvipastoral", "integrated crop", "mixed cropping", "intercropping", "synergy", "integrated pest", "annual cropping", "annual crops", "agronomic measures"],
    "7. Economic Diversification": ["income", "profit", "benefit", "wealth", "economic", "diversity of income", "diversification", "self-sufficiency"],
    "8. Co-creation of Knowledge": ["training", "learning", "innovation", "farmer-to-farmer", "extension", "knowledge", "research", "skills", "local innovations", "education", "capacity building", "adoption of", "advisory service"],
    "9. Social Values & Diets": ["social", "cultural", "aesthetic", "prestige", "traditional", "beliefs", "customs", "norms", "diets", "food security"],
    "10. Fairness": ["gender", "women", "youth", "men", "equality", "landless", "literacy", "fairness", "equity", "disparities", "age of land users", "civil status", "female-headed", "male-headed"],
    "11. Connectivity": ["roads", "infrastructure", "market", "marketing", "logistics", "distribution", "networks", "communication", "transport", "railways", "access to markets", "access to services", "access to technical support", "services"],
    "12. Land & Natural Resource Governance": ["tenure", "rights", "ownership", "registration", "grabbing", "governance", "policy", "administration", "statutory", "customary", "legal", "access", "authorities", "conflict", "secure"],
    "13. Participation": ["participation", "involvement", "stakeholder", "community", "group discussion", "dialogue", "participation", "local communities", "focus group"]
}

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        tech_ontology = json.load(f)
        
    all_terms = []
    for terms in tech_ontology.values():
        all_terms.extend(terms)
    all_terms = sorted(list(set(all_terms)))
    
    principle_ontology = {p: [] for p in PRINCIPLES.keys()}
    principle_ontology["Other Technical Indicators"] = []
    
    for t in all_terms:
        matched = False
        t_low = t.lower()
        
        for principle, keywords in PRINCIPLES.items():
            if any(re.search(re.escape(kw), t_low) for kw in keywords):
                if ("access to services" in t_low or "access to markets" in t_low or "access to technical support" in t_low) \
                   and principle == "12. Land & Natural Resource Governance":
                    continue
                if "rights" in t_low and principle != "12. Land & Natural Resource Governance":
                    continue
                
                principle_ontology[principle].append(t)
                matched = True
        
        if not matched:
            principle_ontology["Other Technical Indicators"].append(t)
            
    for p in principle_ontology:
        principle_ontology[p] = sorted(list(set(principle_ontology[p])))
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(principle_ontology, f, indent=4)
        
    print(f"Final Correction complete. {len(all_terms)} terms mapped.")

if __name__ == "__main__":
    main()
