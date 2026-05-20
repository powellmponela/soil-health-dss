import os
import sqlite3
import json
from db_utils import execute_query, execute_statement
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

BASE_PATH = "c:/SOIL HEALTH"
FW_DIR = os.path.join(BASE_PATH, "Frameworks")
DB_PATH = os.path.join(BASE_PATH, "db", "soil_health.sqlite")
JSON_PATH = os.path.join(BASE_PATH, "data", "framework_metadata.json")

def extract_pdf_text(filepath):
    if not PdfReader:
        return "pypdf not installed"
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        return f"Error: {e}"

def link_pdfs():
    print("=== Linking Frameworks Folder with Database ===")
    
    # 1. Get all PDFs in folder
    folder_files = [f for f in os.listdir(FW_DIR) if f.endswith('.pdf')]
    print(f"Found {len(folder_files)} PDFs in {FW_DIR}")
    
    # 2. Get all filenames in DB
    db_fws = execute_query("SELECT id, filename, name FROM frameworks")
    db_filenames = {fw['filename'] for fw in db_fws if fw['filename']}
    
    # 3. Identify missing PDFs in DB
    missing_in_db = [f for f in folder_files if f not in db_filenames]
    
    if missing_in_db:
        print(f"Adding {len(missing_in_db)} missing PDFs to database...")
        for fname in missing_in_db:
            name = fname.replace(".pdf", "")
            execute_statement(
                "INSERT INTO frameworks (name, title, filename, objective) VALUES (?, ?, ?, ?)",
                (name, name, fname, "Auto-Linked from Folder")
            )
            print(f"  Added: {fname}")
    else:
        print("All PDFs in folder are already in the database.")
        
    # 4. Ensure all frameworks have document entries and extracted text
    print("\nEnsuring all frameworks have document entries...")
    all_fws = execute_query("SELECT id, filename FROM frameworks WHERE filename IS NOT NULL AND filename != ''")
    
    for fw in all_fws:
        fw_id = fw['id']
        fname = fw['filename']
        
        # Check if document exists
        doc = execute_query("SELECT id, status, extracted_text FROM documents WHERE framework_id = ?", (fw_id,))
        
        if not doc:
            print(f"  Creating document entry for: {fname}")
            execute_statement("INSERT INTO documents (framework_id, filename, status) VALUES (?, ?, ?)", (fw_id, fname, "pending"))
            doc = execute_query("SELECT id, status, extracted_text FROM documents WHERE framework_id = ?", (fw_id,))
            
        # Extract text if pending or empty
        doc_entry = doc[0]
        if doc_entry['status'] != 'processed' or not doc_entry['extracted_text']:
            fpath = os.path.join(FW_DIR, fname)
            if os.path.exists(fpath):
                print(f"  Extracting text from: {fname}...")
                text = extract_pdf_text(fpath)
                execute_statement(
                    "UPDATE documents SET extracted_text = ?, status = ?, processed_at = datetime('now') WHERE framework_id = ?",
                    (text, "processed" if "Error:" not in text else "error", fw_id)
                )
            else:
                print(f"  PDF file not found for DB entry: {fname}")
                execute_statement("UPDATE documents SET status = ? WHERE framework_id = ?", ("missing", fw_id))

    print("\n=== Linking Complete ===")
    
    # Summary
    fw_count = execute_query("SELECT COUNT(*) as n FROM frameworks")[0]["n"]
    doc_count = execute_query("SELECT COUNT(*) as n FROM documents WHERE status = 'processed'")[0]["n"]
    print(f"Total Frameworks: {fw_count}")
    print(f"Processed Documents: {doc_count}")

if __name__ == "__main__":
    link_pdfs()
