import sqlite3
import json

db_path = "c:/SOIL HEALTH/db/soil_health.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, name, filename FROM frameworks WHERE title = 'Agroecological Assessment'")
rows = cursor.fetchall()
print(json.dumps(rows, indent=2))
conn.close()
