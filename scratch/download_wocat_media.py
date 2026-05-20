import requests
import os

DOWNLOAD_DIR = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\media_library"

PDF_MAP = {
    "SLM_in_Practice_Book_EN.pdf": "https://wocat.net/documents/1321/SLM_in_Practice_Guidelines_Best_Practices_SSA_English_web.pdf",
    "SLM_Practices_South_Africa.pdf": "https://wocat.net/documents/1319/South_Africa_SLM_Best_Practices_2024.pdf",
    "SLM_Technologies_Ethiopia.pdf": "https://wocat.net/documents/1206/LSR_low.pdf",
    "SLM_Compendium_India_2024.pdf": "https://wocat.net/documents/1318/INDIA_SLM_Compilation_FINAL_240902.pdf",
    "SLM_Compendium_Kenya_2024.pdf": "https://wocat.net/documents/1325/Kenya_Compilation_Final.pdf",
    "World_Atlas_Desertification_Full.pdf": "https://wocat.net/documents/1323/World_Atlas_of_Desertification_Full.pdf",
    "WOCAT_Technologies_Questionnaire_EN.pdf": "https://wocat.net/documents/420/Core_Questionnaire_Technologies_2019_English_July.pdf",
    "WOCAT_Technologies_Questionnaire_FR.pdf": "https://wocat.net/documents/833/Core_Questionnaire_Technologies_2019_French_low.pdf",
    "WOCAT_Approaches_Questionnaire_EN.pdf": "https://wocat.net/documents/59/QA_Core_EN__35mYmGh.pdf",
    "WOCAT_Approaches_Questionnaire_FR.pdf": "https://wocat.net/documents/61/QA_Core_FR_ISidgD0.pdf",
    "Water_Harvesting_Guidelines.pdf": "https://wocat.net/documents/1320/Water_Harvesting_Guidelines_Good_Practices_web.pdf",
    "DRR_Good_Practices_Compendium.pdf": "https://wocat.net/documents/1322/Where_People_and_Land_Safer_DRR_web.pdf",
    "Rangeland_Management_SSA_EN.pdf": "https://wocat.net/documents/1324/Sustainable_Rangeland_Management_SSA_English_web.pdf"
}

def download_pdfs():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        print(f"Created directory: {DOWNLOAD_DIR}")

    for filename, url in PDF_MAP.items():
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        print(f"Downloading {filename}...")
        try:
            response = requests.get(url, stream=True, timeout=60)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Successfully saved {filename}")
            else:
                print(f"Failed to download {filename} (Status: {response.status_code})")
        except Exception as e:
            print(f"Error downloading {filename}: {e}")

if __name__ == "__main__":
    download_pdfs()
