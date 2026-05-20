import json
import os

JSON_MASTER = "principles_indicators/Ontology_index.json"

def count_recursive(node):
    count = 1
    for child in node.get('sub_concepts', []):
        count += count_recursive(child)
    return count

def main():
    if not os.path.exists(JSON_MASTER): return

    with open(JSON_MASTER, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    print("\n=== Master Ontology Principle Breakdown ===")
    print(f"{'Agroecological Principle':<30} | {'Term Count':<10} | {'Percentage':<10}")
    print("-" * 55)

    principle_counts = {}
    for p_name, p_data in master_data.items():
        principle_counts[p_name] = count_recursive(p_data)

    total = sum(principle_counts.values())
    # Sort by count
    sorted_stats = sorted(principle_counts.items(), key=lambda x: x[1], reverse=True)

    for p_name, count in sorted_stats:
        pct = (count / total) * 100
        print(f"{p_name:<30} | {count:<10} | {pct:>8.2f}%")

    print("-" * 55)
    print(f"{'TOTAL':<30} | {total:<10} | 100.00%")

if __name__ == "__main__":
    main()
