import pandas as pd
import os

MATRIX_FILE = "principles_indicators/framework_principle_matrix.csv"

def main():
    if not os.path.exists(MATRIX_FILE): return

    df = pd.read_csv(MATRIX_FILE)
    
    # Sort by a "Total Score" or just alphabetical
    # Let's add a Total column if not exists
    principles = [c for c in df.columns if c not in ['Framework', 'Total', 'Group']]
    df['Total'] = df[principles].sum(axis=1)
    
    df_sorted = df.sort_values(by='Total', ascending=False)

    # Save a clean version for the user
    # We'll use a subset of principles for the preview if it's too wide
    preview_cols = ['Framework'] + principles[:5] + ['Total']
    print("\n=== Framework x Principle Matrix (Top 15 by Total Indicators) ===")
    print(df_sorted[preview_cols].head(15).to_markdown(index=False))

    print(f"\nFull Matrix available at: {MATRIX_FILE}")
    print(f"Total Frameworks: {len(df)}")

if __name__ == "__main__":
    main()
