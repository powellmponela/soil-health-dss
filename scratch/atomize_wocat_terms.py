import json
import os
import re

JSON_MASTER = "principles_indicators/Ontology_index.json"

# Common stopwords and location-like words to remove from WOCAT sentences
JUNK_WORDS = [
    "in", "on", "at", "with", "and", "the", "for", "from", "through", "by", 
    "lamwo", "uganda", "nepal", "ethiopia", "kenya", "tanzania", "malawi",
    "south", "africa", "asia", "ix", "vii", "measure", "technologies", "include"
]

def atomize_sentence(text):
    # Remove numbers at start (e.g. "69 ")
    text = re.sub(r'^\d+\s+', '', text)
    # Remove common punctuation that separates concepts
    parts = re.split(r'[,;.\-\u2013\u2014\u2022\u0007]', text)
    
    atomic_terms = []
    for part in parts:
        part = part.strip()
        if not part: continue
        
        # Further split by " with " or " and "
        sub_parts = re.split(r'\s+(?:with|and|through|via)\s+', part, flags=re.IGNORECASE)
        for sp in sub_parts:
            sp = sp.strip()
            # Clean junk words
            words = sp.split()
            cleaned_words = [w for w in words if w.lower() not in JUNK_WORDS and len(w) > 2]
            
            if len(cleaned_words) > 0:
                clean_term = " ".join(cleaned_words)
                # If the term is too long (> 5 words), it's probably still a sentence
                if len(cleaned_words) <= 5:
                    atomic_terms.append(clean_term)
                else:
                    # Just take the first few words as a noun phrase proxy
                    atomic_terms.append(" ".join(cleaned_words[:3]))

    return list(set(atomic_terms))

def update_node_recursive(node):
    if node.get('source') == "WOCAT" and 'sub_concepts' in node:
        new_children = []
        for child in node['sub_concepts']:
            if child.get('source') == "WOCAT":
                label = child.get('label', '')
                atoms = atomize_sentence(label)
                if len(atoms) > 1:
                    # Replace the sentence child with multiple atomic children
                    for atom in atoms:
                        new_children.append({
                            "label": atom,
                            "source": "WOCAT",
                            "uri": f"wocat:{atom.lower().replace(' ', '_')}",
                            "sub_concepts": []
                        })
                else:
                    new_children.append(child)
            else:
                new_children.append(child)
        node['sub_concepts'] = new_children
    
    for child in node.get('sub_concepts', []):
        update_node_recursive(child)

def main():
    if not os.path.exists(JSON_MASTER): return

    with open(JSON_MASTER, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    print("=== Atomizing WOCAT Sentences into Atomic Indicators ===")
    
    for p_name, p_data in master_data.items():
        update_node_recursive(p_data)

    with open(JSON_MASTER, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, indent=4)

    print("WOCAT Atomization complete. All principle branches updated.")

if __name__ == "__main__":
    main()
