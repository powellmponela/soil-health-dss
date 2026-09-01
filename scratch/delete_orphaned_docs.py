import sqlite3

def delete_orphans():
    conn = sqlite3.connect("db/soil_health.sqlite")
    cursor = conn.cursor()
    
    # Enable foreign keys just in case
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Find orphans first
    cursor.execute("""
        SELECT d.id, d.filename 
        FROM documents d 
        LEFT JOIN frameworks f ON d.framework_id = f.id 
        WHERE f.id IS NULL
    """)
    orphans = cursor.fetchall()
    
    if orphans:
        print(f"Found {len(orphans)} orphaned documents. Deleting...")
        for o in orphans:
            print(f"  Deleting document ID {o[0]} ({o[1]})")
            cursor.execute("DELETE FROM documents WHERE id = ?", (o[0],))
        conn.commit()
        print("Deletion completed successfully.")
    else:
        print("No orphaned documents found.")
        
    conn.close()

if __name__ == "__main__":
    delete_orphans()
