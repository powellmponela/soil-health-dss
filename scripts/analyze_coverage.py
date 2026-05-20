import json
import os

# Path to the production master ontology
MASTER_ONTOLOGY = r"c:\SOIL HEALTH\principles_indicators\offline_storage\master_agroecological_ontology.json"

def show_coverage():
    if not os.path.exists(MASTER_ONTOLOGY):
        print(f"Error: {MASTER_ONTOLOGY} not found.")
        return

    with open(MASTER_ONTOLOGY, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"{'Agroecological Principle':<40} | {'Terms':<6}")
    print("-" * 50)

    total_terms = 0
    
    # Sort by principle number
    principles = sorted(data.keys(), key=lambda x: int(x.split('.')[0]) if '.' in x else 999)

    for principle in principles:
        terms = data[principle]
        count = len(terms)
        total_terms += count
        print(f"{principle:<40} | {count:<6}")

    print("-" * 50)
    print(f"{'TOTAL INTEGRATED TERMS':<40} | {total_terms:<6}")

if __name__ == "__main__":
    show_coverage()
