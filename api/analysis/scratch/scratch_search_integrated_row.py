import pandas as pd
import os

PRINCIPLE_MATRIX_PATH = os.path.join("c:\\SOIL HEALTH", "principles_indicators", "principle_matrix.xlsx")

def search_integrated():
    try:
        df = pd.read_excel(PRINCIPLE_MATRIX_PATH)
        print("Rows in principle_matrix.xlsx:")
        for index, row in df.iterrows():
            if 'integrated' in str(row['pdf_name']).lower():
                print(f"Match found: {row['pdf_name']}")
                print(row)
        
        # Also check if there's a row with a very high score in many principles?
        # Or maybe it's the last row?
        print("\nLast 5 rows:")
        print(df.tail())
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_integrated()
