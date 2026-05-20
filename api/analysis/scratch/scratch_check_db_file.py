import sqlite3
import os

db_path = "c:/SOIL HEALTH/db/soil_health.sqlite"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, name FROM frameworks WHERE filename = 'g-accounting-teeb.pdf'")
row = cursor.fetchone()
if row:
    print(f"Found in DB: ID={row[0]}, Name={row[1]}")
else:
    print("Not found in DB")

conn.close()
