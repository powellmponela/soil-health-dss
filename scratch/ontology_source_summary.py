import json
from collections import defaultdict
import pandas as pd

ONTOLOGY_FILE = r'c:\SOIL HEALTH\principles_indicators\Ontology_index.json'

def summarize_ontology():
    print(f"Loading ontology from {ONTOLOGY_FILE}...")
    with open(ONTOLOGY_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # matrix[principle][source] = count
    matrix = defaultdict(lambda: defaultdict(int))
    
    def collect(nodes, principle):
        for n in nodes:
            source = n.get('source', 'AGROVOC')
            matrix[principle][source] += 1
            if 'sub_concepts' in n:
                collect(n['sub_concepts'], principle)
    
    for p, content in data.items():
        collect(content.get('sub_concepts', []), p)
    
    # Convert to DataFrame
    df = pd.DataFrame(matrix).fillna(0).astype(int).T
    
    # Identify major sources (total terms > 10)
    col_totals = df.sum(axis=0)
    major_sources = col_totals[col_totals > 10].index.tolist()
    minor_sources = col_totals[col_totals <= 10].index.tolist()
    
    # Group minor sources into "Other"
    if minor_sources:
        df['Other'] = df[minor_sources].sum(axis=1)
        df = df.drop(columns=minor_sources)
    
    # Add a Total row and column
    df['Total'] = df.sum(axis=1)
    
    # Sort principles logically (alphabetical or standard order)
    df = df.sort_index()
    
    # Print the table
    print("\nOntology Term Distribution Matrix (Major Sources):")
    print(df.to_markdown())
    
    # Save to CSV
    df.to_csv(r'c:\SOIL HEALTH\principles_indicators\ontology_summary_clean.csv')

if __name__ == "__main__":
    summarize_ontology()
