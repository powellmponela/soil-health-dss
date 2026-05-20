import sqlite3
import os

DB_PATH = os.path.join("c:\\SOIL HEALTH", "db", "soil_health.sqlite")

def check_frameworks():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("Checking frameworks table...")
    cursor.execute("SELECT id, name, title FROM frameworks WHERE name LIKE '%Out 6%' OR title LIKE '%Out 6%' OR name LIKE '%Integrated framework%' OR title LIKE '%Integrated framework%'")
    rows = cursor.fetchall()
    
    if not rows:
        print("No matching frameworks found. Listing all frameworks:")
        cursor.execute("SELECT id, name, title FROM frameworks LIMIT 10")
        rows = cursor.fetchall()
        
    for row in rows:
        print(f"ID: {row['id']}, Name: {row['name']}, Title: {row['title']}")
        
    conn.close()

if __name__ == "__main__":
    check_frameworks()
