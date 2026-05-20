import requests
import json
import os
import time

# Configuration
OUTPUT_DIR = "principles_indicators"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "multi_ontology_mapping.json")

# Principle-Keyword Map (Shared for all sources)
SEARCH_MAP = {
    "Participation": ["participation", "community development", "governance", "democracy"],
    "Fairness": ["social justice", "equality", "human rights", "equity", "poverty"],
    "Co-creation of Knowledge": ["education", "traditional knowledge", "research", "learning"],
    "Social Values and Diets": ["food security", "nutrition", "culture", "diet"],
    "Connectivity": ["trade", "markets", "networks", "infrastructure"],
    "Land Governance": ["land tenure", "property", "policy", "law", "legislation"],
    "Economic Diversification": ["livelihoods", "employment", "income", "diversification"],
    "Recycling": ["waste", "recycling", "biomass", "circular economy"],
    "Synergy": ["cooperation", "integration", "ecosystem services"],
    "Biodiversity": ["biodiversity", "species", "conservation", "ecology"],
    "Soil Health": ["soil", "fertility", "erosion", "organic matter"],
    "Animal Health": ["animal welfare", "livestock", "veterinary"],
    "Input Reduction": ["pesticides", "fertilizers", "efficiency", "sustainable agriculture"]
}

def search_gemet(keyword):
    """GEMET API (Eionet)"""
    url = f"https://www.eionet.europa.eu/gemet/api/getConceptsMatchingKeywordByAutocompletion?word={keyword}&language=en"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return [{"label": i['label'], "uri": i['uri'], "source": "GEMET"} for i in r.json()]
    except: return []
    return []

def search_ols(keyword, ontology):
    """EBI OLS (ENVO, SWEET, etc.)"""
    url = f"https://www.ebi.ac.uk/ols/api/search?q={keyword}&ontology={ontology.lower()}&rows=10"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return [{"label": i['label'], "uri": i['iri'], "source": ontology.upper()} for i in r.json()['response']['docs']]
    except: return []
    return []

def fetch_all():
    results = {}
    print("Starting Multi-Ontology Fetch (GEMET, ENVO, SWEET)...")
    
    for principle, keywords in SEARCH_MAP.items():
        print(f"Processing: {principle}")
        results[principle] = []
        seen_uris = set()
        
        for keyword in keywords:
            print(f"  Searching '{keyword}'...")
            # GEMET
            gemet_matches = search_gemet(keyword)
            for m in gemet_matches:
                if m['uri'] not in seen_uris:
                    results[principle].append(m)
                    seen_uris.add(m['uri'])
            
            # ENVO
            envo_matches = search_ols(keyword, "envo")
            for m in envo_matches:
                if m['uri'] not in seen_uris:
                    results[principle].append(m)
                    seen_uris.add(m['uri'])
            
            # SWEET
            sweet_matches = search_ols(keyword, "sweet")
            for m in sweet_matches:
                if m['uri'] not in seen_uris:
                    results[principle].append(m)
                    seen_uris.add(m['uri'])
            
            time.sleep(0.2)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    
    total = sum(len(v) for v in results.values())
    print(f"\nSaved {total} terms to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_all()
