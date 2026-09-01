import pandas as pd

def inspect_headers():
    i_path = "principles_indicators/indicator_matrix_hierarchical.xlsx"
    xl = pd.ExcelFile(i_path)
    print("Sheet names:", xl.sheet_names)
    for name in xl.sheet_names:
        df = xl.parse(name)
        print(f"\nSheet '{name}' columns count: {len(df.columns)}")
        print("First 15 columns:")
        print(df.columns.tolist()[:15])
        print("Sample of column names with ' | ':")
        pipe_cols = [c for c in df.columns if ' | ' in str(c)]
        print(f"Found {len(pipe_cols)} columns with ' | '")
        if pipe_cols:
            print("First 5:", pipe_cols[:5])

if __name__ == "__main__":
    inspect_headers()

if __name__ == "__main__":
    inspect_headers()
