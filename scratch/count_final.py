import json
import os

ONTOLOGY_INDEX = "principles_indicators/Ontology_index.json"

def count_nodes(n):
    c = 1
    for child in n.get('sub_concepts', []):
        c += count_nodes(child)
    return c

def main():
    with open(ONTOLOGY_INDEX, 'r', encoding='utf-8') as f:
        d = json.load(f)
    
    total = 0
    for p, data in d.items():
        cnt = count_nodes(data)
        print(f"{p}: {cnt}")
        total += cnt
    print(f"Total: {total}")

if __name__ == "__main__":
    main()
