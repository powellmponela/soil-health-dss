from pypdf import PdfReader
import os

PDF_PATH = os.path.join("c:\\SOIL HEALTH", "References", "ASDE-D-25-01749_R4.pdf")

def extract_text():
    try:
        reader = PdfReader(PDF_PATH)
        text = ""
        for i in range(min(5, len(reader.pages))): # First 5 pages
            text += reader.pages[i].extract_text()
        print(text[:2000]) # Print first 2000 chars
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_text()
