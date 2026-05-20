import os
import json
import datetime
from db_utils import init_db, execute_query, execute_statement
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

BASE_PATH = os.path.join(os.path.dirname(__file__), "..")
METADATA_PATH = os.path.join(BASE_PATH, "data", "framework_metadata.json")
REGISTRATIONS_PATH = os.path.join(BASE_PATH, "data", "registrations.json")
FW_DIR = os.path.join(BASE_PATH, "Frameworks")

def extract_pdf_text(filepath):
    if not PdfReader:
        raise Exception("pypdf not installed")
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def migrate_data():
    print("Initializing database schema...")
    init_db()

    print("=== Starting data migration ===")

    # Import framework metadata
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        print(f"Importing {len(metadata)} frameworks from metadata...")
        
        for item in metadata:
            existing = execute_query("SELECT id, title, publisher FROM frameworks WHERE filename = ?", (item.get("filename"),))
            if not existing:
                execute_statement(
                    """INSERT INTO frameworks (name, title, author_date, publisher, doi_url, filename, objective) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        item.get("name"), item.get("title"), item.get("author_date"), 
                        item.get("publisher"), item.get("doi_url"), item.get("filename"),
                        "Agroecological Assessment"
                    )
                )
            else:
                # Always sync all fields from JSON to keep DB up to date
                execute_statement(
                    """UPDATE frameworks SET name = ?, title = ?, author_date = ?, publisher = ?, doi_url = ? 
                       WHERE filename = ?""",
                    (
                        item.get("name"), item.get("title"), item.get("author_date"), 
                        item.get("publisher"), item.get("doi_url"), item.get("filename")
                    )
                )
        print("  Frameworks imported/updated.")
    else:
        print(f"  No metadata file found at: {METADATA_PATH}")

    # Import user registrations
    if os.path.exists(REGISTRATIONS_PATH):
        with open(REGISTRATIONS_PATH, "r", encoding="utf-8") as f:
            regs = json.load(f)
        print(f"Importing {len(regs)} registrations...")
        
        for item in regs:
            name = f"{item.get('authors', '')} ({item.get('date', '')})"
            existing = execute_query("SELECT id FROM frameworks WHERE filename = ?", (item.get("filename"),))
            if not existing:
                execute_statement(
                    """INSERT INTO frameworks (name, title, author_date, publisher, doi_url, filename, objective)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (name, item.get("title"), name, item.get("publisher"), item.get("url"), item.get("filename"), "User Registration")
                )
        print("  Registrations imported.")

    # Link PDFs — create document entries
    all_fws = execute_query("SELECT id, filename FROM frameworks WHERE filename IS NOT NULL AND filename != ''")
    if all_fws:
        print(f"Linking {len(all_fws)} PDFs to documents table...")
        
        for fw in all_fws:
            fw_id = fw["id"]
            fname = fw["filename"]
            
            existing_doc = execute_query("SELECT id FROM documents WHERE framework_id = ?", (fw_id,))
            if not existing_doc:
                execute_statement(
                    "INSERT INTO documents (framework_id, filename, status) VALUES (?, ?, ?)",
                    (fw_id, fname, "pending")
                )
        print("  Document links created.")

    # Extract text from pending PDFs
    pending = execute_query("SELECT id, filename FROM documents WHERE status = 'pending'")
    if pending:
        print(f"Extracting text from {len(pending)} PDFs...")
        
        success_count = 0
        for doc in pending:
            doc_id = doc["id"]
            fname = doc["filename"]
            fpath = os.path.join(FW_DIR, fname)
            
            if os.path.exists(fpath):
                try:
                    full_txt = extract_pdf_text(fpath)
                    execute_statement(
                        "UPDATE documents SET extracted_text = ?, status = 'processed', processed_at = datetime('now') WHERE id = ?",
                        (full_txt, doc_id)
                    )
                    success_count += 1
                except Exception as e:
                    print(f"  Error extracting {fname}: {e}")
                    execute_statement("UPDATE documents SET status = 'error' WHERE id = ?", (doc_id,))
            else:
                print(f"  PDF not found: {fname}")
                execute_statement("UPDATE documents SET status = 'missing' WHERE id = ?", (doc_id,))
        print(f"  Extracted text from {success_count}/{len(pending)} PDFs.")
    else:
        print("  No pending PDFs to extract.")

    # Summary
    fw_count = execute_query("SELECT COUNT(*) as n FROM frameworks")[0]["n"]
    doc_count = execute_query("SELECT COUNT(*) as n FROM documents")[0]["n"]
    processed = execute_query("SELECT COUNT(*) as n FROM documents WHERE status = 'processed'")[0]["n"]
    
    print("=== Migration Summary ===")
    print(f"  Frameworks: {fw_count}")
    print(f"  Documents:  {doc_count}")
    print(f"  Processed:  {processed}")
    print("=========================")

if __name__ == "__main__":
    migrate_data()
