import pandas as pd
import os

INDICATOR_MATRIX_PATH = os.path.join("c:\\SOIL HEALTH", "principles_indicators", "indicator_matrix_hierarchical.xlsx")

def check_cols():
    try:
        df = pd.read_excel(INDICATOR_MATRIX_PATH)
        print("Columns in indicator_matrix_hierarchical.xlsx:")
        print(df.columns.tolist()[:10]) # Just first 10
        print("First few rows:")
        print(df.iloc[:5, 0:5])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_cols()
