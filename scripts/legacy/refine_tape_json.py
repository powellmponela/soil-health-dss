import json
import os
import re

def refine_label(label):
    if not label: return ""
    
    # Remove index base periods
    label = re.sub(r'\(2014-2016 = 100\)', '', label)
    
    # Simplify long multi-sector labels
    label = label.replace("Agriculture, forestry, and fishing, value added", "Agri-forestry-fishing value added")
    label = label.replace("Agricultural irrigated land (% of total agricultural land)", "Irrigated land (% total ag land)")
    label = label.replace("Fertilizer consumption (kilograms per hectare of arable land)", "Fertilizer use (kg/ha arable)")
    label = label.replace("Adult literacy rate, population 15+ years, both sexes (%)", "Adult literacy rate (%)")
    label = label.replace("Rural poverty headcount ratio at national poverty lines (% of rural population)", "Rural poverty ratio (%)")
    label = label.replace("Agricultural land (% of land area)", "Agricultural land (% area)")
    label = label.replace("Arable land (% of land area)", "Arable land (% area)")
    label = label.replace("Forest area (% of land area)", "Forest area (% area)")
    label = label.replace("Marine protected areas (% of territorial waters)", "Marine protected areas (%)")
    label = label.replace("Terrestrial protected areas (% of total land area)", "Terrestrial protected areas (%)")
    
    # Cleanup units and boilerplate
    label = label.replace("(% of total population)", "(%)")
    label = label.replace("(% of GDP)", "(% GDP)")
    
    return label.strip()

def refine_ontology():
    path = r"c:\SOIL HEALTH\principles_indicators\offline_storage\tape\agroecological_key_terms_indicators_compact_TAPE.json"
    if not os.path.exists(path):
        print("File not found.")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    refined_data = {}
    for p, content in data.items():
        # Refine key terms (capitalize)
        refined_key_terms = sorted(list(set([t.capitalize() for t in content.get("key_terms", [])])))
        
        # Refine indicator labels
        refined_indicators = []
        seen_labels = set()
        for ind in content.get("indicators", []):
            orig_label = ind.get("label", "")
            new_label = refine_label(orig_label)
            if new_label and new_label not in seen_labels:
                ind["label"] = new_label
                refined_indicators.append(ind)
                seen_labels.add(new_label)
        
        refined_data[p] = {
            "key_terms": refined_key_terms,
            "indicators": refined_indicators
        }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(refined_data, f, indent=2)
    
    print(f"Refined TAPE ontology saved to {path}")

if __name__ == "__main__":
    refine_ontology()
