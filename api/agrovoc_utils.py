import requests
import json
import os

SEARCH_API = "https://agrovoc.fao.org/skosmos/rest/v1/search"
SPARQL_ENDPOINT = "https://agrovoc.fao.org/sparql"

def download_agrovoc_terms(principle_synonyms):
    """
    Downloads Agrovoc terms for a set of principle synonyms using REST API with wildcard fallback.
    """
    results = {}
    for principle, synonyms in principle_synonyms.items():
        print(f"Fetching terms for principle: {principle}")
        principle_terms = []
        for synonym in synonyms:
            print(f"  Processing: {synonym}...")
            
            # Helper to search with a specific query string
            def search_agrovoc(q):
                params = {
                    "query": q,
                    "lang": "en",
                    "vocab": "agrovoc"
                }
                try:
                    import time
                    time.sleep(0.5) # Sleep to avoid overloading
                    response = requests.get(SEARCH_API, params=params, timeout=20)
                    if response.status_code == 200:
                        return response.json().get('results', [])
                except Exception as e:
                    print(f"    Error: {e}")
                return []

            # 1. Try exact search first
            found_items = search_agrovoc(synonym)
            
            # 2. If nothing found, try wildcard search
            if not found_items:
                print(f"    No exact match, trying wildcard...")
                found_items = search_agrovoc(f"{synonym}*")
            
            if found_items:
                print(f"    Found {len(found_items)} results")
                # Look for exact prefLabel match first
                best_match = None
                for item in found_items:
                    if item.get('prefLabel', '').lower() == synonym.lower():
                        best_match = item
                        break
                
                # If no exact prefLabel, take the first result
                if not best_match:
                    best_match = found_items[0]
                
                principle_terms.append({
                    "label": best_match['prefLabel'],
                    "uri": best_match['uri']
                })
            else:
                print(f"    No results found even with wildcard.")
        
        results[principle] = principle_terms
    
    return results

def search_agrovoc_contains(keyword, limit=500):
    """
    Finds all Agrovoc terms containing the keyword using SPARQL.
    """
    print(f"Pulling all terms containing: {keyword}")
    query = f"""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT DISTINCT ?concept ?label
    WHERE {{
      ?concept a skos:Concept .
      ?concept skos:prefLabel ?label .
      FILTER (lang(?label) = "en")
      FILTER (CONTAINS(LCASE(STR(?label)), "{keyword.lower()}"))
    }}
    LIMIT {limit}
    """
    return execute_sparql(query)

def get_collection_members(collection_uri):
    """
    Fetches all members of a specific SKOS Collection.
    """
    print(f"Pulling members for collection: {collection_uri}")
    query = f"""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT DISTINCT ?member ?label
    WHERE {{
      <{collection_uri}> skos:member ?member .
      ?member skos:prefLabel ?label .
      FILTER (lang(?label) = "en")
    }}
    """
    results = execute_sparql(query)
    # The execute_sparql returns list of dicts with 'concept' and 'label'
    # but the query above uses '?member'. Let's standardize.
    for r in results:
        if 'member' in r:
            r['concept'] = r.pop('member')
    return results

def get_concept_info(uri):
    """
    Fetches broader and related concepts for a given URI.
    """
    print(f"    Fetching details for: {uri}")
    query = f"""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?property ?target ?label
    WHERE {{
      {{ 
        <{uri}> skos:broader ?target . 
        BIND("broader" AS ?property) 
      }}
      UNION
      {{ 
        <{uri}> skos:related ?target . 
        BIND("related" AS ?property) 
      }}
      ?target skos:prefLabel ?label .
      FILTER (lang(?label) = "en")
    }}
    """
    results = execute_sparql(query)
    info = {"broader": [], "related": [], "narrower": [], "definition": "", "scopeNote": ""}
    for r in results:
        prop = r.get('property')
        if prop in info:
            info[prop].append({
                "label": r.get('label'),
                "uri": r.get('target')
            })
    return info

