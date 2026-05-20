import requests
import json
import time
import re
import os
from collections import defaultdict

# --- CONFIGURATION ---
INDEX_FILE = "principles_indicators/agrovoc_complete_index.txt"
OUTPUT_FILE = "principles_indicators/input_reduction_biophysical_master.json"

# Biophysical Keywords for Input Reduction
BIOPHYSICAL_ROOTS = [
    "nitrogen", "phosphorus", "fertilizer", "pesticide", "urea", "nitrification", 
    "urease", "inhibitor", "biofertilizer", "rhizobium", "mycorrhiza", "mulch", 
    "tillage", "biomass", "compost", "manure", "biological control"
]

# --- 1. LOCAL AGROVOC PARSER ---
def get_roots_from_index(file_path, keywords):
    print(f"Searching local index for biophysical roots...")
    found = []
    if not os.path.exists(file_path):
        print(f"Local index file not found at {file_path}.")
        return found
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if any(k in line.lower() for k in keywords):
                    match = re.match(r"^(.*?)\s+\((http://aims\.fao\.org/aos/agrovoc/c_.*?)\)$", line)
                    if match:
                        found.append({"label": match.group(1), "uri": match.group(2)})
    except Exception as e:
        print(f"Error reading index: {e}")
    return found

# --- 2. AGROVOC SPARQL EXPANDER ---
def expand_agrovoc(uri):
    """Pulls the 6 core relations from AGROVOC."""
    endpoint = "https://agrovoc.fao.org/sparql"
    query = f"""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX agrontology: <http://aims.fao.org/aos/agrontology#>
    SELECT DISTINCT ?rel ?term WHERE {{
      {{ <{uri}> skos:narrower ?r . ?r skos:prefLabel ?term . BIND("Narrower" AS ?rel) }}
      UNION {{ <{uri}> skos:broader ?r . ?r skos:prefLabel ?term . BIND("Broader" AS ?rel) }}
      UNION {{ <{uri}> skos:related ?r . ?r skos:prefLabel ?term . BIND("Related" AS ?rel) }}
      UNION {{ <{uri}> skos:altLabel ?term . BIND("EntryTerm" AS ?rel) }}
      UNION {{ <{uri}> agrontology:isAffectedBy ?r . ?r skos:prefLabel ?term . BIND("AffectedBy" AS ?rel) }}
      UNION {{ <{uri}> agrontology:isIncludedIn ?r . ?r skos:prefLabel ?term . BIND("IncludedIn" AS ?rel) }}
      FILTER (lang(?term) = "en")
    }}
    """
    try:
        r = requests.post(endpoint, data={'query': query}, headers={'Accept': 'application/sparql-results+json'}, timeout=15)
        return r.json()['results']['bindings'] if r.status_code == 200 else []
    except: return []

# --- 3. ENVO & SWEET REST EXTRACTOR (via EBI OLS) ---
def query_ols(keyword, ontology):
    """Queries EBI OLS for ENVO or SWEET terms."""
    url = f"https://www.ebi.ac.uk/ols4/api/search?q={keyword}&ontology={ontology.lower()}&rows=5"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return [{"label": i['label'], "uri": i['iri']} for i in r.json()['response']['docs']]
    except: return []
    return []

# --- MAIN PIPELINE ---
def main():
    # Step 1: Get Biophysical Roots from your local file
    roots = get_roots_from_index(INDEX_FILE, BIOPHYSICAL_ROOTS)
    
    master_dict = {
        "agrovoc_expanded": defaultdict(list),
        "envo_scientific": [],
        "sweet_physical": []
    }

    print(f"Found {len(roots)} biophysical roots. Starting expansion...")

    # Step 2: Expand AGROVOC (Top 20 roots for speed as requested in template)
    for root in roots[:20]:
        print(f"  Expanding AGROVOC: {root['label']}")
        relations = expand_agrovoc(root['uri'])
        for row in relations:
            rel, term = row['rel']['value'], row['term']['value'].lower()
            if term not in master_dict["agrovoc_expanded"][rel]:
                master_dict["agrovoc_expanded"][rel].append(term)
        
        # Step 3: Fetch Scientific counterparts in ENVO/SWEET
        master_dict["envo_scientific"].extend(query_ols(root['label'], "envo"))
        master_dict["sweet_physical"].extend(query_ols(root['label'], "sweet"))
        
        time.sleep(0.3) # Politeness

    # Final Cleanup & Deduplication
    master_dict["envo_scientific"] = [dict(t) for t in {tuple(d.items()) for d in master_dict["envo_scientific"]}]
    master_dict["sweet_physical"] = [dict(t) for t in {tuple(d.items()) for d in master_dict["sweet_physical"]}]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(master_dict, f, indent=4)
    
    print(f"\nSuccess! 100+ Biophysical terms extracted to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
