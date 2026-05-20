import json
import os

# Paths
AGROVOC_MAP = r"c:\SOIL HEALTH\api\data\agrovoc_principles_map.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\agrovoc\agrovoc_ontology_compact.json"

def main():
    if not os.path.exists(AGROVOC_MAP):
        print("Error: agrovoc_principles_map.json not found.")
        return

    with open(AGROVOC_MAP, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Standardize Principle names
    p_map = {
        "Recycling": "1. Recycling",
        "Input Reduction": "2. Input Reduction",
        "Soil Health": "3. Soil Health",
        "Animal Health": "4. Animal Health",
        "Biodiversity": "5. Biodiversity",
        "Synergy": "6. Synergy",
        "Economic Diversification": "7. Economic Diversification",
        "Co-creation of Knowledge": "8. Co-creation of Knowledge",
        "Social Values and Diets": "9. Social Values & Diets",
        "Fairness": "10. Fairness",
        "Connectivity": "11. Connectivity",
        "Land and natural resource governance": "12. Land & Natural Resource Governance",
        "Land Governance": "12. Land & Natural Resource Governance",
        "Participation": "13. Participation"
    }

    agrovoc_data = {v: {"key_terms": [], "indicators": []} for v in p_map.values()}
    total_found = 0

    for uri, content in data.items():
        label = content.get("prefLabel")
        principles = content.get("principles", [])
        if not label: continue

        for p_raw in principles:
            std_p = p_map.get(p_raw, p_raw.title())
            # Handle titles like "Animal health" to "Animal Health"
            if std_p not in agrovoc_data:
                # Try title case match
                for k, v in p_map.items():
                    if k.lower() == p_raw.lower():
                        std_p = v
                        break
            
            if std_p not in agrovoc_data:
                agrovoc_data[std_p] = {"key_terms": [], "indicators": []}

            agrovoc_data[std_p]["indicators"].append({
                "label": label,
                "source": "AGROVOC",
                "uri": uri
            })
            total_found += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(agrovoc_data, f, indent=4)
    
    print(f"Restored AGROVOC: {total_found} indicators -> {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
