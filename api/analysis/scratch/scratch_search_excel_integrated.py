import pandas as pd
import os

PRINCIPLE_MATRIX_PATH = os.path.join("c:\\SOIL HEALTH", "principles_indicators", "principle_matrix.xlsx")
INDICATOR_MATRIX_PATH = os.path.join("c:\\SOIL HEALTH", "principles_indicators", "indicator_matrix_hierarchical.xlsx")

def search_matrices():
    try:
        df1 = pd.read_excel(PRINCIPLE_MATRIX_PATH)
        print("Searching principle_matrix.xlsx...")
        match1 = df1[df1.apply(lambda row: row.astype(str).str.contains('Integrated', case=False).any(), axis=1)]
        if not match1.empty:
            print("Found in principle_matrix:")
            print(match1['pdf_name'].tolist())
            
        df2 = pd.read_excel(INDICATOR_MATRIX_PATH)
        print("Searching indicator_matrix_hierarchical.xlsx...")
        match2 = df2[df2.apply(lambda row: row.astype(str).str.contains('Integrated', case=False).any(), axis=1)]
        if not match2.empty:
            print("Found in indicator_matrix:")
            print(match2['pdf_name'].tolist())
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_matrices()
