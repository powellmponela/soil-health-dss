import fitz
import os
import json

UNESCO_PDF = "principles_indicators/offline_storage/unesco_thesaurus/Unesco_thesaurus.pdf"

def exhaustive_extract(path):
    if not os.path.exists(path): return
    
    doc = fitz.open(path)
    print(f"Scanning {path} ({doc.page_count} pages)...")
    
    found_any = False
    for i in range(doc.page_count):
        page = doc[i]
        # Try different modes
        t_plain = page.get_text("text")
        t_blocks = page.get_text("blocks")
        
        if len(t_plain.strip()) > 0 or len(t_blocks) > 0:
            print(f"Found content on Page {i}!")
            print(f"  Snippet: {t_plain.strip()[:200]}...")
            found_any = True
            # If we find text, we can stop or continue
            break
            
        if i % 100 == 0:
            print(f"  Checked {i} pages...")
            
    doc.close()
    if not found_any:
        print("No selectable text found in the entire document.")

if __name__ == "__main__":
    exhaustive_extract(UNESCO_PDF)
    exhaustive_extract("principles_indicators/offline_storage/oecd_macrothesaurus/oecd_macrothesaurus.pdf")
