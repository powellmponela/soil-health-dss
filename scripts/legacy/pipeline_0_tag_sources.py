import json
import os
import re

# Load strict relevance logic from pipeline_1
from pipeline_1_build_ontology import is_relevant, FORBIDDEN_KEYWORDS

DATA_DIR = "principles_indicators"
OFFLINE_STORAGE = os.path.join(DATA_DIR, "offline_storage")

SOURCES = {
    "AGROVOC": os.path.join("api", "data", "agrovoc_principles_map.json"),
    "WORLD_BANK": os.path.join(OFFLINE_STORAGE, "world_bank", "terms.json"),
    "ILOSTAT": os.path.join(OFFLINE_STORAGE, "ilostat", "terms.json"),
    "HASSET": os.path.join(OFFLINE_STORAGE, "hasset", "terms.json"),
    "UNBIS": os.path.join(OFFLINE_STORAGE, "unbis", "terms.json"),
    "UNESCO": os.path.join(OFFLINE_STORAGE, "unesco_thesaurus", "terms.json"),
    "WOCAT": os.path.join(OFFLINE_STORAGE, "wocat", "wocat_extracted_terms.json"),
    "FAOSTAT": os.path.join(OFFLINE_STORAGE, "faostat", "terms.json"),
    "HLPE": os.path.join(OFFLINE_STORAGE, "hlpe_enriched", "terms.json"),
    "BIOPHYSICAL": os.path.join(OFFLINE_STORAGE, "biophysical_expansion", "terms.json"),
    "MANUAL": os.path.join(OFFLINE_STORAGE, "manual_injection", "terms.json")
}

# Principles to scan for generic sources
PRINCIPLES = [
    "Participation", "Fairness", "Co-creation of Knowledge", 
    "Social Values and Diets", "Connectivity", "Land Governance",
    "Economic Diversification", "Recycling", "Synergy", "Biodiversity",
    "Soil Health", "Animal Health", "Input Reduction"
]

def clean_label(label):
    if not label: return ""
    # Strip World Bank numeric codes like "110400:HOUSING..."
    label = re.sub(r'^\d+:', '', label)
    # Strip parenthetical categories like "(Category)"
    label = re.sub(r'\(.*?\)', '', label).strip()
    return label

def process_standard_source(source_name, path, tagged_data):
    if not os.path.exists(path):
        return
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tagged_data[source_name] = {}
    
    # Handle list of dicts (standard) or dict of dicts (AGROVOC)
    items = data.values() if isinstance(data, dict) else data
    
    for item in items:
        # AGROVOC uses 'prefLabel', others use 'label' or 'term'
        label = clean_label(item.get('prefLabel', item.get('label', item.get('term', ''))))
        if not label: continue
        
        # Some sources have pre-defined principles, others need scanning
        principles = item.get('principles', [])
        if not principles:
            principles = PRINCIPLES
        
        # If principles are pre-defined, we use a more lenient threshold of 1 hit
        use_threshold = 1 if item.get('principles') else None
        
        for p in principles:
            if is_relevant(label, p, threshold=use_threshold):
                if p not in tagged_data[source_name]: 
                    tagged_data[source_name][p] = []
                # Keep URI if available
                uri = item.get('uri', '')
                tagged_data[source_name][p].append({"term": label, "uri": uri})
    
    count = sum(len(v) for v in tagged_data[source_name].values())
    print(f"Tagged {source_name}: {count} valid terms.")

def tag_sources():
    print("=== Tagging Principles per Source (Comprehensive Pipeline) ===")
    tagged_data = {}

    for name, path in SOURCES.items():
        process_standard_source(name, path, tagged_data)

    # Save results
    output_path = os.path.join(DATA_DIR, "source_specific_tags.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tagged_data, f, indent=4)
    
    # Save human-readable summary
    summary_path = os.path.join(DATA_DIR, "source_specific_tags_summary.txt")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=== COMPREHENSIVE SOURCE-SPECIFIC PRINCIPLE TAGGING ===\n\n")
        # Sort sources for consistent report
        for source in sorted(tagged_data.keys()):
            principles = tagged_data[source]
            f.write(f"SOURCE: {source}\n")
            if not principles:
                f.write("  (No valid terms found for this source)\n")
            
            # Sort principles for consistent report
            for p in sorted(principles.keys()):
                terms = principles[p]
                f.write(f"  [{p}] ({len(terms)} terms)\n")
                # Group and sort for readability
                unique_terms = sorted(list(set([x['term'] for x in terms])))
                for t in unique_terms[:15]:
                    f.write(f"    - {t}\n")
                if len(unique_terms) > 15: 
                    f.write(f"    ... and {len(unique_terms)-15} more\n")
            f.write("\n")

    print(f"Tagging complete. Results saved to {output_path}")

if __name__ == "__main__":
    tag_sources()
