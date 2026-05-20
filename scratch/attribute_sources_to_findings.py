import json
import os

JSON_MASTER = "principles_indicators/Ontology_index.json"
EXTRACTED_REPORT = "principles_indicators/extracted_terms_per_principle.txt"
FRAMEWORK_TERMS_FILE = "principles_indicators/extracted_framework_terms.json"

def get_term_source_map(node, mapping):
    label = node.get('label', '').lower()
    source = node.get('source', 'AGROVOC')
    if label:
        mapping[label] = source
    for child in node.get('sub_concepts', []):
        get_term_source_map(child, mapping)

def main():
    if not os.path.exists(JSON_MASTER) or not os.path.exists(FRAMEWORK_TERMS_FILE): return

    with open(JSON_MASTER, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    with open(FRAMEWORK_TERMS_FILE, 'r', encoding='utf-8') as f:
        framework_data = json.load(f)

    # 1. Build a map of label -> source from the Master Ontology
    label_to_source = {}
    for p_data in master_data.values():
        get_term_source_map(p_data, label_to_source)

    # 2. Find terms in frameworks and attribute sources
    found_terms_set = set()
    for fw_content in framework_data.values():
        tf = fw_content.get('terms_found', [])
        for entry in tf:
            term = entry.get('term', '')
            if term:
                found_terms_set.add(term.lower())

    # 3. Create the Attributed Report
    report_lines = []
    source_stats = {}

    for principle, p_data in master_data.items():
        ontology_labels = set()
        # Collect all labels for this principle to find intersection
        temp_map = {}
        get_term_source_map(p_data, temp_map)
        ontology_labels = set(temp_map.keys())
        
        intersected = sorted(list(ontology_labels.intersection(found_terms_set)))
        report_lines.append(f"=== {principle} ({len(intersected)} terms) ===")
        
        for term in intersected:
            source = label_to_source.get(term, "UNKNOWN")
            report_lines.append(f"  - {term} [{source}]")
            source_stats[source] = source_stats.get(source, 0) + 1
        report_lines.append("")

    with open(EXTRACTED_REPORT, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))

    print("\n=== Source Attribution Stats for Extracted Terms ===")
    sorted_stats = sorted(source_stats.items(), key=lambda x: x[1], reverse=True)
    for src, count in sorted_stats:
        print(f"{src}: {count}")

if __name__ == "__main__":
    main()
