import os
import json
import time
import requests
import xml.etree.ElementTree as ET
import csv
import re

# Configuration
OUTPUT_DIR = "principles_indicators"
RAW_DATA_DIR = os.path.join("data", "raw")
PROCESSED_DATA_DIR = os.path.join("data", "processed")

# Ensure directories exist
for d in [OUTPUT_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

# Centralized Keyword Map
SEARCH_MAP = {
    "Participation": ["community participation", "collective action", "farmer groups", "local governance", "inclusive decision making", "stakeholder engagement", "empowerment", "farmer organization"],
    "Fairness": ["social justice", "equitable trade", "labour rights", "fair price", "social protection", "human rights", "poverty reduction", "gender equity", "decent work"],
    "Co-creation of Knowledge": ["farmer-to-farmer", "traditional knowledge", "indigenous knowledge", "action research", "knowledge exchange", "local wisdom", "participatory research"],
    "Social Values and Diets": ["dietary diversity", "traditional food", "food culture", "nutrition", "culturally appropriate food", "food heritage"],
    "Connectivity": ["market access", "short food chains", "producer networks", "consumer connections", "value chain transparency", "local markets"],
    "Land Governance": ["land tenure", "property rights", "land reform", "common land", "natural resource management", "tenure security"],
    "Economic Diversification": ["on-farm income", "off-farm income", "rural livelihoods", "microfinance", "rural entrepreneurship", "value addition"],
    "Recycling": ["nutrient cycling", "waste recycling", "biomass reuse", "circular economy", "composting", "water recovery", "manure management", "mulch", "biochar", "vermicompost", "residue", "urine", "dung"],
    "Synergy": ["crop-livestock integration", "agroforestry", "intercropping", "ecological synergy", "integrated management", "biological synergy", "intercrop", "agroforest"],
    "Biodiversity": ["crop diversity", "species richness", "nature conservation", "genetic resources", "pollinator conservation", "agrobiodiversity"],
    "Soil Health": ["soil fertility", "soil organic matter", "soil conservation", "soil microbiology", "manure application", "soil structure", "terrace", "bund", "tillage", "cover crop", "mulch"],
    "Animal Health": ["animal welfare", "livestock health", "veterinary services", "resilient breeds", "animal health"],
    "Input Reduction": ["pesticide reduction", "fertilizer efficiency", "biological control", "integrated pest management", "organic inputs", "tillage", "irrigation", "drip", "low-input", "no-till", "minimum-till"]
}

FORBIDDEN_KEYWORDS = [
    "facility", "hospital", "medical", "anaesthesia", "surgery", "patient", "clinical",
    "fiat", "ice", "geological", "volcano", "crater", "oceanic", "benthopelagic",
    "bicycle", "currency", "devaluation", "post-anesthesia", "care unit", "rod",
    "driveway", "booth", "monsoon", "restaurant", "slum", "wildfire", "carbohydrate",
    "cation", "potassium", "haber-bosch", "biosolids", "bone meal",
    "economic recovery", "disaster recovery", "balance of payments", "balance of trade",
    "balance sheet", "balance organs", "customs duties", "customs unions", "blood groups",
    "adolescent fertility", "Goal 3", "Goal 6", "Goal 8", "Goal 9", "Goal 11", "Goal 14", "Goal 15",
    "semen", "preservation", "frozen", "sperm", "artificial insemination"
]

def is_relevant(label, principle, threshold=None):
    if not label: return False
    label_lower = label.lower()
    
    # 1. Check forbidden
    if any(k in label_lower for k in FORBIDDEN_KEYWORDS):
        return False
    
    # 2. Principle-specific strict context mapping
    CONTEXT_MAP = {
        "Participation": ["participation", "stakeholder", "community", "governance", "collective", "empowerment", "inclusive", "decision", "farmer", "producer", "association", "organization"],
        "Fairness": ["fair", "equity", "equitable", "justice", "rights", "poverty", "gender", "labour", "employment", "wage", "decent", "protection", "social"],
        "Co-creation of Knowledge": ["knowledge", "learning", "education", "research", "farmer", "indigenous", "traditional", "wisdom", "sharing", "extension", "participatory"],
        "Social Values and Diets": ["diet", "nutrition", "culture", "cultural", "food system", "healthy", "consumption", "heritage", "traditional", "values"],
        "Connectivity": ["market", "network", "trade", "value chain", "consumer", "producer", "connection", "linkage", "transparency", "short chain"],
        "Land Governance": ["land", "tenure", "property", "reform", "common", "policy", "governance", "resource", "rights"],
        "Economic Diversification": ["income", "livelihood", "diversification", "employment", "entrepreneurship", "off-farm", "on-farm", "rural", "value addition"],
        "Recycling": ["recycling", "waste", "biomass", "nutrient", "circular", "reuse", "recovery", "compost", "water", "wastewater", "manure", "mulch", "biochar", "vermicompost", "residue", "urine", "dung"],
        "Synergy": ["synergy", "integration", "integrated", "agroecological", "agroecology", "redesign", "ecological", "intercropping", "mixed", "agroforestry", "intercrop", "agroforest"],
        "Biodiversity": ["biodiversity", "species", "diversity", "nature", "conservation", "genetic", "wildlife", "variety", "agrobiodiversity"],
        "Soil Health": ["soil", "fertility", "organic", "microbial", "structure", "erosion", "conservation", "health", "terrace", "bund", "tillage", "cover crop", "mulch"],
        "Animal Health": ["animal welfare", "livestock health", "veterinary services", "resilient breeds", "health", "disease"],
        "Input Reduction": ["reduction", "efficiency", "pesticide", "fertilizer", "biological", "input", "sustainable", "organic", "tillage", "irrigation", "drip", "low-input", "no-till", "minimum-till"]
    }
    
    if principle in CONTEXT_MAP:
        # High noise principles or principles with very generic keywords require TWO hits
        high_noise = ["Social Values and Diets", "Participation", "Fairness", "Economic Diversification", "Recycling", "Connectivity"]
        hits = sum(1 for k in CONTEXT_MAP[principle] if k in label_lower)
        
        if threshold is None:
            threshold = 2 if principle in high_noise else 1
        
        # Exception: if the label EXACTLY matches a specific technical anchor, 1 hit is enough
        if hits == 1 and label_lower in CONTEXT_MAP[principle]:
            threshold = 1
            
        if hits < threshold:
            return False
            
    # 3. Avoid very short or overly generic labels
    if len(label_lower) < 3:
        return False
        
    return True

def build_master_index():
    print("=== Phase 2: Building Master Ontology Index (Consolidating Tagged Sources) ===")
    
    tags_path = os.path.join(OUTPUT_DIR, "source_specific_tags.json")
    if not os.path.exists(tags_path):
        print("Source tags not found. Running pipeline_0 first...")
        # Note: In a real environment we would import and call, but here we expect the user/caller to run pipeline_0
        return

    with open(tags_path, 'r', encoding='utf-8') as f:
        tagged_data = json.load(f)

    # Master structure
    master = {p: {"principle": p, "sub_concepts": []} for p in SEARCH_MAP.keys()}
    
    seen_labels = {p: set() for p in SEARCH_MAP.keys()}
    
    for source, principles in tagged_data.items():
        for principle, terms in principles.items():
            if principle not in master: continue
            
            for t in terms:
                label = t['term'].lower().strip()
                # Final validation
                if not is_relevant(label, principle): continue
                
                if label not in seen_labels[principle]:
                    # Splitting into levels and cleaning
                    # Remove "and" as requested
                    clean_label_str = label.replace(" and ", " ").replace(" & ", " ")
                    
                    # Splitting logic for Master / 2nd / 3rd level
                    # Patterns to split: " / ", " - ", " | ", ", ", ": ", "–", "—", and specific compound terms
                    temp_parts = re.split(r' / | - | \| |, |: |–|—', clean_label_str)
                    
                    parts = []
                    for p in temp_parts:
                        # Split high-priority compound research terms and common disaggregations
                        sub_p = p
                        # Core user-requested splits
                        sub_p = sub_p.replace("female to male", "female to male | ")
                        sub_p = sub_p.replace("gender", " | gender | ")
                        sub_p = sub_p.replace("wage gap", " | wage gap")
                        sub_p = sub_p.replace("learning outcomes", " | learning outcomes")
                        
                        # General disaggregation (Disaggregate across ontology)
                        sub_p = sub_p.replace("male-recipient", " | male")
                        sub_p = sub_p.replace("female-recipient", " | female")
                        sub_p = sub_p.replace("rural", " | rural")
                        sub_p = sub_p.replace("urban", " | urban")
                        sub_p = sub_p.replace("labor", " | labor")
                        sub_p = sub_p.replace("social protection", " | social protection")
                        sub_p = sub_p.replace("borrowing", " | borrowing | ")
                        sub_p = sub_p.replace("selling something", " | selling something | ")
                        sub_p = sub_p.replace("seeking help from friends and family", " | seeking help from friends and family | ")
                        sub_p = sub_p.replace("seeking help from", " | seeking help from | ")
                        
                        # Handle qualifiers like "degree of", "level of", "autonomy in"
                        sub_p = sub_p.replace("degree of ", " | ")
                        sub_p = sub_p.replace("level of ", " | ")
                        sub_p = sub_p.replace("autonomy in ", "autonomy | ")
                        sub_p = sub_p.replace("autonomy over the ", "autonomy | ")
                        
                        # Intelligent context splitting for high-signal keywords
                        # Move the core keyword to its own level while keeping the modifier
                        agro_keywords = [
                            "accountability", "innovation", "equity", "adequacy", "efficiency", 
                            "authority", "policy", "rights", "data", "standards", "emissions",
                            "health", "soil", "water", "biodiversity", "nutrient", "management", 
                            "governance", "resilience", "sustainable", "security", "diversity"
                        ]
                        for keyword in agro_keywords:
                            if f" {keyword}" in sub_p.lower():
                                sub_p = sub_p.replace(f" {keyword}", f" | {keyword}")
                            if f"{keyword} " in sub_p.lower():
                                sub_p = sub_p.replace(f"{keyword} ", f"{keyword} | ")
                        
                        for sp in sub_p.split("|"):
                            s_stripped = sp.strip()
                            if s_stripped:
                                parts.append(s_stripped)
                    
                    # Final cleaning and deduplication of parts while preserving order
                    cleaned_parts = []
                    seen_parts = set()
                    for p in parts:
                        # Normalize common suffixes requested by user or seen in noise
                        p_clean = p.replace("-all", "").replace("-fe", "").strip()
                        # Remove trailing/leading hyphens
                        p_clean = p_clean.strip("-").strip()
                        
                        # Skip generic administrative levels as requested
                        admin_noise = ["policy goal", "lever", "pillar"]
                        if any(noise in p_clean.lower() for noise in admin_noise):
                            continue
                            
                        if p_clean and p_clean not in seen_parts:
                            cleaned_parts.append(p_clean)
                            seen_parts.add(p_clean)
                    
                    master_term = cleaned_parts[0] if len(cleaned_parts) > 0 else label
                    second_level = cleaned_parts[1] if len(cleaned_parts) > 1 else None
                    third_level = cleaned_parts[2] if len(cleaned_parts) > 2 else None

                    master[principle]["sub_concepts"].append({
                        "label": label,
                        "master_indicator": master_term,
                        "level_2": second_level,
                        "level_3": third_level,
                        "uri": t['uri'],
                        "source": source,
                        "functional_role": "Indicator"
                    })
                    seen_labels[principle].add(label)

    # Save to production locations
    master_json = os.path.join(OUTPUT_DIR, "Ontology_index.json")
    master_txt = os.path.join(OUTPUT_DIR, "Ontology_index.txt")
    
    with open(master_json, 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=4)
        
    with open(master_txt, 'w', encoding='utf-8') as f:
        f.write("=== MASTER AGROECOLOGICAL ONTOLOGY INDEX (RECONSTRUCTED) ===\n\n")
        for p, content in master.items():
            f.write(f"[{p.upper()}] ({len(content['sub_concepts'])} terms)\n")
            # Sort by master indicator then levels (handle None values for sorting)
            sorted_concepts = sorted(content["sub_concepts"], key=lambda x: (x.get('master_indicator') or '', x.get('level_2') or '', x.get('level_3') or ''))
            
            last_master = None
            for concept in sorted_concepts:
                m = concept.get('master_indicator')
                l2 = concept.get('level_2')
                l3 = concept.get('level_3')
                
                if m != last_master:
                    f.write(f"  - {m}\n")
                    last_master = m
                
                if l2:
                    f.write(f"    - {l2}\n")
                    if l3:
                        f.write(f"      - {l3}\n")
            f.write("\n")
            
    print(f"Master Ontology updated: {master_json}")

if __name__ == "__main__":
    build_master_index()
