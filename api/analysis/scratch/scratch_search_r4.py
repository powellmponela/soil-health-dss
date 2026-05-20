import sqlite3
import os

DB_PATH = os.path.join("c:\\SOIL HEALTH", "db", "soil_health.sqlite")

def search_frameworks():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("Searching for 'R4' or 'Returns' or 'Integrated'...")
    cursor.execute("SELECT id, name, title FROM frameworks WHERE name LIKE '%R4%' OR title LIKE '%R4%' OR name LIKE '%Returns%' OR title LIKE '%Returns%' OR title LIKE '%Integrated%'")
    rows = cursor.fetchall()
    
    for row in rows:
        try:
            print(f"ID: {row['id']}, Name: {row['name']}, Title: {row['title']}")
        except:
            print(f"ID: {row['id']}, Name: [Encoding Error]")
            
    conn.close()

if __name__ == "__main__":
    search_frameworks()
