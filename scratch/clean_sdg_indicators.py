import json
import os
import re

JSON_PATH = "principles_indicators/Ontology_index.json"

def clean_sdg_label(label):
    # Remove "- " prefix
    label = re.sub(r'^- ', '', label)
    # Remove indicator codes like "1.1.1", "1.a.2", "2.4.1"
    label = re.sub(r'^\d+\.[0-9a-z]+\.\d+\s*', '', label, flags=re.IGNORECASE)
    # Remove Tier info if already appended (e.g. "(Tier I)")
    label = re.sub(r'\s*\(Tier\s+[I|V|X]+\)', '', label)
    return label.strip()

def extract_key_terms(label):
    """
    Simplifies long SDG descriptions into searchable key terms.
    Example: 'Proportion of population living below international poverty line'
    -> 'poverty line'
    """
    # This is a heuristic. We'll take the main noun phrases or just clean the label.
    # For now, we will use the cleaned label as the primary descriptor.
    return label

def main():
    if not os.path.exists(JSON_PATH): return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    def process_node(node):
        source = node.get('source', '')
        if source == 'SDG':
            original_label = node.get('label', '')
            cleaned = clean_sdg_label(original_label)
            # If the label was cleaned successfully, update it
            if cleaned and cleaned != original_label:
                node['label'] = cleaned
                # Store the original as a property if needed for reference
                node['original_indicator'] = original_label
                print(f"Cleaned: {original_label} -> {cleaned}")
        
        for child in node.get('sub_concepts', []):
            process_node(child)

    for principle in data.values():
        process_node(principle)

    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print("SDG labels humanized in Master JSON.")

if __name__ == "__main__":
    main()
