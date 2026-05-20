import json
import os

ONTOLOGY_INDEX = "principles_indicators/Ontology_index.json"

def load_list(path):
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("===")]

def merge_global():
    if not os.path.exists(ONTOLOGY_INDEX): return
    with open(ONTOLOGY_INDEX, 'r', encoding='utf-8') as f: data = json.load(f)

    # 1. SDGs -> Multiple
    sdg_terms = load_list("principles_indicators/offline_storage/unbis/sdg_indicators.txt")
    sdg_map = {
        "Poverty": "Fairness",
        "Hunger": "Social Values and Diets",
        "Gender": "Fairness",
        "Water": "Soil Health",
        "Climate": "Synergy",
        "Land": "Biodiversity",
        "Sustainable agriculture": "Input Reduction",
        "Consumption": "Recycling"
    }
    for line in sdg_terms:
        # Check if it's a Goal or Indicator
        if line.startswith("Goal"): continue
        target_p = "Land Governance" # Default for policy
        for keyword, p in sdg_map.items():
            if keyword in line: target_p = p; break
        
        data[target_p]["sub_concepts"].append({"label": line, "uri": "https://sdgs.un.org/indicators", "source": "SDG", "sub_concepts": []})

    # 2. World Bank -> Land Governance / Economic Diversification
    wb_terms = load_list("principles_indicators/offline_storage/world_bank/indicators.txt")
    for line in wb_terms:
        target_p = "Land Governance"
        if "Employment" in line or "Value added" in line: target_p = "Economic Diversification"
        if "Yield" in line or "Production" in line: target_p = "Synergy"
        
        data[target_p]["sub_concepts"].append({"label": line, "uri": "https://data.worldbank.org/indicator", "source": "World_Bank", "sub_concepts": []})

    with open(ONTOLOGY_INDEX, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print("SDG and World Bank merge complete.")

if __name__ == "__main__":
    merge_global()
