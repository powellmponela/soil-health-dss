import pandas as pd
import os

PATH = os.path.join("c:\\SOIL HEALTH", "principles_indicators", "principle_matrix.xlsx")

def list_all():
    try:
        df = pd.read_excel(PATH)
        print("All framework names in matrix:")
        for name in df['pdf_name'].tolist():
            print(f"'{name}'")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_all()
