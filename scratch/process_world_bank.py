import csv
import json
import os
import re

csv_file = r'c:\SOIL HEALTH\principles_indicators\offline_storage\world_bank\World_Bank_Master_Glossary_All_Databases.csv'
output_dir = r'c:\SOIL HEALTH\principles_indicators\offline_storage\world_bank'

terms_json = os.path.join(output_dir, 'terms.json')
terms_txt = os.path.join(output_dir, 'terms.txt')

keywords = {
    "Economic Diversification": ["poverty", "income", "employment", "market", "economic", "trade", "finance", "gdp", "investment", "credit"],
    "Land Governance": ["land", "tenure", "property", "ownership", "rights", "policy", "governance", "institution", "law", "regulation"],
    "Connectivity": ["infrastructure", "transport", "road", "internet", "communication", "electricity", "energy access", "supply chain"],
    "Fairness": ["inequality", "equity", "gender", "women", "youth", "vulnerable", "social protection", "wages", "labor", "human rights"],
    "Participation": ["community", "cooperative", "association", "group", "collective", "participatory", "decentralization", "local"],
    "Co-creation of Knowledge": ["education", "school", "literacy", "training", "extension", "research", "innovation", "skills", "knowledge"],
    "Social Values and Diets": ["health", "nutrition", "food security", "diet", "sanitation", "water", "calorie", "malnutrition", "hunger"],
    "Biodiversity": ["forest", "conservation", "biodiversity", "species", "ecosystem", "habitat", "wildlife", "genetic"],
    "Soil Health": ["soil", "land degradation", "erosion", "desertification", "fertilizer", "nutrient"],
    "Input Reduction": ["efficiency", "water use", "energy use", "pesticide", "chemical", "reduction", "optimization"],
    "Recycling": ["waste", "biomass", "recycle", "circular", "residue", "compost"],
    "Synergy": ["integration", "agroforestry", "mixed farming", "system", "holistic"],
    "Animal Health": ["livestock", "animal", "veterinary", "disease", "poultry", "cattle", "pasture"]
}

extracted = []

def process_world_bank():
    print(f"Processing World Bank dataset: {csv_file}")
    
    with open(csv_file, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        
        count = 0
        for row in reader:
            indicator_id = row.get('indicator_id', '').strip()
            indicator_name = row.get('indicator', '').strip()
            indicator_desc = row.get('indicator_desc', '').strip()
            topics = row.get('topics', '').strip()
            
            if not indicator_name:
                continue
                
            text_to_search = f"{indicator_name} {indicator_desc} {topics}".lower()
            
            mapped_principles = []
            for principle, kws in keywords.items():
                if any(re.search(r'\b' + kw + r'\b', text_to_search) for kw in kws):
                    mapped_principles.append(principle)
            
            if mapped_principles:
                # Format label cleanly
                label = indicator_name
                # Some names have extra formatting, let's keep it simple
                extracted.append({
                    "uri": f"world_bank:{indicator_id}" if indicator_id else f"world_bank:idx_{count}",
                    "label": label,
                    "principles": list(set(mapped_principles)),
                    "source": "World_Bank"
                })
            count += 1
            
    print(f"Scanned {count} rows. Extracted {len(extracted)} relevant indicators.")
    
    with open(terms_json, 'w', encoding='utf-8') as f:
        json.dump(extracted, f, indent=4)
        
    with open(terms_txt, 'w', encoding='utf-8') as f:
        for item in extracted:
            f.write(f"{item['label']} | {','.join(item['principles'])}\n")
            
    print(f"Saved to {terms_json} and {terms_txt}")

if __name__ == "__main__":
    process_world_bank()
