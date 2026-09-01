import pandas as pd
import sqlite3
import os

DB_PATH = "db/soil_health.sqlite"
INDICATOR_MATRIX_PATH = "principles_indicators/indicator_matrix_hierarchical.xlsx"

def populate_matrix():
    print("Connecting to DB...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Loading indicator matrix...")
    try:
        indicator_matrix = pd.read_excel(INDICATOR_MATRIX_PATH)
        first_col = indicator_matrix.columns[0]
        indicator_matrix = indicator_matrix.rename(columns={first_col: 'pdf_name'})
    except Exception as e:
        print(f"Failed to load indicator_matrix: {e}")
        return

    # Clear existing data in indicator_matrix (if we are repopulating)
    cursor.execute("DELETE FROM indicator_matrix")
    
    # Also fetch existing frameworks
    cursor.execute("SELECT id, filename FROM frameworks")
    fws = cursor.fetchall()
    
    # Build dictionary from pdf_name (without .pdf) to framework_id
    fw_map = {}
    for fw_id, fname in fws:
        if fname:
            sn = fname.replace(".pdf", "").strip().lower()
            fw_map[sn] = fw_id
            
    print(f"Found {len(fw_map)} frameworks in DB.")

    # Get principles and indicators mapping
    # We will insert missing principles and indicators
    cursor.execute("SELECT id, name FROM principles")
    principles_map = {row[1].lower().strip(): row[0] for row in cursor.fetchall()}
    
    cursor.execute("SELECT id, name FROM indicators")
    indicators_map = {row[1].lower().strip(): row[0] for row in cursor.fetchall()}

    cols = [c for c in indicator_matrix.columns if c != "pdf_name"]
    
    inserted_count = 0
    for index, row in indicator_matrix.iterrows():
        pdf_name_val = row["pdf_name"]
        if pd.isnull(pdf_name_val): continue
        target_sn = str(pdf_name_val).strip().lower().replace(".pdf", "")
        
        fw_id = fw_map.get(target_sn)
        if not fw_id:
            continue
            
        for c in cols:
            parts = str(c).split(" | ")
            if len(parts) >= 3:
                p = parts[1].strip()
                ind = parts[2].strip()
                val = row[c]
                val = float(val) if pd.notnull(val) else 0.0
                
                if val > 0:
                    p_lower = p.lower().strip()
                    if p_lower not in principles_map:
                        cursor.execute("INSERT INTO principles (name) VALUES (?)", (p,))
                        principles_map[p_lower] = cursor.lastrowid
                    p_id = principles_map[p_lower]
                    
                    ind_lower = ind.lower().strip()
                    if ind_lower not in indicators_map:
                        cursor.execute("INSERT INTO indicators (name) VALUES (?)", (ind,))
                        indicators_map[ind_lower] = cursor.lastrowid
                    ind_id = indicators_map[ind_lower]
                    
                    cursor.execute(
                        "INSERT INTO indicator_matrix (framework_id, principle_id, indicator_id, indicator_value) VALUES (?, ?, ?, ?)",
                        (fw_id, p_id, ind_id, val)
                    )
                    inserted_count += 1

    conn.commit()
    conn.close()
    print(f"Inserted {inserted_count} rows into indicator_matrix.")

if __name__ == "__main__":
    populate_matrix()
