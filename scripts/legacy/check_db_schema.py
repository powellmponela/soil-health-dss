import sqlite3

def check_schema():
    conn = sqlite3.connect('api/soildss.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    
    for table in tables:
        print(f"\nSchema for {table[0]}:")
        cursor.execute(f"PRAGMA table_info({table[0]})")
        print(cursor.fetchall())
    
    conn.close()

if __name__ == "__main__":
    check_schema()
