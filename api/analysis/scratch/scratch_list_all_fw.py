import sqlite3
import os

DB_PATH = os.path.join("c:\\SOIL HEALTH", "db", "soil_health.sqlite")

def list_all_frameworks():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, title FROM frameworks")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row['id']}, Name: {row['name']}, Title: {row['title']}")
    conn.close()

if __name__ == "__main__":
    list_all_frameworks()
