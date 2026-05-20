import sqlite3
import requests
import json

db_path = "c:/SOIL HEALTH/db/soil_health.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT f.id, f.name, f.filename, d.extracted_text FROM frameworks f JOIN documents d ON f.id = d.framework_id WHERE f.title = 'Agroecological Assessment'")
rows = cursor.fetchall()

def query_crossref(name, text):
    # Use name (e.g. "Johnston and Bruulsema 2014") as the primary query
    url = "https://api.crossref.org/works"
    params = {
        "query.bibliographic": name + " " + text[:100].replace('\n', ' '),
        "select": "title,author,publisher,DOI,issued",
        "rows": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data['message']['items']:
            item = data['message']['items'][0]
            title = item.get('title', [''])[0]
            publisher = item.get('publisher', '')
            doi = item.get('DOI', '')
            
            # format author
            authors_list = item.get('author', [])
            author_str = ""
            if authors_list:
                author_str = ", ".join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors_list[:2]])
                if len(authors_list) > 2:
                    author_str += " et al."
                    
            year = ""
            if 'issued' in item and 'date-parts' in item['issued']:
                year = str(item['issued']['date-parts'][0][0])
                
            author_year = f"{author_str} ({year})" if author_str and year else author_str or year
            
            return {
                "title": title,
                "author_date": author_year,
                "publisher": publisher,
                "doi_url": f"https://doi.org/{doi}" if doi else ""
            }
    except Exception as e:
        print(f"Error: {e}")
    return None

import time

updates = []
for row in rows:
    fw_id, name, filename, text = row
    print(f"--- {name} ({filename}) ---")
    meta = query_crossref(name, text)
    if meta:
        print(f"Title: {meta['title']}")
        print(f"Author (Year): {meta['author_date']}")
        print(f"Publisher: {meta['publisher']}")
        print(f"DOI: {meta['doi_url']}")
        
        # We will use the original name as author_date if crossref fails
        final_author = meta['author_date'] if meta['author_date'] else name
        
        # Update query
        updates.append((meta['title'], final_author, meta['publisher'], meta['doi_url'], fw_id))
    else:
        print("No match found.")
    print("")
    time.sleep(0.5)

# Update database
if updates:
    cursor.executemany("UPDATE frameworks SET title = ?, author_date = ?, publisher = ?, doi_url = ? WHERE id = ?", updates)
    conn.commit()
    print(f"Updated {len(updates)} frameworks.")

conn.close()
