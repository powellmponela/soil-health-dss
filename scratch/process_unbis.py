import csv
import json
import os
import re

input_file = r'c:\SOIL HEALTH\principles_indicators\offline_storage\unbis\unbist-20250708.csv'
output_txt = r'c:\SOIL HEALTH\principles_indicators\offline_storage\unbis\terms.txt'
output_json = r'c:\SOIL HEALTH\principles_indicators\offline_storage\unbis\terms.json'

keywords = [
    'SOCIAL', 'EQUITY', 'GENDER', 'WOMEN', 'RIGHTS', 'JUSTICE', 'POVERTY', 'WAGE', 'LABOUR', 'EMPLOYMENT',
    'AGRICULTURE', 'FARMING', 'LAND', 'SOIL', 'HEALTH', 'FERTILIZER', 'IRRIGATION', 'CROPS', 'LIVESTOCK',
    'POLICY', 'REGULATION', 'LAW', 'GOVERNANCE', 'PLANNING', 'LEGISLATION',
    'ECONOMIC', 'INCOME', 'FINANCE', 'MARKET', 'TRADE', 'DIVERSIFICATION', 'LIVELIHOOD',
    'METHODOLOGY', 'RESEARCH', 'STATISTICS', 'INDICATOR'
]

def is_english(text):
    if not text: return False
    # Check if it contains mostly latin characters
    return bool(re.search(r'[a-zA-Z]', text)) and not any(ord(c) > 1000 for c in text)

terms = []

print(f"Reading {input_file}...")
with open(input_file, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        uri = row['uri']
        label = row['prefLabel']
        
        if is_english(label):
            label_upper = label.upper()
            # Check if any keyword is in the label
            if any(kw in label_upper for kw in keywords):
                terms.append({
                    "label": label,
                    "uri": uri
                })

# Deduplicate by URI and Label (multilingual rows might have same URI)
unique_terms = {}
for t in terms:
    key = (t['uri'], t['label'])
    if key not in unique_terms:
        unique_terms[key] = t

# Sort by label
sorted_terms = sorted(unique_terms.values(), key=lambda x: x['label'])

print(f"Extracted {len(sorted_terms)} relevant terms.")

# Save to TXT
with open(output_txt, mode='w', encoding='utf-8') as f:
    for t in sorted_terms:
        f.write(f"{t['label']} ({t['uri']})\n")

# Save to JSON
with open(output_json, mode='w', encoding='utf-8') as f:
    json.dump(list(sorted_terms), f, indent=4)

print("Saved results.")
