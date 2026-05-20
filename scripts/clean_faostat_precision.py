import json
import os

# Paths
SOURCE_TERMS = r"c:\SOIL HEALTH\principles_indicators\offline_storage\faostat\terms.json"
MASTER_FILE = r"c:\SOIL HEALTH\master_agroecological_ontology.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\faostat\faostat_ontology_compact.json"

def clean_label(label):
    # Canonical cleaning: lowercase, strip, handle plurals simply
    l = label.lower().strip()
    if l.endswith('s') and not l.endswith('ss'):
        return l[:-1]
    return l

def main():
    if not os.path.exists(SOURCE_TERMS) or not os.path.exists(MASTER_FILE):
        print("Error: Missing source terms or master file.")
        return

    with open(SOURCE_TERMS, "r", encoding="utf-8") as f:
        original_terms = json.load(f)
        # Create a lookup set of lowercase labels from original provenance
        provenance_labels = set(t["label"].lower().strip() for t in original_terms)

    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        master = json.load(f)
    
    principles = master.get("principles", {})
    
    refined_faostat = {}
    
    for p_name, content in principles.items():
        refined_faostat[p_name] = {"key_terms": [], "indicators": []}
        
        # We check every indicator in the master. 
        # If its label (cleaned) matches something in FAOSTAT's terms.json, we keep it.
        seen_labels = set()
        
        for ind in content.get("indicators", []):
            label = ind.get("label", "")
            cleaned = clean_label(label)
            
            # Match against provenance
            if cleaned in provenance_labels or label.lower() in provenance_labels:
                if cleaned not in seen_labels:
                    refined_faostat[p_name]["indicators"].append({
                        "label": label.title(),
                        "source": "FAOSTAT"
                    })
                    seen_labels.add(cleaned)

        # Do the same for key_terms if applicable
        for kt in content.get("key_terms", []):
            if clean_label(kt) in provenance_labels:
                refined_faostat[p_name]["key_terms"].append(kt.title())

    # Save
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(refined_faostat, f, indent=4)
    
    print(f"FAOSTAT finalized and cleaned: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
