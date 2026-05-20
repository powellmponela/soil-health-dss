import pandas as pd
import os

PATH = os.path.join("c:\\SOIL HEALTH", "principles_indicators", "indicator_matrix_hierarchical.xlsx")

def check_data():
    try:
        df = pd.read_excel(PATH, header=[0, 1, 2])
        print("Columns:")
        print(df.columns[:5])
        print("\nRows (first 5):")
        print(df.iloc[:5, 0:5])
        
        # Check if any row matches "Integrated"
        print("\nChecking for 'Integrated' in index or first column:")
        # The first column usually becomes the index or the first level
        for val in df.index:
            if 'integrated' in str(val).lower():
                print(f"Found in index: {val}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
