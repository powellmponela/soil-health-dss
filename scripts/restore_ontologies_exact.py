import json
import os

# Paths
INDEX_FILE = r"c:\SOIL HEALTH\principles_indicators\Ontology_index.json"
BASE_DIR = r"c:\SOIL HEALTH\principles_indicators\offline_storage"

def main():
    if not os.path.exists(INDEX_FILE):
        print("Error: Ontology_index.json not found.")
        return

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index = json.load(f)

    # List of sources to process
    sources = ["AGROVOC", "WORLD_BANK", "HASSET", "ILOSTAT", "UNBIS", "UNESCO", "WOCAT", "FAOSTAT", "HLPE", "BIOPHYSICAL", "MANUAL"]
    
    for src in sources:
        # Map source tag to folder name
        folder_name = src.lower()
        if src == "UNESCO": folder_name = "unesco_thesaurus"
        if src == "BIOPHYSICAL": folder_name = "biophysical_expansion"
        if src == "HLPE": folder_name = "hlpe_enriched"
        
        target_dir = os.path.join(BASE_DIR, folder_name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        src_data = {}
        total_found = 0

        for principle_name, principle_content in index.items():
            # Standardize principle name for keys (e.g., "Participation" to "13. Participation")
            # We will use a map to ensure consistency with the master
            p_map = {
                "Recycling": "1. Recycling",
                "Input Reduction": "2. Input Reduction",
                "Soil Health": "3. Soil Health",
                "Animal Health": "4. Animal Health",
                "Biodiversity": "5. Biodiversity",
                "Synergy": "6. Synergy",
                "Economic Diversification": "7. Economic Diversification",
                "Co-creation of Knowledge": "8. Co-creation of Knowledge",
                "Social Values and Diets": "9. Social Values and Diets",
                "Fairness": "10. Fairness",
                "Connectivity": "11. Connectivity",
                "Land Governance": "12. Land & Natural Resource Governance",
                "Participation": "13. Participation"
            }
            
            p_key = p_map.get(principle_name, principle_name)
            src_data[p_key] = {"key_terms": [], "indicators": []}

            sub_concepts = principle_content.get("sub_concepts", [])
            for item in sub_concepts:
                if item.get("source") == src:
                    # PRESERVE EXACT STRINGS
                    indicator_obj = {
                        "label": item.get("label"),
                        "source": src,
                        "uri": item.get("uri")
                    }
                    # Include Levels if they exist
                    if item.get("level_2"): indicator_obj["level_2"] = item.get("level_2")
                    if item.get("level_3"): indicator_obj["level_3"] = item.get("level_3")
                    
                    src_data[p_key]["indicators"].append(indicator_obj)
                    total_found += 1

        # Save
        output_file = os.path.join(target_dir, f"{folder_name}_ontology_compact.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(src_data, f, indent=4)
        
        print(f"Restored {src}: {total_found} terms -> {output_file}")

if __name__ == "__main__":
    main()
