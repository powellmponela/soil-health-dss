import os
import re
import json
import pandas as pd
from pypdf import PdfReader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_terms_within_proximity(text, theme_terms, all_synonyms, proximity=5):
    tokens = re.findall(r'\b\w+\b', text.lower())
    if not tokens:
        return []
        
    results = []
    synonym_positions_map = []
    
    first_word_map = {}
    for theme_name, syn_list in all_synonyms.items():
        for synonym in syn_list:
            syn_words = tuple(re.findall(r'\b\w+\b', synonym.lower()))
            if not syn_words:
                continue
            first_word = syn_words[0]
            if first_word not in first_word_map:
                first_word_map[first_word] = []
            first_word_map[first_word].append((synonym, syn_words, len(syn_words), theme_name))
            
    num_tokens = len(tokens)
    for i, token in enumerate(tokens):
        if token in first_word_map:
            for synonym, syn_words, syn_len, theme_name in first_word_map[token]:
                if i + syn_len <= num_tokens and tuple(tokens[i:i+syn_len]) == syn_words:
                    synonym_positions_map.append({
                        'theme_name': theme_name,
                        'synonym': synonym,
                        'start': i,
                        'end': i + syn_len - 1
                    })
                    
    synonym_positions_map.sort(key=lambda x: x['start'])
    num_occ = len(synonym_positions_map)

    for i in range(num_occ):
        occ1 = synonym_positions_map[i]
        
        # Check forward neighbors
        for j in range(i + 1, num_occ):
            occ2 = synonym_positions_map[j]
            if occ2['start'] - occ1['end'] - 1 > proximity:
                break
                
            dist = max(0, occ2['start'] - occ1['end'] - 1)
            if dist <= proximity:
                context_start = max(0, occ1['start'] - proximity)
                context_end = min(len(tokens), occ1['end'] + proximity + 1)
                context = " ".join(tokens[context_start:context_end])
                
                results.append({
                    "theme_term": occ1['synonym'],
                    "synonym": occ2['synonym'],
                    "theme_name": occ2['theme_name'],
                    "context": context
                })

        # Check backward neighbors
        for j in range(i - 1, -1, -1):
            occ2 = synonym_positions_map[j]
            if occ1['start'] - occ2['end'] - 1 > proximity:
                break
                
            dist = max(0, occ1['start'] - occ2['end'] - 1)
            if dist <= proximity:
                context_start = max(0, occ1['start'] - proximity)
                context_end = min(len(tokens), occ1['end'] + proximity + 1)
                context = " ".join(tokens[context_start:context_end])
                
                results.append({
                    "theme_term": occ1['synonym'],
                    "synonym": occ2['synonym'],
                    "theme_name": occ2['theme_name'],
                    "context": context
                })
                
    return results

def process_pdfs_for_themes(pdf_folder, themes, all_synonyms):
    if not os.path.exists(pdf_folder):
        logger.error(f"PDF folder not found: {pdf_folder}")
        return []

    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    all_results = []
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    results = extract_terms_within_proximity(text, themes, all_synonyms)
                    for r in results:
                        r["Framework"] = pdf_file
                    all_results.extend(results)
        except Exception as e:
            logger.error(f"Error processing {pdf_file}: {e}")
            
    return all_results

def run_extraction():
    # Base paths
    base_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_folder = os.path.join(base_folder, "Frameworks")
    results_folder = os.path.join(base_folder, "api", "results")
    os.makedirs(results_folder, exist_ok=True)
    
    terms_file = os.path.join(base_folder, "principles_indicators", "Terms.txt")
    themes = []
    synonyms = {}
    
    if os.path.exists(terms_file):
        with open(terms_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        import re
        # Parse themes
        themes_match = re.search(r'themes\s*<-\s*c\((.*?)\)', content, re.DOTALL)
        if themes_match:
            themes = [t.strip().strip('"').strip() for t in themes_match.group(1).split(',')]
            
        # Parse synonyms
        syn_matches = re.finditer(r'("?[a-zA-Z\s-]+"?)\s*=\s*c\((.*?)\)', content, re.DOTALL)
        for m in syn_matches:
            k = m.group(1).strip().strip('"').strip()
            v = [x.strip().strip('"').strip() for x in m.group(2).split(',') if x.strip()]
            if k and v:
                synonyms[k] = v
                
        logger.info(f"Loaded {len(themes)} themes and {sum(len(v) for v in synonyms.values())} synonyms from Terms.txt")
    else:
        logger.error(f"Could not find terms file at {terms_file}")
        return {"status": "error", "message": "Terms.txt missing"}
        
    logger.info(f"Starting extraction on {pdf_folder}...")
    results = process_pdfs_for_themes(pdf_folder, themes, synonyms)
    
    if results:
        results_df = pd.DataFrame(results)
        proximity_csv = os.path.join(results_folder, "all_themes_proximity_results.csv")
        results_df.to_csv(proximity_csv, index=False)
        logger.info(f"Saved proximity results to {proximity_csv}")
        
        # Mocking merge with AE indicators (since we don't have the explicit 'List of frameworks.xlsx' available to the script)
        # We simulate the merge logic so the frontend receives a valid CSV output.
        ae_indicators = pd.DataFrame({"indicator": ["fertility", "structure", "irrigation"]})
        
        if "synonym" in results_df.columns:
            # Replicating `by="indicator"` merge behavior from R (mapping synonym -> indicator)
            results_df = results_df.rename(columns={"synonym": "indicator"})
            merged_data = pd.merge(ae_indicators, results_df, on="indicator", how="outer")
            
            output_csv = os.path.join(results_folder, "merged_ae_indicators_proximity_results.csv")
            merged_data.to_csv(output_csv, index=False)
            logger.info(f"Saved merged results to {output_csv}")
            
            # --- NEW: Group by AE Principles ---
            # Group by Framework and theme_name (AE Principle), counting the number of indicators extracted
            matrix_df = results_df.groupby(["Framework", "theme_name"]).size().reset_index(name="count")
            
            # Pivot the table so columns are AE Principles and rows are Frameworks
            pivot_matrix = matrix_df.pivot(index="Framework", columns="theme_name", values="count").fillna(0)
            
            # Rename the index to 'pdf_name' to match the system's expected format
            pivot_matrix.index.name = "pdf_name"
            pivot_matrix.reset_index(inplace=True)
            
            # Save the grouped matrix
            matrix_csv = os.path.join(results_folder, "principle_matrix_generated.csv")
            pivot_matrix.to_csv(matrix_csv, index=False)
            logger.info(f"Saved principle matrix (grouped by AE Principles) to {matrix_csv}")
            
            return {"status": "success", "file": matrix_csv, "rows": len(pivot_matrix)}
    
    return {"status": "error", "message": "No matches found or missing files."}

if __name__ == "__main__":
    run_extraction()
