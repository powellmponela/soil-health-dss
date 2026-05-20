import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']
plt.rcParams['font.family'] = 'sans-serif'

# Constants
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LIST_OF_FRAMEWORKS_PATH = os.path.join(BASE_PATH, "References", "List of frameworks.xlsx")
OUTPUT_PATH_A = os.path.join(BASE_PATH, "api", "results", "figure2a_orientation.png")
OUTPUT_PATH_B = os.path.join(BASE_PATH, "api", "results", "figure2b_evolution.png")
FW_DIR = os.path.join(BASE_PATH, "Frameworks")

def generate_figure2():
    print("Generating Figure 2: Use-orientation over time...")
    
    # 1. Load Data
    try:
        df = pd.read_excel(LIST_OF_FRAMEWORKS_PATH, sheet_name='frameworks_categorised')
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return

    # 2. Clean Data
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)
    
    # Fill NAs with 0
    cols = ['Theoretical/principles', 'Practical approaches', 'Analytical']
    df[cols] = df[cols].fillna(0)
    
    # Sort by Year and then Title
    df = df.sort_values(['Year', 'short title'], ascending=[True, True])
    
    # 3. Figure 2a: Horizontal bar chart
    # ── Map labels to Author-Date (Abbreviation) ──────────────────────────
    import json
    META_PATH = os.path.join(BASE_PATH, "data", "framework_metadata.json")
    label_map = {}
    
    def normalize_key(k):
        return str(k).lower().strip().replace("_", "-").replace(".pdf", "")

    if os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            meta_data = json.load(f)
            for item in meta_data:
                fname = normalize_key(item["filename"])
                author_date = item.get("name", "Unknown")
                # Extract abbreviation from filename if it contains a hyphen
                if "-" in fname:
                    abbr = fname.split("-")[-1].upper()
                else:
                    abbr = fname.upper()
                label_map[fname] = f"{author_date} ({abbr})".replace('‐', '-').replace('\xa0', ' ')
    
    # 3. Transform for plotting — Only use the 64 PDFs in the folder
    pdfs_in_folder = [f for f in os.listdir(FW_DIR) if f.lower().endswith(".pdf")]
    pdf_norm_map = {normalize_key(f): f for f in pdfs_in_folder}
    
    plot_df = []
    for pdf_key, original_filename in pdf_norm_map.items():
        # Find match in Excel
        # Normalize Excel abbrev for matching
        excel_match = df[df['abbrev'].apply(normalize_key) == pdf_key]
        
        if not excel_match.empty:
            row = excel_match.iloc[0]
            label = label_map.get(pdf_key, f"{row['short title']} ({int(row['Year'])})").replace('‐', '-').replace('\xa0', ' ')
            
            if len(label) > 80:
                label = label[:77] + "..."
                
            if row['Theoretical/principles'] == 1:
                plot_df.append({'Framework': label, 'Orientation': 'Theoretical', 'Value': 1, 'Year': row['Year']})
            if row['Practical approaches'] == 1:
                plot_df.append({'Framework': label, 'Orientation': 'Practical', 'Value': 1, 'Year': row['Year']})
            if row['Analytical'] == 1:
                plot_df.append({'Framework': label, 'Orientation': 'Analytical', 'Value': 1, 'Year': row['Year']})
        else:
            # Fallback for PDFs not in Excel (should not happen with 64 sync, but for safety)
            label = label_map.get(pdf_key, original_filename)
            plot_df.append({'Framework': label, 'Orientation': 'Theoretical', 'Value': 0, 'Year': 2024})

    plot_df = pd.DataFrame(plot_df)
    # Sort by Year so it looks chronologically grouped
    plot_df = plot_df.sort_values('Year', ascending=True)
    
    plt.figure(figsize=(16, 20)) # Increased width for long labels
    sns.stripplot(data=plot_df, y='Framework', x='Orientation', hue='Orientation', 
                  palette={'Theoretical': 'green', 'Practical': 'red', 'Analytical': 'blue'},
                  size=10, jitter=False, dodge=False)
    
    plt.title("Figure 2a: Use-orientation of Reviewed Frameworks (n=64)", fontsize=22, fontweight='bold', pad=20)
    plt.grid(True, axis='y', linestyle='--', alpha=0.3)
    plt.subplots_adjust(left=0.4) # More space for y-labels
    plt.savefig(OUTPUT_PATH_A, dpi=300)
    print(f"Figure 2a saved to {OUTPUT_PATH_A}")

    # 4. Figure 2b: Evolution (Bubble chart)
    # Count occurrences per year
    evolution_df = df.groupby('Year')[cols].sum().reset_index()
    evolution_melted = evolution_df.melt(id_vars='Year', var_name='Orientation', value_name='Count')
    evolution_melted = evolution_melted[evolution_melted['Count'] > 0]
    
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=evolution_melted, x='Year', y='Orientation', size='Count', hue='Orientation',
                    sizes=(100, 2000), palette={'Theoretical/principles': 'green', 'Practical approaches': 'red', 'Analytical': 'blue'},
                    alpha=0.6, legend='brief')
    
    plt.title("Figure 2b: Distribution of Use-orientation Categories by Year", fontsize=22, fontweight='bold', pad=20)
    plt.xlabel("Year of Publication", fontsize=16, fontweight='bold')
    plt.ylabel("Orientation Category", fontsize=16, fontweight='bold')
    plt.xticks(sorted(df['Year'].unique()), rotation=45, fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH_B, dpi=300)
    print(f"Figure 2b saved to {OUTPUT_PATH_B}")

if __name__ == "__main__":
    generate_figure2()
