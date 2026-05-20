import json
import os

# Configuration Paths
JSON_MASTER = "principles_indicators/Ontology_index.json"
TXT_MASTER = "principles_indicators/Ontology_index.txt"
FRAMEWORK_TERMS_FILE = "principles_indicators/extracted_framework_terms.json"
EXTRACTED_REPORT_FILE = "principles_indicators/extracted_terms_per_principle.txt"

def format_hierarchy_node(node, level=0):
    """Formats a node for the full hierarchy view (Ontology_index.txt)"""
    lines = []
    label = node.get('label', 'Unnamed')
    uri = node.get('uri', 'No URI')
    source = node.get('source', 'AGROVOC')
    rel = node.get('relationship', 'root')
    indent = "  " * level
    lines.append(f"{indent}- [{source}] {label} ({rel}) ({uri})")
    for child in node.get('sub_concepts', []):
        lines.extend(format_hierarchy_node(child, level + 1))
    return lines

def get_all_ontology_labels(node, labels_set):
    """Collects all labels from an ontology node for intersection analysis"""
    label = node.get('label')
    if label:
        labels_set.add(label.lower())
    for child in node.get('sub_concepts', []):
        get_all_ontology_labels(child, labels_set)

def sync_all():
    print("--- Starting Master Ontology Synchronization ---")
    
    if not os.path.exists(JSON_MASTER):
        print(f"Error: {JSON_MASTER} not found.")
        return

    with open(JSON_MASTER, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    # 1. Update Ontology_index.txt (Full Hierarchy View)
    print(f"Updating {TXT_MASTER}...")
    with open(TXT_MASTER, 'w', encoding='utf-8') as f:
        for principle, p_data in master_data.items():
            f.write(f"=== {principle} ===\n")
            lines = format_hierarchy_node(p_data, level=0)
            if lines:
                for line in lines[1:]: # Skip the root itself as it's the principle header
                    f.write(line + "\n")
            f.write("\n\n")

    # 2. Update extracted_terms_per_principle.txt (Framework Findings Report)
    if os.path.exists(FRAMEWORK_TERMS_FILE):
        print(f"Updating {EXTRACTED_REPORT_FILE}...")
        with open(FRAMEWORK_TERMS_FILE, 'r', encoding='utf-8') as f:
            framework_data = json.load(f)
        
        # Aggregate all terms found across all frameworks
        # terms_found may be a list of {term, count, ...} objects or a plain dict
        found_terms_set = set()
        for fw_id, fw_content in framework_data.items():
            tf = fw_content.get('terms_found', {})
            if isinstance(tf, list):
                for item in tf:
                    t = item.get('term', '') if isinstance(item, dict) else str(item)
                    if t:
                        found_terms_set.add(t.lower())
            elif isinstance(tf, dict):
                for term in tf.keys():
                    found_terms_set.add(term.lower())
        
        report_lines = []
        for principle, p_data in master_data.items():
            ontology_labels = set()
            get_all_ontology_labels(p_data, ontology_labels)
            
            # Find intersection
            intersected = sorted(list(ontology_labels.intersection(found_terms_set)))
            report_lines.append(f"=== {principle} ({len(intersected)} terms) ===")
            for term in intersected:
                report_lines.append(f"  - {term}")
            report_lines.append("")
        
        with open(EXTRACTED_REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))
        print(f"Extraction report synchronized ({len(found_terms_set)} total terms aggregated).")
    else:
        print(f"Warning: {FRAMEWORK_TERMS_FILE} not found. Skipping extraction report update.")

    print("\nMaster Synchronization Complete.")

if __name__ == "__main__":
    sync_all()
