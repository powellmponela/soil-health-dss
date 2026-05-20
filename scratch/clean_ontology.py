import json

ONTOLOGY_FILE = r"c:\SOIL HEALTH\principles_indicators\Ontology_index.json"

# List of noisy terms to remove from the ontology
# We remove them if they appear as standalone labels
NOISY_TERMS = {
    'may', 'incl', 'example', 'has', 'which', 'each', 
    'compared', 'their', 'shape', 'size', 'did not', 'etc',
    'individuals', 'length', 'losses', 'logistics', 'including', 
    'persons', 'ratio of', 'share of', 'current', 'account', 
    'surface', 'percent of', 'idaho'
}

# Special handling for acronyms - we might keep them but only if we handle them correctly in extraction.
# For now, let's remove 'UN' and 'WHO' if they are lowercase or ambiguous in the ontology source.
# Actually, the user says "who (only if institution world health organization)" and "un (only if united nations)".
# Since the ontology is our source of truth, if the label is JUST 'WHO' or 'UN', it's risky.
# Let's keep them in the ontology for now but handle them in the extraction script.

def clean_node(node):
    if 'sub_concepts' in node:
        # Filter out sub_concepts that are in our noisy list
        node['sub_concepts'] = [
            clean_node(child) for child in node['sub_concepts'] 
            if child['label'].lower().strip() not in NOISY_TERMS
        ]
    return node

def main():
    print(f"Cleaning {ONTOLOGY_FILE}...")
    with open(ONTOLOGY_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for principle in data:
        data[principle] = clean_node(data[principle])

    with open(ONTOLOGY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Ontology cleaned.")

if __name__ == "__main__":
    main()
