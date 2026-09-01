import sqlite3

def check_db_contents():
    conn = sqlite3.connect("db/soil_health.sqlite")
    cursor = conn.cursor()
    
    tables = ['frameworks', 'principles', 'indicators', 'indicator_matrix', 'documents', 'suggestions']
    
    print("=== Database Table Counts ===")
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} rows")
        except sqlite3.OperationalError as e:
            print(f"{table}: Error - {e}")
            
    print("\n=== Principles ===")
    try:
        cursor.execute("SELECT id, name FROM principles")
        for row in cursor.fetchall():
            print(f"  ID {row[0]}: {row[1]}")
    except Exception as e:
        print("Error getting principles:", e)
        
    print("\n=== Frameworks Sample (Top 5) ===")
    try:
        cursor.execute("SELECT id, name, title, author_date FROM frameworks LIMIT 5")
        for row in cursor.fetchall():
            print(f"  ID {row[0]}: {row[1]} | {row[2]} ({row[3]})")
    except Exception as e:
        print("Error getting frameworks:", e)

    print("\n=== Indicators Sample (Top 5) ===")
    try:
        cursor.execute("SELECT id, name, description FROM indicators LIMIT 5")
        for row in cursor.fetchall():
            print(f"  ID {row[0]}: {row[1]} - {row[2]}")
    except Exception as e:
        print("Error getting indicators:", e)

    print("\n=== Documents Status Summary ===")
    try:
        cursor.execute("SELECT status, COUNT(*) FROM documents GROUP BY status")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
    except Exception as e:
        print("Error getting documents summary:", e)

    print("\n=== Suggestions Status Summary ===")
    try:
        cursor.execute("SELECT status, COUNT(*) FROM suggestions GROUP BY status")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
    except Exception as e:
        print("Error getting suggestions summary:", e)

    conn.close()

if __name__ == "__main__":
    check_db_contents()
