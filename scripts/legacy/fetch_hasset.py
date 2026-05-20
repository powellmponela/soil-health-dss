import requests
import json
import os
import time
import xml.etree.ElementTree as ET

# Configuration
HASSET_API_BASE = "https://vocabularyserver.com/hasset/services.php"
OUTPUT_DIR = "principles_indicators"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "hasset_mapping.json")

# Principles to search in HASSET (Expanded for high-resolution social dimensions)
PRINCIPLE_SEARCH_MAP = {
    "Participation": [
        "participation", "collective action", "community development", "social organization", 
        "empowerment", "inclusion", "decision making", "governance", "democracy"
    ],
    "Fairness": [
        "social justice", "equality", "human rights", "equity", "gender equality", 
        "labour rights", "poverty", "ethical trade", "social protection", "distributive justice"
    ],
    "Co-creation of Knowledge": [
        "traditional knowledge", "indigenous knowledge", "action research", "learning", 
        "education", "knowledge transfer", "local wisdom", "farmer-to-farmer"
    ],
    "Social Values and Diets": [
        "food culture", "dietary habits", "food security", "nutrition", "consumer behavior", 
        "cultural heritage", "traditional food", "food systems"
    ],
    "Connectivity": [
        "market access", "trade relations", "value chains", "power relations", 
        "social networks", "economic relations", "transparency"
    ],
    "Land Governance": [
        "land tenure", "property rights", "land reform", "environmental law", 
        "common land", "natural resource management", "policy making", "legislation"
    ],
    "Economic Diversification": [
        "livelihoods", "rural employment", "income distribution", "microfinance", 
        "entrepreneurship", "economic development", "job creation"
    ],
    "Recycling": ["waste management", "circular economy", "biomass", "resource recovery"],
    "Synergy": ["cooperation", "integrated management", "interdisciplinary research"],
    "Biodiversity": ["nature conservation", "environmental protection", "genetic resources"]
}

def search_hasset(query):
    params = {
        "task": "search",
        "arg": query
    }
    try:
        response = requests.get(HASSET_API_BASE, params=params, timeout=15)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        results = []
        for term in root.findall(".//term"):
            term_id = term.find("term_id").text
            label = term.find("string").text
            results.append({
                "label": label,
                "uri": f"https://vocabularyserver.com/hasset/index.php?tema={term_id}",
                "source": "HASSET"
            })
        return results
    except Exception as e:
        print(f"Error searching HASSET for '{query}': {e}")
        return []

def fetch_hasset():
    results = {}
    
    print("Fetching HASSET Terms via TemaTres API...")
    
    for principle, keywords in PRINCIPLE_SEARCH_MAP.items():
        print(f"Processing Principle: {principle}")
        results[principle] = []
        seen_ids = set()
        
        for keyword in keywords:
            print(f"  Searching for '{keyword}'...")
            matches = search_hasset(keyword)
            
            for match in matches:
                if match["uri"] not in seen_ids:
                    results[principle].append(match)
                    seen_ids.add(match["uri"])
            
            time.sleep(0.5)
            
    # Save the results
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
        
    print(f"\nSaved {sum(len(v) for v in results.values())} HASSET terms to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_hasset()
