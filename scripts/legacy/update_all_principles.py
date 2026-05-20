import requests
import json
import time
import re
import os
import sys
from collections import defaultdict

# Add project root to path for agrovoc_utils
sys.path.append(os.path.join(os.getcwd(), "api"))
from agrovoc_utils import execute_sparql

# Paths
ROOTS_FILE = "principles_indicators/massive_root_nodes.json"
MASTER_BALANCED = "principles_indicators/Ontology_index.json"
MASTER_BALANCED_TXT = "principles_indicators/Ontology_index.txt"

# --- 1. AGROVOC SPARQL EXPANDER ---
def expand_agrovoc(uri):
    query = f"""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX agrontology: <http://aims.fao.org/aos/agrontology#>
    SELECT DISTINCT ?rel ?term ?target WHERE {{
      {{ <{uri}> skos:narrower ?target . ?target skos:prefLabel ?term . BIND("Narrower" AS ?rel) }}
      UNION {{ <{uri}> skos:related ?target . ?target skos:prefLabel ?term . BIND("Related" AS ?rel) }}
      UNION {{ <{uri}> agrontology:affects ?target . ?target skos:prefLabel ?term . BIND("Affects" AS ?rel) }}
      FILTER (lang(?term) = "en")
    }}
    LIMIT 20
    """
    try:
        results = execute_sparql(query)
        if results and "results" in results:
            return results["results"]["bindings"]
    except: return []
    return []

# --- 2. OLS EXTRACTOR ---
def query_ols(keyword, ontology):
    url = f"https://www.ebi.ac.uk/ols4/api/search?q={keyword}&ontology={ontology.lower()}&rows=5"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return [{"label": i['label'], "uri": i['iri'], "source": ontology.upper()} for i in r.json()['response']['docs']]
    except: return []
    return []

def main():
    if not os.path.exists(ROOTS_FILE) or not os.path.exists(MASTER_BALANCED):
        print("Error: Required files missing.")
        return

    with open(ROOTS_FILE, 'r', encoding='utf-8') as f:
        roots_data = json.load(f)
    
    with open(MASTER_BALANCED, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    print("Starting Global Biophysical Expansion for all 13 Principles...")

    for principle, uris in roots_data.items():
        print(f"\nExpanding Principle: {principle}")
        
        # Ensure principle exists in master
        if principle not in master_data:
            master_data[principle] = {"sub_concepts": []}
            
        existing_uris = set()
        def collect_uris(nodes):
            for n in nodes:
                existing_uris.add(n['uri'])
                if 'sub_concepts' in n: collect_uris(n['sub_concepts'])
        collect_uris(master_data[principle].get('sub_concepts', []))

        # Process top 3 roots per principle for speed/coverage balance
        for uri in uris[:3]:
            print(f"  Root: {uri}")
            
            # A. AGROVOC Expansion
            relations = expand_agrovoc(uri)
            for row in relations:
                rel_label = row['term']['value']
                rel_uri = row['target']['value']
                rel_type = row['rel']['value']
                
                if rel_uri not in existing_uris:
                    master_data[principle]["sub_concepts"].append({
                        "label": rel_label,
                        "uri": rel_uri,
                        "source": f"AGROVOC_{rel_type}",
                        "sub_concepts": []
                    })
                    existing_uris.add(rel_uri)
            
            # B. OLS Expansion (ENVO)
            # Try to get label first or use last part of URI
            label_seed = uri.split('/')[-1]
            envo_terms = query_ols(label_seed, "envo")
            for term in envo_terms:
                if term['uri'] not in existing_uris:
                    master_data[principle]["sub_concepts"].append({
                        "label": term['label'],
                        "uri": term['uri'],
                        "source": "ENVO",
                        "sub_concepts": []
                    })
                    existing_uris.add(term['uri'])
            
            time.sleep(0.2)

    # Save Results
    with open(MASTER_BALANCED, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, indent=4)

    # Regenerate Summary TXT
    def write_node(node, level, lines):
        indent = "  " * level
        source = node.get("source", "AGROVOC")
        lines.append(f"{indent}- [{source}] {node['label']} ({node['uri']})\n")
        for child in node.get('sub_concepts', []):
            write_node(child, level + 1, lines)

    summary_lines = ["=== MASTER BALANCED AGROECOLOGY ONTOLOGY (Global Biophysical Update) ===\n"]
    summary_lines.append("Sources: AGROVOC, ENVO, GEMET, LANDVOC, UNBIS, HASSET, etc.\n\n")
    
    for p, content in master_data.items():
        summary_lines.append(f"\n[{p.upper()}]\n")
        for root in content.get('sub_concepts', []):
            write_node(root, 0, summary_lines)

    with open(MASTER_BALANCED_TXT, 'w', encoding='utf-8') as f:
        f.writelines(summary_lines)

    print("\nUpdate All Complete.")

if __name__ == "__main__":
    main()
