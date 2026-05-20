import json

JSON_FILE = r"c:\SOIL HEALTH\principles_indicators\extracted_framework_terms.json"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\framework_word_by_word_extraction.txt"

def main():
    print("Loading data...")
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = []
    
    for fw_name, fw_content in sorted(data.items()):
        lines.append(f"==================================================")
        lines.append(f"Framework: {fw_name}")
        lines.append(f"==================================================")
        
        terms = fw_content.get("terms_found", [])
        # Sort by frequency then alphabetically
        terms = sorted(terms, key=lambda x: (-x.get("count", 0), x.get("term", "")))
        
        if not terms:
            lines.append("  No terms extracted.\n")
            continue
            
        for t in terms:
            term_str = t.get("term", "UNKNOWN")
            count = t.get("count", 0)
            principle = t.get("principle", "UNKNOWN")
            source = t.get("source", "UNKNOWN")
            lines.append(f"  - {term_str} (x{count}) [{principle}] [{source}]")
            
        lines.append("\n")

    print(f"Writing {len(lines)} lines to output...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Done! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
