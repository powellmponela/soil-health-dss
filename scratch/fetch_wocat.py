import requests
import json
import os
import sys

# Ensure console can handle UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = "https://qcat.wocat.net/en/api/v2/"
TECH_URL = f"{BASE_URL}technologies/?format=json&filter__qg_location__country=country_NPL"
APP_URL = f"{BASE_URL}approaches/?format=json&filter__qg_location__country=country_NPL"

OFFLINE_DIR = "principles_indicators/offline_storage/wocat"

def fetch_qcat(url, filename):
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            os.makedirs(OFFLINE_DIR, exist_ok=True)
            with open(os.path.join(OFFLINE_DIR, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Saved to {filename}")
            return data
        else:
            print(f"Error {response.status_code}")
    except Exception as e:
        # Don't print the whole exception if it contains bad characters
        print(f"Request failed for {filename}")
    return None

def main():
    tech_data = fetch_qcat(TECH_URL, "nepal_technologies.json")
    app_data = fetch_qcat(APP_URL, "nepal_approaches.json")
    
    if app_data and 'results' in app_data:
        social_terms = []
        for result in app_data['results']:
            name = result.get('name', '')
            if name: social_terms.append(name)
        
        with open(os.path.join(OFFLINE_DIR, "social_indicators.txt"), 'w', encoding='utf-8') as f:
            f.write("\n".join(social_terms))
        print(f"Extracted {len(social_terms)} indicators.")

if __name__ == "__main__":
    main()
