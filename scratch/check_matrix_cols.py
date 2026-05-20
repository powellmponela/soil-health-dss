import pandas as pd
import numpy as np

matrix_file = r'c:\SOIL HEALTH\principles_indicators\framework_principle_matrix.csv'

def generate_principle_by_ontology():
    df = pd.read_csv(matrix_file)
    
    principle_cols = [c for c in df.columns if c.startswith('P_') and c != 'P_Additional Consolidated Terms']
    new_sources = ['S_UNBIS', 'S_UNESCO', 'S_WOCAT']
    traditional_sources = [c for c in df.columns if c.startswith('S_') and c not in new_sources]
    
    # Unfortunately, framework_principle_matrix.csv only has total detections per principle (P_*) 
    # AND total detections per source (S_*).
    # It does NOT cross-tabulate Principle x Source for the frameworks.
    # Wait, does the script 'extract_framework_matrix.py' save a cross-tabulated matrix?
    print("Columns:", df.columns.tolist())

if __name__ == "__main__":
    generate_principle_by_ontology()
