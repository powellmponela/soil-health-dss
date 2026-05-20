import json
import os

# Paths
MASTER_BALANCED = "principles_indicators/Ontology_index.json"
MASTER_BALANCED_TXT = "principles_indicators/Ontology_index.txt"

def consolidate_balanced():
    if not os.path.exists(MASTER_BALANCED):
        print("Error: Ontology_index.json not found.")
        return

    with open(MASTER_BALANCED, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Build the Master TXT (Hierarchical Tree)
    summary_lines = ["=== MASTER BALANCED AGROECOLOGY ONTOLOGY (Final Enriched Version) ===\n"]
    summary_lines.append("Sources: AGROVOC, ENVO, GEMET, LANDVOC, UNBIS, HASSET, FAOSTAT, etc.\n")
    summary_lines.append("Depth: High-resolution hierarchical mapping for 13 principles\n\n")

    def write_node(node, level=0):
        indent = "  " * level
        source = node.get("source", "AGROVOC")
        role = node.get("functional_role", "")
        role_str = f" | Role: {role}" if role else ""
        
        summary_lines.append(f"{indent}- [{source}] {node['label']} ({node['uri']}){role_str}\n")
        for child in node.get('sub_concepts', []):
            write_node(child, level + 1)

    for principle, content in data.items():
        summary_lines.append(f"\n[{principle.upper()}]\n")
        for root in content.get('sub_concepts', []):
            write_node(root, 0)

    with open(MASTER_BALANCED_TXT, 'w', encoding='utf-8') as f:
        f.writelines(summary_lines)

    print(f"Master Balanced Ontology summary updated: {MASTER_BALANCED_TXT}")

if __name__ == "__main__":
    consolidate_balanced()
