import sqlite3
import re

db_path = "c:/SOIL HEALTH/db/soil_health.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all frameworks with the generic title
cursor.execute("SELECT f.id, f.name, f.filename, d.extracted_text, f.title FROM frameworks f JOIN documents d ON f.id = d.framework_id")
rows = cursor.fetchall()

def extract_doi_url(text):
    if not text: return ""
    doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", text)
    if doi_match:
        return f"https://doi.org/{doi_match.group(0)}"
    
    url_match = re.search(r"https?://[a-zA-Z0-9./?=_-]+", text)
    if url_match:
        return url_match.group(0)
    return ""

updates = []

for row in rows:
    fw_id, name, filename, text, title = row
    
    new_title = title
    new_publisher = "-"
    new_doi = extract_doi_url(text)
    
    # Mapping of common abbreviations to publishers
    pub_map = {
        'FAO': 'Food and Agriculture Organization of the United Nations (FAO)',
        'UNEP': 'United Nations Environment Programme (UNEP)',
        'EEA': 'European Environment Agency (EEA)',
        'European Commission': 'European Commission',
        'IFA': 'International Fertilizer Association (IFA)',
        'AGRF': 'Alliance for a Green Revolution in Africa (AGRF)',
        'NEPAD': 'African Union Development Agency (NEPAD)',
        'CGIAR': 'CGIAR Initiative on Agroecology',
        'Cornell': 'Cornell University',
        'USDA': 'United States Department of Agriculture (USDA)',
        'Millennium Ecosystem Assessment': 'Millennium Ecosystem Assessment',
        'World Bank': 'World Bank Group',
        'HLPE': 'High Level Panel of Experts (HLPE)',
    }

    # Check author_date and title for publisher mentions
    for key, val in pub_map.items():
        if key.lower() in (name or "").lower() or key.lower() in (title or "").lower():
            new_publisher = val
            break

    # Journal extraction from text if available
    if text:
        if "Soil Science Society of America Journal" in text:
            new_publisher = "Soil Science Society of America Journal"
        elif "Agronomy for Sustainable Development" in text:
            new_publisher = "Agronomy for Sustainable Development"
        elif "Nature" in text[:500]:
            new_publisher = "Nature Publishing Group"
        elif "Science" in text[:500]:
            new_publisher = "AAAS"
        elif "Frontiers in" in text[:500]:
            new_publisher = "Frontiers Media"
        elif "Elsevier" in text[:500] or "ScienceDirect" in text:
            new_publisher = "Elsevier / ScienceDirect"

    # Specific overrides for prominent frameworks
    if "1000 Landscapes" in name:
        new_publisher = "1000 Landscapes for 1 Billion People"
        if "2022a" in name:
            new_title = "A Practical Guide to Integrated Landscape Management"
            new_doi = "https://landscapes.global/"
        elif "2022b" in name:
            new_title = "Integrated Landscape Management Tool Guide"
            new_doi = "https://terraso.org/"
    elif "Alcamo" in name:
        new_publisher = "Millennium Ecosystem Assessment"
        new_title = "Ecosystems and Human Well-being: A Framework for Assessment"
    elif "Apfelbaum" in name:
        new_publisher = "Applied Ecological Services (AES)"
    elif "Andrews" in name and "2004" in name:
        new_publisher = "Soil Science Society of America Journal"
    elif "FAO" in name or "FAO" in title:
        new_publisher = "FAO"
        if "TAPE" in title or "2019" in name:
             new_title = "Tool for Agroecology Performance Evaluation (TAPE) - Guidelines for application"
    elif "Arshad" in name:
        new_publisher = "Journal of Applied Ecology"
    elif "AGRF" in name:
        new_publisher = "AGRF"
        new_title = "Soil Initiative for Africa: Framework Document"

    updates.append((new_title, new_publisher, new_doi, fw_id))

if updates:
    cursor.executemany("UPDATE frameworks SET title = ?, publisher = ?, doi_url = ? WHERE id = ?", updates)
    conn.commit()
    print(f"Updated {len(updates)} frameworks with better metadata.")

conn.close()
