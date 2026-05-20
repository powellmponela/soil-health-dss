import json
import os

# Paths
INPUT_MASTER = r"c:\SOIL HEALTH\principles_indicators\offline_storage\faostat\ae_ontology_restart_plus_faostat_lowercase.json"
OUTPUT_MASTER = r"c:\SOIL HEALTH\master_agroecological_ontology.json"

def sentence_case(s):
    if not s: return s
    return s[0].upper() + s[1:]

def main():
    if not os.path.exists(INPUT_MASTER):
        print(f"Error: {INPUT_MASTER} not found.")
        return

    with open(INPUT_MASTER, "r", encoding="utf-8") as f:
        data = json.load(f)

    principles_raw = data.get("principles", {})
    master_ontology = {}

    # Principle naming map for standardization
    p_map = {
        "1. recycling": "1. Recycling",
        "2. input reduction": "2. Input Reduction",
        "3. soil health": "3. Soil Health",
        "4. animal health": "4. Animal Health",
        "5. biodiversity": "5. Biodiversity",
        "6. synergy": "6. Synergy",
        "7. economic diversification": "7. Economic Diversification",
        "8. co-creation of knowledge": "8. Co-creation of Knowledge",
        "9. social values & diets": "9. Social Values & Diets",
        "9. social values and diets": "9. Social Values & Diets",
        "10. fairness": "10. Fairness",
        "11. connectivity": "11. Connectivity",
        "12. land & natural resource governance": "12. Land & Natural Resource Governance",
        "12. land and natural resource governance": "12. Land & Natural Resource Governance",
        "13. participation": "13. Participation"
    }

    for p_key, content in principles_raw.items():
        # Get standardized title
        std_p_name = p_map.get(p_key.lower(), p_key.title())
        
        # Clean and sentence-case terms
        key_terms = sorted(list(set([sentence_case(t) for t in content.get("key_terms", []) if t])))
        
        # Clean and sentence-case indicators
        indicators = []
        for ind in content.get("indicators", []):
            if isinstance(ind, str):
                indicators.append({"label": sentence_case(ind), "source": "Multiple"})
            elif isinstance(ind, dict):
                ind_label = sentence_case(ind.get("label", ""))
                ind_source = ind.get("source", "Unknown")
                indicators.append({"label": ind_label, "source": ind_source})
        
        # Deduplicate indicators by label
        unique_indicators = {}
        for ind in indicators:
            if ind["label"] not in unique_indicators:
                unique_indicators[ind["label"]] = ind
        
        master_ontology[std_p_name] = {
            "key_terms": key_terms,
            "indicators": sorted(list(unique_indicators.values()), key=lambda x: x["label"])
        }

    # Add metadata
    final_output = {
        "metadata": {
            "title": "SHDSS Master Agroecological Ontology",
            "version": "1.1.0-PRODUCTION",
            "last_updated_utc": "2026-05-15",
            "total_principles": len(master_ontology),
            "sources": ["FAOSTAT", "World Bank", "TAPE", "UNBIS", "UNESCO", "Agrovoc", "ENVO", "Civicus", "Prindex", "Land Matrix", "ILOSTAT", "GBIF", "AWIN", "WAHIS"]
        },
        "principles": master_ontology
    }

    with open(OUTPUT_MASTER, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)
    
    print(f"Successfully generated Final Master Ontology at {OUTPUT_MASTER}")

if __name__ == "__main__":
    main()
