import json
import os

ontology_path = r'c:\SOIL HEALTH\principles_indicators\Ontology_index.json'
terms_path = r'c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\qcat_terms.json'
output_path = r'c:\SOIL HEALTH\principles_indicators\Ontology_index_patched.json'

print(f"Loading WOCAT terms from {terms_path}...")
with open(terms_path, 'r', encoding='utf-8') as f:
    wocat_terms = json.load(f)

print(f"Loading ontology from {ontology_path}...")
with open(ontology_path, 'r', encoding='utf-8') as f:
    ontology = json.load(f)

counts = {}
total_added = 0

for t in wocat_terms:
    for principle in t['principles']:
        if principle not in ontology:
            continue

        new_entry = {
            "uri": t['uri'],
            "label": t['label'],
            "sub_concepts": [],
            "source": "WOCAT"
        }
        
        # Avoid duplicates based on label since uris might be regenerated
        if not any(e['label'].lower() == t['label'].lower() for e in ontology[principle]['sub_concepts']):
            ontology[principle]['sub_concepts'].append(new_entry)
            counts[principle] = counts.get(principle, 0) + 1
            total_added += 1

print("\nWOCAT Integration Results:")
for p, c in counts.items():
    print(f" - {p}: {c} terms added")
print(f"Total terms added: {total_added}")

print(f"Saving patched ontology to {output_path}...")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(ontology, f, indent=4)

print("Done!")
