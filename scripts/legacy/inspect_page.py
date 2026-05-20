import fitz
import sys

def main(pdf_path, page_num):
    doc = fitz.open(pdf_path)
    text = doc[int(page_num)].get_text()
    with open('temp_page.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    doc.close()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
