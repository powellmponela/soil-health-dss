import json
import os
import re
import csv

# Paths
WB_COMPACT_SOURCE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\world_bank\world_bank_ontology_compact.json"
WOCAT_SOURCE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\wocat_ontology_compact.json"
TAPE_CROSSWALK = r"c:\SOIL HEALTH\principles_indicators\offline_storage\tape\TAPE_indicators_13_principles_crosswalk.csv"
HASSET_SOURCE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\hasset\hasset_ontology_compact.json"
MASTER_OUTPUT = r"c:\SOIL HEALTH\principles_indicators\offline_storage\master_agroecological_ontology.json"

PRINCIPLE_MAP = {
    "1. Recycling": "1. Recycling",
    "2. Input Reduction": "2. Input Reduction",
    "3. Soil Health": "3. Soil Health",
    "4. Animal Health": "4. Animal Health",
    "5. Biodiversity": "5. Biodiversity",
    "6. Synergy": "6. Synergy",
    "7. Economic Diversification": "7. Economic Diversification",
    "8. Co-creation of Knowledge": "8. Co-creation of Knowledge",
    "9. Social Values & Diets": "9. Social Values & Diets",
    "10. Fairness": "10. Fairness",
    "11. Connectivity": "11. Connectivity",
    "12. Land & Natural Resource Governance": "12. Land & Natural Resource Governance",
    "13. Participation": "13. Participation"
}

def clean_term(term):
    if not term: return ""
    term = re.sub(r'^\([a-z0-9]+\)[\s]*', '', term)
    term = re.sub(r'^[a-z0-9]\.[\s]*', '', term)
    return term.strip()

def get_target_p(p_name):
    if not p_name: return None
    p_name_low = p_name.lower().replace("&", "and")
    for k, v in PRINCIPLE_MAP.items():
        k_low = k.lower().replace("&", "and")
        if p_name_low in k_low or k_low in p_name_low:
            return v
    return None

def main():
    print("Starting master ontology synchronization (Integrated: WB, WOCAT, TAPE, HASSET)...")
    
    master_ontology = {}

    # 1. Load World Bank Compact
    if os.path.exists(WB_COMPACT_SOURCE):
        with open(WB_COMPACT_SOURCE, "r", encoding="utf-8") as f:
            wb_data = json.load(f)
            for p_name, content in wb_data.items():
                target_p = get_target_p(p_name)
                if target_p:
                    if target_p not in master_ontology: master_ontology[target_p] = set()
                    if isinstance(content, list):
                        for ind in content:
                            if isinstance(ind, dict) and ind.get("label"):
                                master_ontology[target_p].add(ind["label"].capitalize())
                    elif isinstance(content, dict):
                        for t in content.get("key_terms", []):
                            master_ontology[target_p].add(t.capitalize())
                        for ind in content.get("indicators", []):
                            if ind.get("label"):
                                master_ontology[target_p].add(ind["label"].capitalize())

    # 2. Load WOCAT
    if os.path.exists(WOCAT_SOURCE):
        with open(WOCAT_SOURCE, "r", encoding="utf-8") as f:
            wocat_data = json.load(f)
            for p_name, terms in wocat_data.items():
                target_p = get_target_p(p_name)
                if target_p:
                    if target_p not in master_ontology: master_ontology[target_p] = set()
                    for t in terms:
                        master_ontology[target_p].add(clean_term(t).capitalize())

    # 3. Load TAPE Crosswalk
    if os.path.exists(TAPE_CROSSWALK):
        with open(TAPE_CROSSWALK, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                term = row.get("term")
                p_name = row.get("principle")
                if term and p_name:
                    target_p = get_target_p(p_name)
                    if target_p:
                        if target_p not in master_ontology: master_ontology[target_p] = set()
                        master_ontology[target_p].add(term.capitalize())

    # 4. Load HASSET
    if os.path.exists(HASSET_SOURCE):
        with open(HASSET_SOURCE, "r", encoding="utf-8") as f:
            hasset_data = json.load(f)
            terms_list = hasset_data.get("terms", [])
            for c in terms_list:
                rel = c.get("relevance_for_agroecology_ontology")
                if rel in ["core", "supporting"]:
                    label = c.get("label", "").capitalize()
                    alignments = c.get("agroecology_alignment", [])
                    for a in alignments:
                        p_name = a.get("principle")
                        if p_name and label:
                            target_p = get_target_p(p_name)
                            if target_p:
                                if target_p not in master_ontology: master_ontology[target_p] = set()
                                master_ontology[target_p].add(label)

    # 5. Final Processing and Sorting
    sorted_master = {}
    p_keys = sorted(master_ontology.keys(), key=lambda x: int(re.match(r"(\d+)", x).group(1)) if re.match(r"(\d+)", x) else 999)
    
    for p in p_keys:
        terms = master_ontology[p]
        norm_map = {}
        for t in terms:
            if not t: continue
            low = t.lower()
            if low not in norm_map or len(t) > len(norm_map[low]):
                norm_map[low] = t
        
        final_list = [t for t in norm_map.values() if len(t) > 2]
        sorted_master[p] = sorted(final_list)

    # 6. Save Master
    with open(MASTER_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(sorted_master, f, indent=4)
    
    print(f"Master ontology (Full Integration) generated at {MASTER_OUTPUT}")

if __name__ == "__main__":
    main()
