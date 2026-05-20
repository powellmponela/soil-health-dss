import json
import os

PRINCIPLES_MAP_FILE = "principles_indicators/Ontology_index.json"
FRAMEWORK_TERMS_FILE = "principles_indicators/extracted_framework_terms.json"
OUTPUT_FILE = "principles_indicators/extracted_terms_per_principle.txt"

def get_all_terms(node, terms_set):
    label = node.get('label')
    if label: terms_set.add(label.lower())
    for child in node.get('sub_concepts', []): get_all_terms(child, terms_set)

def main():
    if not os.path.exists(PRINCIPLES_MAP_FILE) or not os.path.exists(FRAMEWORK_TERMS_FILE): return
    with open(PRINCIPLES_MAP_FILE, 'r', encoding='utf-8') as f: principles_map = json.load(f)
    with open(FRAMEWORK_TERMS_FILE, 'r', encoding='utf-8') as f: framework_terms = json.load(f)
    
    found_terms = set()
    for fw_data in framework_terms.values():
        tf = fw_data.get('terms_found', {})
        for term in tf.keys(): found_terms.add(term.lower())

    report_lines = []
    for principle, p_data in principles_map.items():
        ontology_terms = set()
        get_all_terms(p_data, ontology_terms)
        intersected = sorted(list(ontology_terms.intersection(found_terms)))
        report_lines.append(f"=== {principle} ({len(intersected)} terms) ===")
        for term in intersected: report_lines.append(f"  - {term}")
        report_lines.append("")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    print(f"Updated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
