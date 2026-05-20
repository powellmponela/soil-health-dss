import json
import os

ontology_path = r'c:\SOIL HEALTH\principles_indicators\Ontology_index.json'
terms_path = r'c:\SOIL HEALTH\principles_indicators\offline_storage\unbis\terms.json'
output_path = r'c:\SOIL HEALTH\principles_indicators\Ontology_index_patched.json'

mapping_rules = {
    "Soil Health": ["SOIL", "LAND", "FERTILIZER", "GROUND"],
    "Recycling": ["WASTE", "COMPOST", "MANURE", "RECYCLING"],
    "Input Reduction": ["PESTICIDE", "CHEMICAL", "INPUT"],
    "Biodiversity": ["WILDLIFE", "FAUNA", "FLORA", "SPECIES", "ECOSYSTEM", "CONSERVATION", "FOREST", "NATURE"],
    "Economic Diversification": ["ECONOMIC", "INCOME", "MARKET", "TRADE", "FINANCE", "LIVELIHOOD", "DIVERSIFICATION", "DEVELOPMENT"],
    "Social Values and Diets": ["SOCIAL", "DIET", "FOOD", "NUTRITION", "CULTURE", "HEALTH"],
    "Fairness": ["EQUITY", "RIGHTS", "JUSTICE", "POVERTY", "WAGE", "LABOUR", "WOMEN", "GENDER", "DISCRIMINATION", "EQUALITY"],
    "Connectivity": ["POLICY", "REGULATION", "LAW", "GOVERNANCE", "PLANNING", "COOPERATION", "INTERNATIONAL", "TREATIES"],
    "Land Governance": ["LAND TENURE", "LAND REFORM", "PROPERTY RIGHTS", "LAND USE"],
    "Participation": ["PARTICIPATION", "COMMUNITY", "LOCAL", "DECISION MAKING"],
    "Co-creation of Knowledge": ["RESEARCH", "STATISTICS", "METHODOLOGY", "KNOWLEDGE", "EDUCATION", "INDICATOR", "DOCUMENTATION"],
    "Synergy": ["SYNERGY", "INTEGRATION", "SYSTEMS"],
    "Animal Health": ["LIVESTOCK", "ANIMAL", "VETERINARY"]
}

print(f"Loading terms from {terms_path}...")
with open(terms_path, 'r', encoding='utf-8') as f:
    unbis_terms = json.load(f)

print(f"Loading ontology from {ontology_path}...")
with open(ontology_path, 'r', encoding='utf-8') as f:
    ontology = json.load(f)

counts = {k: 0 for k in mapping_rules}
unmapped = 0

for t in unbis_terms:
    label_upper = t['label'].upper()
    mapped = False
    for principle, keywords in mapping_rules.items():
        if any(kw in label_upper for kw in keywords):
            # Add to ontology
            new_entry = {
                "uri": t['uri'],
                "label": t['label'],
                "sub_concepts": [],
                "source": "UNBIS"
            }
            if principle in ontology:
                # Avoid duplicates
                if not any(e['uri'] == t['uri'] for e in ontology[principle]['sub_concepts']):
                    ontology[principle]['sub_concepts'].append(new_entry)
                    counts[principle] += 1
            mapped = True
            # We allow mapping to multiple principles if keywords match
    if not mapped:
        unmapped += 1

print("\nMapping Results:")
for p, c in counts.items():
    print(f" - {p}: {c} terms added")
print(f" - Unmapped: {unmapped}")

print(f"Saving patched ontology to {output_path}...")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(ontology, f, indent=4)

print("Done!")
