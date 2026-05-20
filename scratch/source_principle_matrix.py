import json
import os
import pandas as pd

JSON_MASTER = "principles_indicators/Ontology_index.json"

def aggregate_sources(node, source_counts):
    source = node.get('source', 'UNKNOWN')
    source_counts[source] = source_counts.get(source, 0) + 1
    for child in node.get('sub_concepts', []):
        aggregate_sources(child, source_counts)

def main():
    if not os.path.exists(JSON_MASTER): return

    with open(JSON_MASTER, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    # We want a Matrix: Principles (Rows) x Sources (Cols)
    matrix_data = {}

    for p_name, p_data in master_data.items():
        s_counts = {}
        aggregate_sources(p_data, s_counts)
        matrix_data[p_name] = s_counts

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(matrix_data, orient='index').fillna(0).astype(int)
    
    # Calculate Total per Principle
    df['Total'] = df.sum(axis=1)
    
    # Sort by Total
    df = df.sort_values(by='Total', ascending=False)

    # Print the matrix
    # Select only the top sources to keep it readable, plus the total
    top_sources = df.drop(columns=['Total']).sum().sort_values(ascending=False).head(8).index.tolist()
    display_cols = top_sources + ['Total']
    
    print("\n=== Master Ontology: Source x Principle Distribution Matrix ===")
    print(df[display_cols].to_markdown())

    # Save the full matrix
    df.to_csv("principles_indicators/source_principle_distribution.csv")
    print(f"\nFull Distribution Matrix saved to: principles_indicators/source_principle_distribution.csv")

if __name__ == "__main__":
    main()
