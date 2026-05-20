import pandas as pd
import json
import os
import re

EXCEL_PATH = r"principles_indicators\offline_storage\sdg\Tier Classification of SDG Indicators_ 30 Mar 2026_web.xlsx"
JSON_PATH = "principles_indicators/Ontology_index.json"

def extract_code(text):
    match = re.search(r'(\d+\.[0-9a-z]+\.\d+)', text, re.IGNORECASE)
    return match.group(1) if match else None

def main():
    print("Reading SDG Tier Classification...")
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name='Updated Tier classification')
        mapping = {}
        for index, row in df.iterrows():
            if index == 0: continue
            raw_indicator = str(row.iloc[2]).strip()
            tier = str(row.iloc[6]).strip()
            if raw_indicator and tier and raw_indicator != 'nan' and tier != 'nan':
                code = extract_code(raw_indicator)
                if code:
                    mapping[code] = tier
        print(f"Mapped {len(mapping)} SDG codes to Tiers. Sample: {list(mapping.items())[:5]}")
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0

    def update_node(node):
        nonlocal updated_count
        label = node.get('label', '')
        source = node.get('source', '')
        if source == 'SDG':
            code = extract_code(label)
            if code and code in mapping:
                if f"({mapping[code]})" not in label:
                    node['label'] = f"{label} ({mapping[code]})"
                    updated_count += 1
        
        for child in node.get('sub_concepts', []):
            update_node(child)

    for principle in data.values():
        update_node(principle)

    if updated_count > 0:
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    print(f"Updated {updated_count} SDG indicators in Master JSON.")

if __name__ == "__main__":
    main()
