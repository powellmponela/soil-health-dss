import pandas as pd
import json
import os

# Paths
MATRIX_FILE = r"c:\SOIL HEALTH\principles_indicators\indicator_matrix_hierarchical.xlsx"
OUTPUT_DIR = r"c:\SOIL HEALTH\principles_indicators\offline_storage"

def main():
    if not os.path.exists(MATRIX_FILE):
        print("Error: Matrix file not found.")
        return

    try:
        # Read the Excel file
        df = pd.read_excel(MATRIX_FILE)
        print(f"Successfully read matrix with {len(df)} rows.")
        
        # Look for columns that represent sources
        # Typical columns: 'Indicator', 'Principle', 'FAOSTAT', 'AGROVOC', etc.
        print(f"Columns: {df.columns.tolist()}")
        
        # We want to find all indicators and their sources
        # Let's assume the indicator is in a column named 'Indicator' or similar
        indicator_col = next((c for c in df.columns if 'indicator' in c.lower()), None)
        principle_col = next((c for c in df.columns if 'principle' in c.lower()), None)
        
        if not indicator_col:
            print("Error: Could not find indicator column.")
            return

        # List of potential source columns
        potential_sources = ["AGROVOC", "WORLD_BANK", "HASSET", "ILOSTAT", "UNBIS", "UNESCO", "WOCAT", "FAOSTAT", "HLPE"]
        source_cols = [c for c in df.columns if c.upper() in potential_sources]
        
        # If no specific source columns, maybe it's in a single 'Source' column
        source_id_col = next((c for c in df.columns if 'source' in c.lower()), None)

        # Let's build a mapping of Source -> Principle -> Indicators
        source_maps = {s: {} for s in potential_sources}
        
        for _, row in df.iterrows():
            indicator = str(row[indicator_col]).strip()
            principle = str(row[principle_col]).strip() if principle_col else "Uncategorized"
            
            if source_id_col:
                src = str(row[source_id_col]).strip().upper()
                if src in source_maps:
                    if principle not in source_maps[src]: source_maps[src][principle] = []
                    source_maps[src][principle].append(indicator)
            
            # Also check if there are binary columns for each source
            for sc in source_cols:
                if str(row[sc]).lower() in ['1', '1.0', 'x', 'yes', 'true']:
                    src = sc.upper()
                    if principle not in source_maps[src]: source_maps[src][principle] = []
                    source_maps[src][principle].append(indicator)

        # Now save each one
        for src, principles in source_maps.items():
            if not principles: continue
            
            folder_name = src.lower()
            if src == "UNESCO": folder_name = "unesco_thesaurus"
            target_file = os.path.join(OUTPUT_DIR, folder_name, f"{folder_name}_ontology_compact.json")
            
            # Construct the wide format
            wide_data = {}
            for p, inds in principles.items():
                wide_data[p] = {
                    "key_terms": [],
                    "indicators": [{"label": i, "source": src} for i in sorted(list(set(inds)))]
                }
            
            # Ensure target folder exists
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(wide_data, f, indent=4)
            
            print(f"Restored {src}: {sum(len(v) for v in principles.values())} indicators.")

    except Exception as e:
        print(f"Error processing matrix: {e}")

if __name__ == "__main__":
    main()
