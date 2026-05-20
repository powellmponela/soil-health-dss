import os
import re
import csv

NT_FILE = r"principles_indicators\agrovoc_full\agrovoc_core.nt"
CSV_FILE = r"principles_indicators\agrovoc_complete_index.csv"
TXT_FILE = r"principles_indicators\agrovoc_complete_index.txt"

# Regex for SKOS-XL relationships
# <Concept> <...#prefLabel> <LabelResource>
PREF_LABEL_REL_PATTERN = re.compile(r'<(http://aims.fao.org/aos/agrovoc/c_[^>]+)>\s+<http://www.w3.org/2008/05/skos-xl#prefLabel>\s+<(http://aims.fao.org/aos/agrovoc/xl_en_[^>]+)>')
# <LabelResource> <...#literalForm> "Label"@en
LITERAL_FORM_PATTERN = re.compile(r'<(http://aims.fao.org/aos/agrovoc/xl_en_[^>]+)>\s+<http://www.w3.org/2008/05/skos-xl#literalForm>\s+"([^"]+)"@en')

def main():
    if not os.path.exists(NT_FILE):
        print(f"Error: {NT_FILE} not found.")
        return

    print("Parsing Agrovoc NTriples file (Two-pass approach)...")
    
    label_to_concept = {}
    label_to_text = {}
    
    print("  Pass 1: Extracting relationships and literal forms...")
    with open(NT_FILE, "r", encoding="utf-8") as fin:
        for i, line in enumerate(fin):
            # Check for concept -> label resource mapping
            if "skos-xl#prefLabel" in line:
                match = PREF_LABEL_REL_PATTERN.search(line)
                if match:
                    concept_uri = match.group(1)
                    label_resource = match.group(2)
                    label_to_concept[label_resource] = concept_uri
            
            # Check for label resource -> literal text mapping
            elif "skos-xl#literalForm" in line and "@en" in line:
                match = LITERAL_FORM_PATTERN.search(line)
                if match:
                    label_resource = match.group(1)
                    label_text = match.group(2)
                    label_to_text[label_resource] = label_text
            
            if i % 1000000 == 0 and i > 0:
                print(f"    Processed {i} lines...")

    print(f"  Pass 1 complete. Found {len(label_to_concept)} prefLabel relations and {len(label_to_text)} English labels.")
    
    print("  Pass 2: Joining and writing output...")
    count = 0
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as fcsv, \
         open(TXT_FILE, "w", encoding="utf-8") as ftxt:
        
        writer = csv.writer(fcsv)
        writer.writerow(["URI", "Label"])
        
        # Sort by label for better usability
        sorted_labels = sorted(label_to_text.items(), key=lambda x: x[1].lower())
        
        for label_resource, label_text in sorted_labels:
            if label_resource in label_to_concept:
                concept_uri = label_to_concept[label_resource]
                writer.writerow([concept_uri, label_text])
                ftxt.write(f"{label_text} ({concept_uri})\n")
                count += 1
    
    print(f"Finished! Total terms extracted: {count}")
    print(f"Saved to {CSV_FILE} and {TXT_FILE}")

if __name__ == "__main__":
    main()
