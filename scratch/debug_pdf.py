import fitz
import os

PDF_PATH = "principles_indicators/offline_storage/unesco_thesaurus/Unesco_thesaurus.pdf"

def debug_pdf(path):
    if not os.path.exists(path):
        print(f"Path not found: {path}")
        return
    
    print(f"Debugging: {path}")
    doc = fitz.open(path)
    print(f"Page Count: {doc.page_count}")
    
    for i in range(min(5, doc.page_count)):
        page = doc[i]
        text = page.get_text()
        images = page.get_images()
        print(f"Page {i}: Text length={len(text)}, Images={len(images)}")
        if len(text) > 0:
            print(f"  Snippet: {text[:100]}...")
        if len(images) > 0:
            for img in images:
                print(f"  Image: {img}")
    
    doc.close()

if __name__ == "__main__":
    debug_pdf(PDF_PATH)
    debug_pdf("principles_indicators/offline_storage/oecd_macrothesaurus/oecd_macrothesaurus.pdf")
