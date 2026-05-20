import json
import os

ontology_path = r'c:\SOIL HEALTH\principles_indicators\Ontology_index.json'
terms_path = r'c:\SOIL HEALTH\principles_indicators\offline_storage\world_bank\terms.json'
output_path = r'c:\SOIL HEALTH\principles_indicators\Ontology_index_patched.json'

print(f"Loading World Bank terms from {terms_path}...")
with open(terms_path, 'r', encoding='utf-8') as f:
    wb_terms = json.load(f)

print(f"Loading ontology from {ontology_path}...")
with open(ontology_path, 'r', encoding='utf-8') as f:
    ontology = json.load(f)

counts = {}
total_added = 0

# Limit additions per principle to prevent database explosion
# World bank dataset is huge, let's keep only unique labels up to a certain threshold if needed.
# Since it's a "Master Ontology", we'll just insert them but deduplicate strictly by label.

for t in wb_terms:
    for principle in t['principles']:
        if principle not in ontology:
            continue

        new_entry = {
            "uri": t['uri'],
            "label": t['label'],
            "sub_concepts": [],
            "source": "World_Bank"
        }
        
        # Avoid exact label duplicates
        existing_labels = {e['label'].lower() for e in ontology[principle]['sub_concepts']}
        if t['label'].lower() not in existing_labels:
            ontology[principle]['sub_concepts'].append(new_entry)
            counts[principle] = counts.get(principle, 0) + 1
            total_added += 1

print("\nWorld Bank Integration Results:")
for p, c in sorted(counts.items()):
    print(f" - {p}: {c} terms added")
print(f"Total terms added: {total_added}")

print(f"Saving patched ontology to {output_path}...")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(ontology, f, indent=4)

print("Done!")
