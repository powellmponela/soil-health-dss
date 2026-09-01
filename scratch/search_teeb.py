import sqlite3

def search():
    conn = sqlite3.connect("db/soil_health.sqlite")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, title, filename 
        FROM frameworks 
        WHERE name LIKE '%teeb%' OR title LIKE '%teeb%' OR filename LIKE '%teeb%'
    """)
    rows = cursor.fetchall()
    print("TEEB Frameworks in DB:")
    for r in rows:
        print(f"ID: {r[0]} | Name: {r[1]} | Title: {r[2]} | Filename: {r[3]}")
    conn.close()

if __name__ == "__main__":
    search()
