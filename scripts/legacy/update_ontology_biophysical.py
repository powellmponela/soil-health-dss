import json
import os

# Paths
MASTER_BALANCED = "principles_indicators/Ontology_index.json"
BIOPHYSICAL_MASTER = "principles_indicators/input_reduction_biophysical_master.json"
MASTER_BALANCED_TXT = "principles_indicators/Ontology_index.txt"

def update_with_biophysical():
    if not os.path.exists(MASTER_BALANCED) or not os.path.exists(BIOPHYSICAL_MASTER):
        print("Error: Required files not found.")
        return

    with open(MASTER_BALANCED, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    with open(BIOPHYSICAL_MASTER, 'r', encoding='utf-8') as f:
        biophysical_data = json.load(f)

    principle_key = "Input Reduction"
    for k in master_data.keys():
        if k.lower() == principle_key.lower():
            principle_key = k
            break

    if principle_key not in master_data:
        master_data[principle_key] = {"sub_concepts": []}

    # 1. Merge AGROVOC Expanded (Flat labels)
    for rel, terms in biophysical_data["agrovoc_expanded"].items():
        for term in terms:
            if not any(t['label'] == term for t in master_data[principle_key]["sub_concepts"]):
                master_data[principle_key]["sub_concepts"].append({
                    "label": term,
                    "uri": f"agrovoc_expanded/{rel}/{term.replace(' ', '_')}",
                    "source": f"AGROVOC_{rel}",
                    "sub_concepts": []
                })

    # 2. Merge ENVO Scientific
    for item in biophysical_data["envo_scientific"]:
        if not any(t['uri'] == item['uri'] for t in master_data[principle_key]["sub_concepts"]):
            master_data[principle_key]["sub_concepts"].append({
                "label": item["label"],
                "uri": item["uri"],
                "source": "ENVO",
                "sub_concepts": []
            })

    # 3. Merge SWEET Physical
    for item in biophysical_data["sweet_physical"]:
        if not any(t['uri'] == item['uri'] for t in master_data[principle_key]["sub_concepts"]):
            master_data[principle_key]["sub_concepts"].append({
                "label": item["label"],
                "uri": item["uri"],
                "source": "SWEET",
                "sub_concepts": []
            })

    # Save Master
    with open(MASTER_BALANCED, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, indent=4)

    # Regenerate TXT Summary
    summary_lines = ["=== MASTER BALANCED AGROECOLOGY ONTOLOGY (Updated with Biophysical Master) ===\n"]
    summary_lines.append("Sources: AGROVOC, ENVO, GEMET, LANDVOC, UNBIS, HASSET, SWEET, etc.\n\n")

    def write_node(node, level=0):
        indent = "  " * level
        source = node.get("source", "AGROVOC")
        summary_lines.append(f"{indent}- [{source}] {node['label']} ({node['uri']})\n")
        for child in node.get('sub_concepts', []):
            write_node(child, level + 1)

    for principle, content in master_data.items():
        summary_lines.append(f"\n[{principle.upper()}]\n")
        for root in content.get('sub_concepts', []):
            write_node(root, 0)

    with open(MASTER_BALANCED_TXT, 'w', encoding='utf-8') as f:
        f.writelines(summary_lines)

    print("Master Balanced Ontology updated with Biophysical Master data.")

if __name__ == "__main__":
    update_with_biophysical()
