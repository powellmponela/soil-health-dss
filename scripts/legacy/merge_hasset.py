import json
import os

# Paths
MASTER_BALANCED = "principles_indicators/Ontology_index.json"
HASSET_MAP = "principles_indicators/hasset_mapping.json"
MASTER_BALANCED_TXT = "principles_indicators/Ontology_index.txt"

def merge_hasset():
    if not os.path.exists(MASTER_BALANCED) or not os.path.exists(HASSET_MAP):
        print("Error: Required mapping files not found.")
        return

    with open(MASTER_BALANCED, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(HASSET_MAP, 'r', encoding='utf-8') as f:
        hasset_data = json.load(f)

    # Merge
    for principle, terms in hasset_data.items():
        if principle in data:
            for term in terms:
                # Deduplicate by URI
                if not any(t['uri'] == term['uri'] for t in data[principle]["sub_concepts"]):
                    data[principle]["sub_concepts"].append({
                        "label": term["label"],
                        "uri": term["uri"],
                        "source": "HASSET",
                        "sub_concepts": []
                    })

    # Save
    with open(MASTER_BALANCED, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    # Regenerate TXT
    summary_lines = ["=== MASTER BALANCED AGROECOLOGY ONTOLOGY (Enriched with HASSET) ===\n"]
    summary_lines.append("Sources: AGROVOC, ENVO, GEMET, LANDVOC, UNBIS, HASSET, etc.\n\n")

    def write_node(node, level=0):
        indent = "  " * level
        source = node.get("source", "AGROVOC")
        summary_lines.append(f"{indent}- [{source}] {node['label']} ({node['uri']})\n")
        for child in node.get('sub_concepts', []):
            write_node(child, level + 1)

    for principle, content in data.items():
        summary_lines.append(f"\n[{principle.upper()}]\n")
        for root in content.get('sub_concepts', []):
            write_node(root, 0)

    with open(MASTER_BALANCED_TXT, 'w', encoding='utf-8') as f:
        f.writelines(summary_lines)

    print("Master Balanced Ontology enriched with HASSET terms.")

if __name__ == "__main__":
    merge_hasset()
