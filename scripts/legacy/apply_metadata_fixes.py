import sqlite3
import json
import os

db_path = "db/soil_health.sqlite"
metadata_path = "data/framework_metadata.json"

fixes = [
    {
        "filename": "Andrews-SMAF.pdf",
        "title": "The Soil Management Assessment Framework: A Quantitative User Tool"
    },
    {
        "filename": "TEEB.pdf",
        "title": "The Economics of Ecosystems and Biodiversity: Mainstreaming the Economics of Nature (Synthesis Report)",
        "author_date": "TEEB (2010)"
    },
    {
        "filename": "USDA-CFSHAG.pdf",
        "title": "Soil Health Technical Note No. 450-06: Cropland In-Field Soil Health Assessment Guide"
    },
    {
        "filename": "Arshad-SQI.pdf",
        "doi_url": "https://doi.org/10.1016/S0167-8809(01)00252-3"
    },
    {
        "filename": "CICES.pdf",
        "title": "Common International Classification of Ecosystem Services (CICES) V5.1: A Guideline",
        "doi_url": "https://doi.org/10.3897/oneeco.3.e27108"
    },
    {
        "filename": "Common-4returns.pdf",
        "name": "Commonland et al 2021",
        "author_date": "Commonland et al (2021)"
    },
    {
        "filename": "Cornell-CASH.pdf",
        "name": "Moebius-Clune et al. 2016",
        "author_date": "Moebius-Clune, B. N., et al (2016)"
    },
    {
        "filename": "Deel-SEMWISE.pdf",
        "doi_url": "https://doi.org/10.1016/j.apsoil.2024.105260"
    },
    {
        "filename": "FAO-agroecology.pdf",
        "doi_url": "https://doi.org/10.4060/ca7173en"
    },
    {
        "filename": "FAO-VGSSM.pdf",
        "title": "Voluntary Guidelines for Sustainable Soil Management"
    }
]

def apply_fixes():
    print("=== Applying Metadata Fixes ===")
    
    # 1. Update Database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for fix in fixes:
        filename = fix["filename"]
        updates = []
        params = []
        for key, val in fix.items():
            if key != "filename":
                updates.append(f"{key} = ?")
                params.append(val)
        
        if updates:
            sql = f"UPDATE frameworks SET {', '.join(updates)} WHERE filename = ?"
            params.append(filename)
            cursor.execute(sql, params)
            print(f"  Updated DB: {filename}")
    
    conn.commit()
    conn.close()
    
    # 2. Update JSON
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        updated_count = 0
        for item in metadata:
            for fix in fixes:
                if item["filename"] == fix["filename"]:
                    for key, val in fix.items():
                        if key != "filename":
                            item[key] = val
                    updated_count += 1
        
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print(f"  Updated JSON: {updated_count} entries.")

if __name__ == "__main__":
    apply_fixes()
