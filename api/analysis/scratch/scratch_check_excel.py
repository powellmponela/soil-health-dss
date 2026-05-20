import pandas as pd
import os

PRINCIPLE_MATRIX_PATH = os.path.join("c:\\SOIL HEALTH", "principles_indicators", "principle_matrix.xlsx")

def check_pdf_names():
    try:
        df = pd.read_excel(PRINCIPLE_MATRIX_PATH)
        print("PDF names in principle_matrix.xlsx:")
        for name in df['pdf_name'].tolist():
            print(name)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_pdf_names()
