import uvicorn
from migrate import migrate_data

if __name__ == "__main__":
    print("Running database migration...")
    try:
        migrate_data()
    except Exception as e:
        print(f"Migration failed: {e}")
        
    print("Starting FastAPI server...")
    uvicorn.run("logic:app", host="0.0.0.0", port=8000, reload=True)
