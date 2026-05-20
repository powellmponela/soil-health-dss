import os
import json
import sys
import time
import requests

# Add the project root to sys.path so 'api' is resolvable at runtime
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from api.agrovoc_utils import execute_sparql

ROOT_NODES_FILE = os.path.join(os.getcwd(), "principles_indicators", "massive_root_nodes.json")
if os.path.exists(ROOT_NODES_FILE):
    with open(ROOT_NODES_FILE, 'r', encoding='utf-8') as f:
        ROOT_NODES = json.load(f)
else:
    print(f"Warning: {ROOT_NODES_FILE} not found. Using empty roots.")
    ROOT_NODES = {}

OUTPUT_DIR = "principles_indicators"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "advanced_agrovoc_mapping.json")

def get_children_batch(uris):
    """
    Fetches narrower, component, included, related, and interaction terms for a batch of URIs.
    """
    if not uris: return {}
    
    values_str = " ".join([f"<{uri}>" for uri in uris])
    query = f"""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX agrontology: <http://aims.fao.org/aos/agrontology#>
    PREFIX agro: <http://aims.fao.org/aos/agrovoc/>
    
    SELECT DISTINCT ?parent ?child ?label ?prop
    WHERE {{
      VALUES ?parent {{ {values_str} }}
      {{ ?parent skos:narrower ?child . BIND("narrower" AS ?prop) }}
      UNION
      {{ ?parent skos:related ?child . BIND("related" AS ?prop) }}
      UNION
      {{ ?parent agrontology:hasComponent ?child . BIND("component" AS ?prop) }}
      UNION
      {{ ?parent agrontology:includes ?child . BIND("includes" AS ?prop) }}
      UNION
      {{ ?parent agrontology:affects ?child . BIND("affects" AS ?prop) }}
      UNION
      {{ ?parent agrontology:isAffectedBy ?child . BIND("isAffectedBy" AS ?prop) }}
      UNION
      {{ ?parent agrontology:isAchievedByMeansOf ?child . BIND("achievedBy" AS ?prop) }}
      
      ?child skos:prefLabel ?label .
      FILTER (lang(?label) = 'en')
    }}
    """
    
    results = execute_sparql(query)
    mapping = {}
    for r in results:
        parent = r['parent']
        if parent not in mapping: mapping[parent] = []
        mapping[parent].append({
            "uri": r['child'],
            "label": r['label'],
            "relationship": r['prop'],
            "sub_concepts": []
        })
    return mapping

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    master_map = {}
    
    # We will build the tree level by level for all roots at once
    print("Initializing Master AGROVOC Mapping from Root Nodes...")
    
    # 1. Initialize root objects
    for principle, root_uris in ROOT_NODES.items():
        master_map[principle] = {
            "label": principle,
            "sub_concepts": []
        }
        for uri in root_uris:
            master_map[principle]["sub_concepts"].append({
                "uri": uri,
                "label": "Root", # To be fetched
                "sub_concepts": []
            })

    # 2. Iteratively fetch levels
    current_level_nodes = []
    for p in master_map.values():
        current_level_nodes.extend(p["sub_concepts"])

    max_depth = 3
    for depth in range(1, max_depth + 1):
        print(f"Processing Level {depth}...")
        
        # 1. Fetch labels for nodes that don't have them (like roots in first pass)
        nodes_needing_labels = [n for n in current_level_nodes if n['label'] == "Root"]
        if nodes_needing_labels:
            uris = list(set([n['uri'] for n in nodes_needing_labels]))
            values_str = " ".join([f"<{u}>" for u in uris])
            q = f"PREFIX skos: <http://www.w3.org/2004/02/skos/core#> SELECT ?uri ?label WHERE {{ VALUES ?uri {{ {values_str} }} ?uri skos:prefLabel ?label . FILTER(lang(?label)='en') }}"
            labels = execute_sparql(q)
            label_map = {r['uri']: r['label'] for r in labels}
            for n in nodes_needing_labels:
                n['label'] = label_map.get(n['uri'], n['uri'].split('/')[-1])

        # 2. Collect all URIs at this level that need children
        uris_to_query = [node['uri'] for node in current_level_nodes]
        
        all_children_mapping = {}
        batch_size = 50
        for i in range(0, len(uris_to_query), batch_size):
            batch = uris_to_query[i:i+batch_size]
            print(f"  Querying batch {i//batch_size + 1} ({len(batch)} URIs)...")
            all_children_mapping.update(get_children_batch(batch))
            time.sleep(0.2)
        
        # Assign children
        next_level_nodes = []
        for node in current_level_nodes:
            children = all_children_mapping.get(node['uri'], [])
            node['sub_concepts'] = children
            next_level_nodes.extend(children)
        
        current_level_nodes = next_level_nodes
        if not current_level_nodes:
            break

    # 3. Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(master_map, f, indent=2)
    
    print(f"\nMapping complete. Saved to {OUTPUT_FILE}")

    # 4. Generate summary TXT
    summary_file = os.path.join(OUTPUT_DIR, "complete_agrovoc_summary.txt")
    
    def write_tree(f, node, indent=0):
        spacing = "  " * indent
        rel = f" [{node['relationship']}]" if node.get('relationship') else ""
        if node.get('uri'):
            f.write(f"{spacing}- {node['label']}{rel} ({node['uri']})\n")
        else:
            f.write(f"{spacing}{node['label']}\n")
            
        for sub in node.get('sub_concepts', []):
            write_tree(f, sub, indent + 1)

    with open(summary_file, "w", encoding="utf-8") as f:
        for principle, data in master_map.items():
            f.write(f"=== {principle} ===\n")
            write_tree(f, data)
            f.write("\n" + "="*50 + "\n\n")
    
    print(f"Saved summary to {summary_file}")

if __name__ == "__main__":
    main()
