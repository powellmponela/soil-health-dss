import json
import os

JSON_MASTER = "principles_indicators/Ontology_index.json"
WOCAT_MAPPED = "principles_indicators/wocat_mapped_principles.json"

def add_terms_to_node(node, terms, source="WOCAT"):
    current_labels = {c.get('label', '').lower() for c in node.get('sub_concepts', [])}
    
    for term in terms:
        if term.lower() not in current_labels:
            new_concept = {
                "label": term,
                "source": source,
                "uri": f"wocat:{term.lower().replace(' ', '_')}",
                "sub_concepts": []
            }
            node['sub_concepts'].append(new_concept)
            current_labels.add(term.lower())

def main():
    if not os.path.exists(JSON_MASTER) or not os.path.exists(WOCAT_MAPPED): return

    with open(JSON_MASTER, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    with open(WOCAT_MAPPED, 'r', encoding='utf-8') as f:
        wocat_data = json.load(f)

    # Principle keys in WOCAT mapping match the top-level keys in Master Index
    # (e.g., "Recycling", "Fairness", etc.)
    
    total_added = 0
    for principle, terms in wocat_data.items():
        if principle in master_data:
            # Add WOCAT terms as direct sub-concepts of the Principle node
            # (Or we could create a 'WOCAT_Expansion' child node)
            if 'sub_concepts' not in master_data[principle]:
                master_data[principle]['sub_concepts'] = []
            
            # Group them under a specific 'WOCAT_Expansion' node to keep it clean
            wocat_node = None
            for child in master_data[principle]['sub_concepts']:
                if child.get('label') == "WOCAT SLM Expansion":
                    wocat_node = child
                    break
            
            if not wocat_node:
                wocat_node = {
                    "label": "WOCAT SLM Expansion",
                    "source": "WOCAT",
                    "uri": f"wocat:{principle.lower()}_expansion",
                    "sub_concepts": []
                }
                master_data[principle]['sub_concepts'].append(wocat_node)
            
            # Deduplicate and add
            existing_count = len(wocat_node['sub_concepts'])
            add_terms_to_node(wocat_node, terms)
            total_added += (len(wocat_node['sub_concepts']) - existing_count)

    with open(JSON_MASTER, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, indent=4)

    print(f"Successfully merged {total_added} unique WOCAT terms into Master Ontology.")

if __name__ == "__main__":
    main()
