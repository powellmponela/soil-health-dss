import csv
import json
import os
import re

csv_path = r'c:\SOIL HEALTH\principles_indicators\offline_storage\unesco_thesaurus\voc001.csv'
terms_json_path = r'c:\SOIL HEALTH\principles_indicators\offline_storage\unesco_thesaurus\terms.json'
terms_txt_path = r'c:\SOIL HEALTH\principles_indicators\offline_storage\unesco_thesaurus\terms.txt'

mapping_rules = {
    "Fairness": ["RIGHTS", "GENDER", "EQUITY", "JUSTICE", "POVERTY", "WOMEN", "DISCRIMINATION", "EQUALITY", "HUMAN RIGHTS"],
    "Co-creation of Knowledge": ["EDUCATION", "RESEARCH", "SCIENCE", "TECHNOLOGY", "KNOWLEDGE", "SCHOOL", "TEACHING", "INFORMATION", "METHODOLOGY", "STATISTICS"],
    "Connectivity": ["POLICY", "REGIONALISM", "GOVERNANCE", "CULTURE", "COMMUNICATION", "INTERNATIONAL", "COOPERATION", "TREATIES"],
    "Social Values and Diets": ["HEALTH", "FOOD", "NUTRITION", "SOCIETY", "SOCIAL", "DIET", "CULTURAL"],
    "Economic Diversification": ["INDUSTRIALIZATION", "ECONOMY", "MARKET", "DEVELOPMENT", "TRADE", "INCOME"],
    "Soil Health": ["SOIL", "LAND", "AGRICULTURE", "ENVIRONMENT", "NATURE", "ECOLOGY"],
    "Land Governance": ["LAND TENURE", "LAND REFORM", "PROPERTY RIGHTS", "LAND USE"],
    "Biodiversity": ["WILDLIFE", "FAUNA", "FLORA", "SPECIES", "ECOSYSTEM", "CONSERVATION", "FOREST"]
}

def is_english(text):
    # Simple check: mostly ASCII and common English words/patterns
    # UNESCO labels in English usually don't have non-ASCII characters
    try:
        text.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

print(f"Processing {csv_path}...")

extracted_terms = []
seen_uris = set()

with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Predicate for prefLabel
        if row['Predicate'] == 'http://www.w3.org/2004/02/skos/core#prefLabel':
            label = row['Object']
            uri = row['Subject']
            
            if is_english(label) and uri not in seen_uris:
                label_upper = label.upper()
                mapped_principles = []
                for principle, keywords in mapping_rules.items():
                    if any(kw in label_upper for kw in keywords):
                        mapped_principles.append(principle)
                
                if mapped_principles:
                    extracted_terms.append({
                        "uri": uri,
                        "label": label,
                        "principles": list(set(mapped_principles)),
                        "source": "UNESCO"
                    })
                    seen_uris.add(uri)

print(f"Extracted {len(extracted_terms)} relevant terms.")

# Save JSON
with open(terms_json_path, 'w', encoding='utf-8') as f:
    json.dump(extracted_terms, f, indent=4)

# Save TXT
with open(terms_txt_path, 'w', encoding='utf-8') as f:
    for t in extracted_terms:
        f.write(f"{t['label']} ({t['uri']}) - {', '.join(t['principles'])}\n")

print(f"Saved to {terms_json_path} and {terms_txt_path}")
