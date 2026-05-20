import json
import os

# Path
MASTER_BALANCED = "principles_indicators/Ontology_index.json"

def inject_principle_2_data():
    if not os.path.exists(MASTER_BALANCED):
        print("Error: Ontology_index.json not found.")
        return

    with open(MASTER_BALANCED, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # User provided data for Input Reduction
    new_data = {
        "approaches": {
            "narrower_concepts": ["biocontrol", "biofertilizers", "green manure", "intercropping"],
            "entry_terms": ["input substitution", "low-chemical farming", "preventative agronomy"]
        },
        "inhibitors": {
            "is_affected_by": ["market cosmetic standards", "agrochemical subsidies", "information gaps"],
            "technical_tools": ["nitrification inhibitors", "urease inhibitors", "pesticide adjuvants"],
            "related_constraints": ["path dependency", "technological lock-in", "transition risk"]
        },
        "ontology_links": {
          "agrovoc": "http://aims.fao.org/aos/agrovoc/c_25465",
          "gemet": "pollution control",
          "envo": "anthropogenic process"
        }
    }

    # Targeted principle key (Handling naming variations)
    principle_key = "Input Reduction"
    if principle_key not in data:
        # Check for case variations
        for k in data.keys():
            if k.lower() == principle_key.lower():
                principle_key = k
                break
    
    if principle_key not in data:
        data[principle_key] = {"sub_concepts": []}

    # Injecting the data
    # We'll flatten this into the sub_concepts list to maintain the existing structure
    
    # 1. Approaches
    for term in new_data["approaches"]["narrower_concepts"] + new_data["approaches"]["entry_terms"]:
        data[principle_key]["sub_concepts"].append({
            "label": term,
            "uri": f"manual_injection/input_reduction/{term.replace(' ', '_')}",
            "source": "HLPE_ENRICHED",
            "sub_concepts": []
        })

    # 2. Inhibitors
    for cat in new_data["inhibitors"]:
        for term in new_data["inhibitors"][cat]:
            data[principle_key]["sub_concepts"].append({
                "label": f"{term} ({cat.replace('_', ' ')})",
                "uri": f"manual_injection/inhibitors/{term.replace(' ', '_')}",
                "source": "HLPE_ENRICHED",
                "sub_concepts": []
            })

    # 3. Ontology Links
    for source, val in new_data["ontology_links"].items():
        data[principle_key]["sub_concepts"].append({
            "label": f"Root: {val}",
            "uri": val if val.startswith("http") else f"root/{source}/{val}",
            "source": source.upper(),
            "sub_concepts": []
        })

    # Save
    with open(MASTER_BALANCED, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    print(f"Successfully enriched '{principle_key}' with manual HLPE data.")

if __name__ == "__main__":
    inject_principle_2_data()
