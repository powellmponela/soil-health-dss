import pandas as pd
import os

def inspect():
    p_path = "principles_indicators/principle_matrix.xlsx"
    i_path = "principles_indicators/indicator_matrix_hierarchical.xlsx"
    
    print("=== PRINCIPLE MATRIX (Mponela et al. 2026) ===")
    if os.path.exists(p_path):
        df_p = pd.read_excel(p_path)
        print(f"Shape: {df_p.shape}")
        print("Columns:")
        print(df_p.columns.tolist())
        print("\nFirst 5 rows:")
        print(df_p.head(5).to_string(index=False))
    else:
        print(f"File not found: {p_path}")
        
    print("\n=== INDICATOR MATRIX HIERARCHICAL ===")
    if os.path.exists(i_path):
        df_i = pd.read_excel(i_path)
        print(f"Shape: {df_i.shape}")
        print(f"Total Columns: {len(df_i.columns)}")
        print("First 10 columns:")
        print(df_i.columns.tolist()[:10])
        print("\nFirst 5 rows (first 4 columns):")
        print(df_i.iloc[:5, :4].to_string(index=False))
    else:
        print(f"File not found: {i_path}")

if __name__ == "__main__":
    inspect()
