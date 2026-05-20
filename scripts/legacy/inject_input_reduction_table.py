import json
import os

# Path
MASTER_BALANCED = "principles_indicators/Ontology_index.json"

def inject_input_reduction_table():
    if not os.path.exists(MASTER_BALANCED):
        print("Error: Ontology_index.json not found.")
        return

    with open(MASTER_BALANCED, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # User provided table data
    table_data = [
        {"approach": "Biological Control", "uri": "http://aims.fao.org/aos/agrovoc/c_1167", "role": "Utilizing natural enemies and microorganisms to manage pests."},
        {"approach": "Integrated Pest Management", "uri": "http://aims.fao.org/aos/agrovoc/c_3850", "role": "Combining monitoring, prevention, and targeted interventions."},
        {"approach": "Nutrient Cycling", "uri": "http://aims.fao.org/aos/agrovoc/c_5191", "role": "Utilizing manure, compost, and residues to minimize external fertilizer."},
        {"approach": "Nitrogen Fixation", "uri": "http://aims.fao.org/aos/agrovoc/c_5182", "role": "Using legumes and biofertilizers to capture atmospheric nitrogen."},
        {"approach": "Conservation Tillage", "uri": "http://aims.fao.org/aos/agrovoc/c_5206", "role": "Reducing fuel use and machinery wear while retaining soil moisture."},
        {"approach": "Seed Autonomy", "uri": "http://aims.fao.org/aos/agrovoc/c_330932", "role": "Reducing dependency on annually purchased proprietary seeds."}
    ]

    principle_key = "Input Reduction"
    # Handling case sensitivity
    for k in data.keys():
        if k.lower() == principle_key.lower():
            principle_key = k
            break
            
    if principle_key not in data:
        data[principle_key] = {"sub_concepts": []}

    # Injecting
    for item in table_data:
        # Avoid duplicates
        if not any(t['uri'] == item['uri'] for t in data[principle_key]["sub_concepts"]):
            data[principle_key]["sub_concepts"].append({
                "label": item["approach"],
                "uri": item["uri"],
                "source": "AGROVOC",
                "functional_role": item["role"],
                "sub_concepts": []
            })

    # Save
    with open(MASTER_BALANCED, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    print(f"Successfully enriched '{principle_key}' with functional roles and AGROVOC roots.")

if __name__ == "__main__":
    inject_input_reduction_table()
