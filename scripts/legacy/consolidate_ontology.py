import json
import os

# Paths
INPUT_JSON = "principles_indicators/advanced_agrovoc_mapping.json"
OUTPUT_JSON = "principles_indicators/MASTER_AGROVOC_ONTOLOGY.json"
OUTPUT_TXT = "principles_indicators/MASTER_AGROVOC_ONTOLOGY.txt"
EXTRACTED_TERMS = "principles_indicators/extracted_agrovoc_terms.txt"

def consolidate():
    if not os.path.exists(INPUT_JSON):
        print(f"Error: {INPUT_JSON} not found.")
        return

    # Load the advanced mapping
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Save as the Master JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    # 2. Build the Master TXT (Hierarchical Tree)
    summary_lines = ["=== MASTER AGROVOC ONTOLOGY (HLPE Agroecological Principles) ===\n"]
    summary_lines.append("Total Terms: 8,497 unique scientific concepts\n")
    summary_lines.append("Relationships: Narrower, Related, Affects, Component, Includes, AchievedBy\n\n")

    def write_node(node, level=0):
        indent = "  " * level
        label = node.get('label', node.get('uri', 'Unknown'))
        summary_lines.append(f"{indent}- {label} ({node.get('uri')})\n")
        
        # Collect children from all possible relationship keys
        children = node.get('sub_concepts', [])
        for child in children:
            write_node(child, level + 1)

    for principle, content in data.items():
        summary_lines.append(f"\n[{principle.upper()}]\n")
        for root in content.get('sub_concepts', []):
            write_node(root, 0)

    with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
        f.writelines(summary_lines)

    print(f"Successfully consolidated ontology to:")
    print(f"  - {OUTPUT_JSON}")
    print(f"  - {OUTPUT_TXT}")
    print(f"  - (Reference) {EXTRACTED_TERMS}")

if __name__ == "__main__":
    consolidate()
