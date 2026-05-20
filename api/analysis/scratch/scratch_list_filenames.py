import sqlite3
import os

DB_PATH = os.path.join("c:\\SOIL HEALTH", "db", "soil_health.sqlite")

def list_filenames():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, filename FROM frameworks")
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row['id']}: {row['name']} | {row['filename']}")
    conn.close()

if __name__ == "__main__":
    list_filenames()
