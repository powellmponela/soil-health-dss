import requests
import json
import os
from typing import List, Dict, Optional

CACHE_DIR = os.path.join(os.path.dirname(__file__), "data")
CACHE_FILE = os.path.join(CACHE_DIR, "ontology_cache.json")
# We'll use a single mapping file or split by source
MAP_FILE = os.path.join(CACHE_DIR, "agrovoc_principles_map.json") 

_PRINCIPLES_MAP = None

def load_cache() -> Dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache: Dict):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

def load_principles_map() -> Dict:
    global _PRINCIPLES_MAP
    if _PRINCIPLES_MAP is not None:
        return _PRINCIPLES_MAP
    
    if os.path.exists(MAP_FILE):
        try:
            with open(MAP_FILE, "r", encoding="utf-8") as f:
                _PRINCIPLES_MAP = json.load(f)
                return _PRINCIPLES_MAP
        except Exception as e:
            print(f"Error loading principles map: {e}")
            return {}
    return {}

def get_principles_for_uri(uri: str, label: str) -> List[str]:
    """
    Returns principles for a given URI using the pre-computed map.
    """
    p_map = load_principles_map()
    if uri in p_map:
        return p_map[uri].get("principles", [])
    
    # Fallback: Basic keyword matching for unknown URIs
    principles = []
    # (Implementation of basic matching logic if needed)
    return principles

class OntologyManager:
    @staticmethod
    def search_agrovoc(term: str) -> Optional[Dict]:
        url = "https://agrovoc.fao.org/skosmos/rest/v1/search"
        params = {"query": term, "lang": "en", "unique": "true", "vocab": "agrovoc"}
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    return {"label": results[0].get("prefLabel"), "uri": results[0].get("uri"), "source": "AGROVOC"}
        except: pass
        return None

    @staticmethod
    def search_gemet(term: str) -> Optional[Dict]:
        # GEMET REST API
        url = f"https://www.eionet.europa.eu/gemet/getConceptsMatchingRegexByThesaurus"
        params = {"regex": term, "language": "en", "thesaurus_uri": "http://www.eionet.europa.eu/gemet/concept/"}
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                results = response.json()
                if results:
                    res0 = results[0]
                    if isinstance(res0, dict):
                        uri = res0.get("uri", "")
                        # Try to get a better label if available
                        label = res0.get("preferredLabel", {}).get("string", term)
                        return {"label": label, "uri": uri, "source": "GEMET"}
                    return {"label": term, "uri": res0, "source": "GEMET"}
        except: pass
        return None

    @staticmethod
    def search_envo(term: str) -> Optional[Dict]:
        # OLS API for ENVO
        url = "https://www.ebi.ac.uk/ols/api/search"
        params = {"q": term, "ontology": "envo", "exact": "true"}
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                docs = response.json().get("response", {}).get("docs", [])
                if docs:
                    return {"label": docs[0].get("label"), "uri": docs[0].get("iri"), "source": "ENVO"}
        except: pass
        return None

    @staticmethod
    def search_unbis(term: str) -> Optional[Dict]:
        # UNBIS SPARQL
        url = "https://metadata.un.org/sparql"
        query = f"""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?concept ?label WHERE {{
          ?concept a skos:Concept ; skos:prefLabel ?label .
          FILTER(regex(?label, "^{term}$", "i"))
          FILTER(lang(?label) = "en")
        }} LIMIT 1
        """
        try:
            response = requests.get(url, params={"query": query, "format": "json"}, timeout=5)
            if response.status_code == 200:
                results = response.json().get("results", {}).get("bindings", [])
                if results:
                    return {"label": results[0]["label"]["value"], "uri": results[0]["concept"]["value"], "source": "UNBIS"}
        except: pass
        return None

    @staticmethod
    def search_unesco(term: str) -> Optional[Dict]:
        # UNESCO SPARQL
        url = "http://vocabularies.unesco.org/sparql"
        query = f"""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?concept ?label WHERE {{
          ?concept a skos:Concept ; skos:prefLabel ?label .
          FILTER(regex(?label, "^{term}$", "i"))
          FILTER(lang(?label) = "en")
        }} LIMIT 1
        """
        try:
            response = requests.get(url, params={"query": query, "format": "json"}, timeout=5)
            if response.status_code == 200:
                results = response.json().get("results", {}).get("bindings", [])
                if results:
                    return {"label": results[0]["label"]["value"], "uri": results[0]["concept"]["value"], "source": "UNESCO"}
        except: pass
        return None

def search_ontologies(term: str) -> Optional[Dict]:
    """
    Searches across multiple ontologies and returns the first valid match.
    """
    cache = load_cache()
    if term.lower() in cache:
        return cache[term.lower()]

    # Priority order: AGROVOC -> ENVO -> GEMET
    match = OntologyManager.search_agrovoc(term)
    if not match:
        match = OntologyManager.search_envo(term)
    if not match:
        match = OntologyManager.search_gemet(term)

    if match:
        # Enforce HLPE Principle Mapping
        match["principles"] = get_principles_for_uri(match["uri"], match["label"])
        
        cache[term.lower()] = match
        save_cache(cache)
        return match
    
    return None

def batch_enrich_terms(terms: List[str]) -> List[Dict]:
    enriched = []
    for term in terms:
        match = search_ontologies(term)
        if match:
            enriched.append(match)
    return enriched
