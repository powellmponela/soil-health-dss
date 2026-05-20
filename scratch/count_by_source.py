import json
import os

ONTOLOGY_INDEX = "principles_indicators/Ontology_index.json"

def main():
    if not os.path.exists(ONTOLOGY_INDEX): return
    with open(ONTOLOGY_INDEX, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    counts = {}

    def count_source(node):
        source = node.get('source', 'AGROVOC')
        counts[source] = counts.get(source, 0) + 1
        for child in node.get('sub_concepts', []):
            count_source(child)

    for principle in data.values():
        count_source(principle)

    # Sort by count descending
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    
    print("\n=== Term Count Per Source ===")
    for source, count in sorted_counts:
        print(f"{source}: {count}")

if __name__ == "__main__":
    main()
