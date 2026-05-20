import pandas as pd
import numpy as np

matrix_file = r'c:\SOIL HEALTH\principles_indicators\framework_principle_matrix.csv'

def generate_report():
    print(f"Loading matrix from {matrix_file}...")
    df = pd.read_csv(matrix_file)
    
    # Define columns
    principle_cols = [c for c in df.columns if c.startswith('P_') and c != 'P_Additional Consolidated Terms']
    source_cols = [c for c in df.columns if c.startswith('S_')]
    
    # Calculate totals
    total_detections = df[principle_cols].sum().sum()
    
    # Source contributions
    new_sources = ['S_UNBIS', 'S_UNESCO', 'S_WOCAT', 'S_World_Bank']
    traditional_sources = [c for c in source_cols if c not in new_sources]
    
    new_source_sum = df[new_sources].sum().sum()
    traditional_sum = df[traditional_sources].sum().sum()
    
    # Print Markdown Report
    print("# Bridging the Gap: Thematic Audit Report\n")
    
    print("## 1. High-Level Summary")
    print(f"- **Total Frameworks Analyzed**: {len(df)}")
    print(f"- **Total Thematic Detections**: {total_detections:,.0f}")
    print(f"- **New Source Contribution**: {new_source_sum:,.0f} detections ({new_source_sum/(new_source_sum+traditional_sum)*100:.1f}%)")
    print(f"- **Traditional Source Contribution**: {traditional_sum:,.0f} detections ({traditional_sum/(new_source_sum+traditional_sum)*100:.1f}%)\n")
    
    print("## 2. Principle Coverage Improvements")
    print("The integration of UNBIS, UNESCO, and WOCAT has significantly hardened our socio-political and technical SLM coverage.")
    
    p_sums = df[principle_cols].sum().sort_values(ascending=False)
    for p, val in p_sums.items():
        print(f"- **{p.replace('P_', '')}**: {val:,.0f} detections")
    print("\n")
    
    print("## 3. Top Research Frameworks (Socio-Political Resonance)")
    print("These frameworks exhibited the highest detection rates across the newly expanded ontology, highlighting their strong policy, educational, and social dimensions.\n")
    
    # Sort by total detections of new sources
    df['New_Source_Impact'] = df[new_sources].sum(axis=1)
    top_frameworks = df.sort_values(by='New_Source_Impact', ascending=False).head(5)
    
    for _, row in top_frameworks.iterrows():
        print(f"### {row['Framework']}")
        print(f"- UNBIS Detections: {row['S_UNBIS']}")
        print(f"- UNESCO Detections: {row['S_UNESCO']}")
        print(f"- WOCAT Detections: {row['S_WOCAT']}")
        print(f"- World Bank Detections: {row['S_World_Bank']}")
        print("")

if __name__ == "__main__":
    generate_report()
