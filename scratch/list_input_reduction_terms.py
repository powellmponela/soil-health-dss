import json
import os

JSON_MASTER = "principles_indicators/Ontology_index.json"

def get_all_labels(node, labels):
    labels.append({
        "label": node.get('label'),
        "source": node.get('source'),
        "uri": node.get('uri')
    })
    for child in node.get('sub_concepts', []):
        get_all_labels(child, labels)

def main():
    if not os.path.exists(JSON_MASTER): return

    with open(JSON_MASTER, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    ir_data = master_data.get("Input Reduction")
    if not ir_data:
        print("Principle 'Input Reduction' not found.")
        return

    all_terms = []
    get_all_labels(ir_data, all_terms)

    # Sort by source
    all_terms.sort(key=lambda x: (str(x.get('source') or 'UNKNOWN'), str(x.get('label') or '')))

    print(f"\n=== Full Ontology Distribution: Input Reduction ({len(all_terms)} terms) ===")
    
    current_source = None
    for item in all_terms:
        if item['source'] != current_source:
            current_source = item['source']
            print(f"\n[SOURCE: {current_source}]")
        
        print(f"  - {item['label']}")

if __name__ == "__main__":
    main()
