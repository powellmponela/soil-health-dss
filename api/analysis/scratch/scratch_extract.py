import sqlite3
import re

db_path = "c:/SOIL HEALTH/db/soil_health.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT f.id, f.filename, d.extracted_text, f.doi_url FROM frameworks f JOIN documents d ON f.id = d.framework_id")
rows = cursor.fetchall()

def extract_doi_url(text):
    if not text: return ""
    doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", text)
    if doi_match:
        return f"https://doi.org/{doi_match.group(0)}"
    
    url_match = re.search(r"https?://[a-zA-Z0-9./?=_-]+", text)
    if url_match:
        return url_match.group(0)
    return ""

print("Testing extraction for all documents...")
success_count = 0
for row in rows:
    fw_id, filename, text, old_val = row
    
    if not old_val or old_val == "-":
        new_val = extract_doi_url(text)
        if new_val:
            print(f"Found {new_val} for {filename}")
            success_count += 1

print(f"Found new links for {success_count} documents.")
conn.close()