def get_concepts_info_batch(uris):
    """
    Fetches broader and related concepts for a list of URIs in batches.
    """
    if not uris: return {}
    
    all_info = {uri: {"broader": [], "related": [], "narrower": [], "definition": "", "scopeNote": ""} for uri in uris}
    
    # Process in batches of 50 to avoid huge queries
    batch_size = 50
    for i in range(0, len(uris), batch_size):
        batch = uris[i:i+batch_size]
        print(f"    Fetching details for batch {i//batch_size + 1} ({len(batch)} terms)...")
        
        values_str = " ".join([f"<{uri}>" for uri in batch])
        query = f"""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX skosxl: <http://www.w3.org/2008/05/skos-xl#>
        PREFIX agro: <http://aims.fao.org/aos/agrovoc/>
        PREFIX agrontology: <http://aims.fao.org/aos/agrontology#>
        SELECT ?concept ?property ?target ?label ?value
        WHERE {{
          VALUES ?concept {{ {values_str} }}
          {{ 
            ?concept ?prop ?target .
            FILTER(?prop IN (
              skos:broader, skos:narrower, skos:related,
              agro:isAffectedBy, agro:makeUseOf, agro:usesProcess,
              agro:hasObjectOfActivity, agro:isComponentOf,
              agro:affects, agro:isAchievedByMeansOf,
              agrontology:isAffectedBy, agrontology:makeUseOf, agrontology:usesProcess,
              agrontology:hasObjectOfActivity, agrontology:isComponentOf,
              agrontology:affects, agrontology:isAchievedByMeansOf
            ))
            OPTIONAL {{ 
              ?target skos:prefLabel ?label . 
              FILTER(lang(?label) = "en")
            }}
            BIND(STRAFTER(STR(?prop), "#") AS ?p_name)
            BIND(IF(?p_name = "", STRAFTER(STR(?prop), "agrovoc/"), ?p_name) AS ?property)
          }}
          UNION
          {{
            ?concept skos:altLabel ?value .
            FILTER(lang(?value) = "en")
            BIND("entryTerm" AS ?property)
          }}
          UNION
          {{
            ?collection skos:member ?concept .
            ?collection skos:prefLabel ?label .
            FILTER(lang(?label) = "en")
            BIND(?collection AS ?target)
            BIND("belongsToGroup" AS ?property)
          }}
          UNION
          {{
            ?concept skos:definition ?def .
            ?def skos:definitionVal ?value .
            FILTER(lang(?value) = "en")
            BIND("definition" AS ?property)
          }}
          UNION
          {{
            ?concept skos:scopeNote ?value .
            FILTER(lang(?value) = "en")
            BIND("scopeNote" AS ?property)
          }}
        }}
        """
        results = execute_sparql(query)
        for r in results:
            uri = r.get('uri') or r.get('concept')
            prop = r.get('property')
            if uri in all_info:
                if prop in ["broader", "related", "narrower", "isAffectedBy", "makeUseOf", "usesProcess", "hasObjectOfActivity", "isComponentOf", "belongsToGroup", "affects", "isAchievedByMeansOf"]:
                    if prop not in all_info[uri] or isinstance(all_info[uri][prop], str):
                        all_info[uri][prop] = []
                    all_info[uri][prop].append({
                        "label": r.get('label') or r.get('target').split('/')[-1],
                        "uri": r.get('target')
                    })
                elif prop == "entryTerm":
                    if "entryTerms" not in all_info[uri]: all_info[uri]["entryTerms"] = []
                    all_info[uri]["entryTerms"].append(r.get('value'))
                elif prop in ["definition", "scopeNote"]:
                    all_info[uri][prop] = r.get('value')
    return all_info

def execute_sparql(query):
    """
    Helper to execute SPARQL queries.
    """
    headers = {"Accept": "application/sparql-results+json"}
    try:
        response = requests.get(SPARQL_ENDPOINT, params={"query": query}, headers=headers, timeout=60)
        if response.status_code == 200:
            data = response.json()
            results = []
            for row in data['results']['bindings']:
                # Handle different variable names dynamically
                item = {}
                for var in row:
                    item[var] = row[var]['value']
                
                # Standardize to 'uri' and 'label' if needed, but let's just return raw mapping
                if 'concept' in item: item['uri'] = item.pop('concept')
                if 'member' in item: item['uri'] = item.pop('member')
                if 'label' in item: item['label'] = item['label']
                results.append(item)
            return results
    except Exception as e:
        print(f"  SPARQL Error: {e}")
    return []
