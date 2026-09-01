import sqlite3

def check_missing():
    conn = sqlite3.connect("db/soil_health.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT id, framework_id, filename, status FROM documents WHERE status != 'processed'")
    rows = cursor.fetchall()
    print("Non-processed documents:")
    for r in rows:
        print(f"ID: {r[0]} | Framework ID: {r[1]} | Filename: {r[2]} | Status: {r[3]}")
    conn.close()

if __name__ == "__main__":
    check_missing()
