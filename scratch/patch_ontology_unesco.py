import json
import os

ontology_path = r'c:\SOIL HEALTH\principles_indicators\Ontology_index.json'
terms_path = r'c:\SOIL HEALTH\principles_indicators\offline_storage\unesco_thesaurus\terms.json'
output_path = r'c:\SOIL HEALTH\principles_indicators\Ontology_index_patched.json'

print(f"Loading UNESCO terms from {terms_path}...")
with open(terms_path, 'r', encoding='utf-8') as f:
    unesco_terms = json.load(f)

print(f"Loading ontology from {ontology_path}...")
with open(ontology_path, 'r', encoding='utf-8') as f:
    ontology = json.load(f)

counts = {}
total_added = 0

for t in unesco_terms:
    for principle in t['principles']:
        if principle not in ontology:
            # Handle naming differences if any
            if principle == "Co-creation of Knowledge":
                p_key = "Co-creation of Knowledge"
            elif principle == "Social Values and Diets":
                p_key = "Social Values and Diets"
            elif principle == "Land Governance":
                p_key = "Land Governance"
            else:
                p_key = principle
        else:
            p_key = principle

        if p_key in ontology:
            new_entry = {
                "uri": t['uri'],
                "label": t['label'],
                "sub_concepts": [],
                "source": "UNESCO"
            }
            # Avoid duplicates
            if not any(e['uri'] == t['uri'] for e in ontology[p_key]['sub_concepts']):
                ontology[p_key]['sub_concepts'].append(new_entry)
                counts[p_key] = counts.get(p_key, 0) + 1
                total_added += 1

print("\nUNESCO Integration Results:")
for p, c in counts.items():
    print(f" - {p}: {c} terms added")
print(f"Total terms added: {total_added}")

print(f"Saving patched ontology to {output_path}...")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(ontology, f, indent=4)

print("Done!")
