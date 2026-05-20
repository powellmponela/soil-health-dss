import json
import os
import pandas as pd

JSON_MASTER = "principles_indicators/Ontology_index.json"
MATRIX_FILE = "principles_indicators/framework_principle_matrix.csv"
SOURCE_DIST_FILE = "principles_indicators/source_principle_distribution.csv"

def main():
    if not all(os.path.exists(f) for f in [JSON_MASTER, MATRIX_FILE, SOURCE_DIST_FILE]):
        print("Missing required analysis files.")
        return

    # 1. Load Data
    with open(JSON_MASTER, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    df_matrix = pd.read_csv(MATRIX_FILE)
    df_source = pd.read_csv(SOURCE_DIST_FILE, index_col=0)
    df_source = pd.read_csv(SOURCE_DIST_FILE).set_index('Unnamed: 0')

    # 2. Identify Gaps
    gap_report = []

    for principle in master_data.keys():
        # A. Absolute term count
        term_count = df_source.loc[principle, 'Total'] if principle in df_source.index else 0
        
        # B. Source Diversity (Number of sources contributing > 1% of terms)
        s_row = df_source.loc[principle].drop('Total')
        main_sources = s_row[s_row > (term_count * 0.01)].count()
        dominant_source = s_row.idxmax()
        dominant_pct = (s_row.max() / term_count) * 100 if term_count > 0 else 0

        # C. Research Detection (Average score in frameworks)
        # Note: Score labels in matrix have 'P_' prefix
        m_col = f"P_{principle}"
        detection_score = df_matrix[m_col].mean() if m_col in df_matrix.columns else 0

        gap_report.append({
            "Principle": principle,
            "Term Count": term_count,
            "Source Diversity": main_sources,
            "Dominant Source": f"{dominant_source} ({dominant_pct:.1f}%)",
            "Research Detection (Avg)": detection_score
        })

    df_gap = pd.DataFrame(gap_report)
    
    # 3. Highlight Gaps
    # Thresholds: 
    # - Low Count: < 1000
    # - Low Diversity: < 3 sources
    # - Low Detection: < 100
    
    print("\n=== Critical Gap Analysis: Agroecological Principle Representation ===")
    print(df_gap.sort_values(by='Term Count').to_markdown(index=False))

    print("\n--- Identified Risks ---")
    risks = []
    if (df_gap['Term Count'] < 500).any():
        risks.append("LOW VOLUME: 'Input Reduction' and 'Economic Diversification' have < 600 terms. Vulnerable to missing niche literature.")
    if (df_gap['Source Diversity'] < 4).any():
        risks.append("LOW DIVERSITY: Some principles are > 95% dependent on AGROVOC. Needs more 'Alternative' source injection.")
    if (df_gap['Research Detection (Avg)'] < 50).any():
        risks.append("LOW DETECTION: 'Connectivity' and 'Knowledge Co-creation' are rarely mentioned in the 64 biophysical frameworks.")

    for r in risks:
        print(f"  [!] {r}")

if __name__ == "__main__":
    main()
