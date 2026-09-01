import sqlite3

def check_integrity():
    conn = sqlite3.connect("db/soil_health.sqlite")
    cursor = conn.cursor()
    
    # 1. Orphaned documents
    cursor.execute("""
        SELECT d.id, d.framework_id, d.filename 
        FROM documents d 
        LEFT JOIN frameworks f ON d.framework_id = f.id 
        WHERE f.id IS NULL
    """)
    orphaned_docs = cursor.fetchall()
    print("Orphaned documents (no matching framework):")
    if orphaned_docs:
        for r in orphaned_docs:
            print(f"  Doc ID: {r[0]} | Framework ID: {r[1]} | Filename: {r[2]}")
    else:
        print("  None")
        
    # 2. Frameworks without documents
    cursor.execute("""
        SELECT f.id, f.name, f.filename 
        FROM frameworks f 
        LEFT JOIN documents d ON d.framework_id = f.id 
        WHERE d.id IS NULL
    """)
    missing_docs = cursor.fetchall()
    print("\nFrameworks without documents:")
    if missing_docs:
        for r in missing_docs:
            print(f"  Framework ID: {r[0]} | Name: {r[1]} | Filename: {r[2]}")
    else:
        print("  None")
        
    # 3. Foreign key check (PRAGMA foreign_key_check)
    cursor.execute("PRAGMA foreign_key_check")
    fk_errors = cursor.fetchall()
    print("\nForeign key check results:")
    if fk_errors:
        for err in fk_errors:
            print(f"  Table: {err[0]} | Rowid: {err[1]} | Parent: {err[2]} | Fkid: {err[3]}")
    else:
        print("  No foreign key violations")
        
    # 4. Check for suggestions details
    cursor.execute("SELECT id, type, action, target_name, parent_target, status FROM suggestions")
    sugs = cursor.fetchall()
    print("\nSuggestions details:")
    if sugs:
        for s in sugs:
            print(f"  ID: {s[0]} | Type: {s[1]} | Action: {s[2]} | Target: {s[3]} | Parent: {s[4]} | Status: {s[5]}")
    else:
        print("  None")

    conn.close()

if __name__ == "__main__":
    check_integrity()
