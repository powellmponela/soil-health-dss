import os
import re
import json
import math
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import subprocess
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
# Monkeypatch for NumPy 2.x compatibility with dynamicTreeCut
if not hasattr(np, 'in1d'):
    np.in1d = np.isin
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
import dynamicTreeCut
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from db_utils import execute_query, execute_statement
from migrate import extract_pdf_text
from ontology_utils import batch_enrich_terms, load_principles_map

def link_pdfs_logic():
    # Folder scan logic
    folder_files = [f for f in os.listdir(FW_DIR) if f.endswith('.pdf')]
    db_fws = execute_query("SELECT filename FROM frameworks")
    db_filenames = {fw['filename'] for fw in db_fws if fw['filename']}
    
    missing_in_db = [f for f in folder_files if f not in db_filenames]
    added_count = 0
    for fname in missing_in_db:
        name = fname.replace(".pdf", "")
        execute_statement(
            "INSERT INTO frameworks (name, title, filename, objective) VALUES (?, ?, ?, ?)",
            (name, name, fname, "Auto-Linked from Folder")
        )
        added_count += 1
        
    # Document ensuring
    all_fws = execute_query("SELECT id, filename FROM frameworks WHERE filename IS NOT NULL AND filename != ''")
    processed_count = 0
    for fw in all_fws:
        fw_id = fw['id']
        fname = fw['filename']
        doc = execute_query("SELECT id, status, extracted_text FROM documents WHERE framework_id = ?", (fw_id,))
        
        if not doc:
            execute_statement("INSERT INTO documents (framework_id, filename, status) VALUES (?, ?, ?)", (fw_id, fname, "pending"))
            doc = execute_query("SELECT id, status, extracted_text FROM documents WHERE framework_id = ?", (fw_id,))
            
        doc_entry = doc[0]
        if doc_entry['status'] != 'processed' or not doc_entry['extracted_text']:
            fpath = os.path.join(FW_DIR, fname)
            if os.path.exists(fpath):
                text = extract_pdf_text(fpath)
                execute_statement(
                    "UPDATE documents SET extracted_text = ?, status = ?, processed_at = datetime('now') WHERE framework_id = ?",
                    (text, "processed" if "Error:" not in text else "error", fw_id)
                )
                processed_count += 1
    return added_count, processed_count
class EvaluationRequest(BaseModel):
    framework_id: str

class SuggestionSubmission(BaseModel):
    type: str  # 'indicator_principle' or 'framework'
    action: str  # 'addition' or 'deletion'
    target_name: str
    parent_target: Optional[str] = None
    evidence_url: Optional[str] = None
    contact_details: Optional[str] = None

class SuggestionAction(BaseModel):
    status: str
    dev_response: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_PATH = os.path.join(os.path.dirname(__file__), "..")
FW_DIR = os.path.join(BASE_PATH, "Frameworks")
REGISTRATIONS_PATH = os.path.join(BASE_PATH, "data", "registrations.json")
PRINCIPLE_MATRIX_PATH = os.path.join(BASE_PATH, "principles_indicators", "principle_matrix.xlsx")
INDICATOR_MATRIX_PATH = os.path.join(BASE_PATH, "principles_indicators", "indicator_matrix_hierarchical.xlsx")
AGRONTOLOGY_MATRIX_PATH = os.path.join(BASE_PATH, "principles_indicators", "framework_principle_matrix.csv")
EXTRACTED_TERMS_PATH = os.path.join(BASE_PATH, "principles_indicators", "extracted_framework_terms.json")
MASTER_ONTOLOGY_PATH = os.path.join(BASE_PATH, "principles_indicators", "offline_storage", "master_agroecological_ontology.json")

# Mount static files for results
RESULTS_DIR = os.path.join(BASE_PATH, "api", "results")
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)
app.mount("/results", StaticFiles(directory=RESULTS_DIR), name="results")
app.mount("/Frameworks", StaticFiles(directory=FW_DIR), name="Frameworks")

# ── Shared Clustering Helpers ──────────────────────────────────────────
def run_dynamic_cut(hc_linkage, dist_mat, deep_split=2, min_cluster_size=3):
    res = dynamicTreeCut.cutreeHybrid(
        hc_linkage, distM=dist_mat,
        deepSplit=deep_split, minClusterSize=min_cluster_size, pamStage=True
    )
    return np.array(res["labels"])

def merge_to_k(mat, cl, k, hc_linkage=None):
    valid_ids = sorted(set(cl) - {0})
    n = len(valid_ids)
    if n == 0:
        return fcluster(hc_linkage, k, criterion="maxclust") if hc_linkage is not None else np.ones(mat.shape[0], dtype=int)
    if n <= k:
        id_map = {old: (i + 1) for i, old in enumerate(valid_ids)}
        return np.array([id_map.get(c, 0) for c in cl])
    
    centroids = np.vstack([mat[cl == g].mean(axis=0) for g in valid_ids])
    d_c = pdist(centroids, metric="euclidean")
    hc_c = linkage(d_c, method="complete")
    map_new = fcluster(hc_c, k, criterion="maxclust")
    id_to_new = {old: int(map_new[i]) for i, old in enumerate(valid_ids)}
    return np.array([id_to_new.get(c, 0) for c in cl])

# ── Load matrices ──────────────────────────────────────────────────────
try:
    principle_matrix = pd.read_excel(PRINCIPLE_MATRIX_PATH)
except Exception as e:
    print(f"Failed to load principle_matrix: {e}")
    principle_matrix = None

try:
    indicator_matrix = pd.read_excel(INDICATOR_MATRIX_PATH)
    # Rename first column to pdf_name if it is unnamed
    first_col = indicator_matrix.columns[0]
    if str(first_col).startswith('Unnamed') or first_col != 'pdf_name':
        indicator_matrix = indicator_matrix.rename(columns={first_col: 'pdf_name'})
except Exception as e:
    print(f"Failed to load indicator_matrix: {e}")
    indicator_matrix = None

try:
    agrontology_matrix = pd.read_csv(AGRONTOLOGY_MATRIX_PATH)
    # The first column is "Framework", rename to "pdf_name" for consistency
    first_col = agrontology_matrix.columns[0]
    agrontology_matrix = agrontology_matrix.rename(columns={first_col: 'pdf_name'})
except Exception as e:
    print(f"Failed to load agrontology_matrix: {e}")
    agrontology_matrix = None

design_mapping = {
    "Soil-health Assessment (Diagnostics)": ["Soil health"],
    "Soil Management (Stewardship)": ["Recycling", "Input reduction", "Animal health"],
    "Agroecological & Ecosystem (Safeguards)": ["Biodiversity", "Synergy"],
    "Integrated Landscape & Livelihood (Embedding)": ["Economic diversification", "Connectivity", "Land and natural resource governance"],
    "Policy & Outcome (Iterative Learning)": ["Co-creation of knowledge", "Social values and diets", "Fairness", "Participation"]
}

def list_fws_internal():
    fws = execute_query("SELECT id, name, title, author_date, publisher, doi_url, filename, objective FROM frameworks ORDER BY name")
    for fw in fws:
        fw["status"] = "Active"
    return fws

@app.get("/frameworks")
def get_frameworks():
    fws = list_fws_internal()
    return fws if fws else []

@app.post("/frameworks/register")
async def register_framework(
    upload_type: str = Form(...),
    authors: str = Form(...),
    date: str = Form(...),
    publisher: str = Form(...),
    title: str = Form(...),
    person: str = Form(...),
    right_to_share: str = Form(...),
    url: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    clean_author = re.sub(r'[^A-Za-z0-9]', '_', authors)
    new_filename = f"{clean_author}_{date}.pdf"
    target_path = os.path.join(FW_DIR, new_filename)
    
    if upload_type == "file" and file:
        content = await file.read()
        with open(target_path, "wb") as f:
            f.write(content)
            
    name = f"{authors} ({date})"
    
    execute_statement(
        """INSERT INTO frameworks (name, title, author_date, publisher, doi_url, filename, objective)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, title, name, publisher, url, new_filename, "User Registration")
    )
    
    fw_res = execute_query("SELECT id FROM frameworks WHERE filename = ?", (new_filename,))
    if fw_res:
        fw_id = fw_res[0]["id"]
        execute_statement(
            "INSERT INTO documents (framework_id, filename, status) VALUES (?, ?, ?)",
            (fw_id, new_filename, "pending")
        )
        
        if os.path.exists(target_path):
            try:
                full_txt = extract_pdf_text(target_path)
                execute_statement(
                    "UPDATE documents SET extracted_text = ?, status = 'processed', processed_at = datetime('now') WHERE framework_id = ?",
                    (full_txt, fw_id)
                )
            except Exception:
                execute_statement("UPDATE documents SET status = 'error' WHERE framework_id = ?", (fw_id,))
                
    return {"status": "success", "filename": new_filename, "label": name}

@app.post("/evaluate")
def evaluate(req: EvaluationRequest):
    framework_id = req.framework_id
    target_sn = framework_id
    
    if framework_id.isdigit():
        idx = int(framework_id)
        all_fws = list_fws_internal()
        match = next((f for f in all_fws if f["id"] == idx), None)
        if match and match["filename"]:
            target_sn = re.sub(r'\.pdf$', '', match["filename"])
    elif framework_id.endswith(".pdf"):
        target_sn = re.sub(r'\.pdf$', '', framework_id)
        
    def get_summary_scores(matrix, is_percentage=True, is_agrontology=False):
        if matrix is None: return []
        row = matrix[matrix['pdf_name'].str.lower().str.strip() == target_sn.lower().strip()]
        if row.empty: return []
        row = row.iloc[0]
        
        # Determine principle columns
        if is_agrontology:
            # Agrontology matrix has Framework, BestBackend, then 13 principles starting with P_
            orig_cols = matrix.columns[2:15]
        else:
            # Mponela matrix has pdf_name, then 13 principles
            orig_cols = matrix.columns[1:14]
            
        def normalize_principle_name(p):
            p = str(p).replace('\xa0', ' ').replace('P_', '').strip()
            # Standard mapping for common variations
            mapping = {
                "animal health": "Animal Health",
                "biodiversity": "Biodiversity",
                "co-creation of knowledge": "Co-creation of Knowledge",
                "connectivity": "Connectivity",
                "economic diversification": "Economic Diversification",
                "fairness": "Fairness",
                "input reduction": "Input Reduction",
                "land governance": "Land and Natural Resource Governance",
                "land and natural resource governance": "Land and Natural Resource Governance",
                "participation": "Participation",
                "recycling": "Recycling",
                "social values and diets": "Social Values and Diets",
                "soil health": "Soil Health",
                "synergy": "Synergy"
            }
            return mapping.get(p.lower(), p)

        scores = []
        for i, p_orig in enumerate(orig_cols):
            val = row[p_orig]
            if is_percentage:
                score = min(1, float(val) / 100.0) if pd.notnull(val) else 0.0
            else:
                # Normalize counts relative to max for this principle across all frameworks
                max_val = matrix[p_orig].max()
                score = min(1, float(val) / max_val) if pd.notnull(val) and max_val > 0 else 0.0
            scores.append({"principle": normalize_principle_name(p_orig), "score": score})
        
        # Sort scores by the standard order defined in App.js if possible
        order = ["Recycling", "Input Reduction", "Soil Health", "Animal Health", "Biodiversity", "Synergy", "Economic Diversification", "Co-creation of Knowledge", "Social Values and Diets", "Fairness", "Connectivity", "Land and Natural Resource Governance", "Participation"]
        scores.sort(key=lambda x: order.index(x["principle"]) if x["principle"] in order else 99)
        return scores

    def get_design_scores(summary_scores):
        if not summary_scores: return []
        d_scores = []
        for dp, relevant_agro in design_mapping.items():
            display_name = dp.split(" (")[1].replace(")", "") if " (" in dp else dp
            scores_subset = [s["score"] for s in summary_scores if s["principle"].lower() in [ra.lower() for ra in relevant_agro]]
            avg_score = sum(scores_subset) / len(scores_subset) if scores_subset else 0.0
            d_scores.append({"principle": display_name, "score": avg_score})
        return d_scores

    def get_recommendation(summary_scores, source_name):
        if not summary_scores: return ""
        sorted_scores = sorted(summary_scores, key=lambda x: x["score"], reverse=True)
        top_2 = sorted_scores[:2]
        bottom_1 = sorted_scores[-1]
        
        rec_text = f"[{source_name}] Strongest alignment in {top_2[0]['principle'].title()} ({int(top_2[0]['score']*100)}%)"
        if len(top_2) > 1:
            rec_text += f" and {top_2[1]['principle'].title()} ({int(top_2[1]['score']*100)}%)"
        
        if bottom_1['score'] < 0.3:
            rec_text += f". Alignment gap identified in {bottom_1['principle'].title()}."
        return rec_text

    mponela_summary = get_summary_scores(principle_matrix, is_percentage=True, is_agrontology=False)
    agrontology_summary = get_summary_scores(agrontology_matrix, is_percentage=False, is_agrontology=True)
    
    mponela_design = get_design_scores(mponela_summary)
    agrontology_design = get_design_scores(agrontology_summary)
    
    mponela_rec = get_recommendation(mponela_summary, "Mponela et al. 2026")
    agrontology_rec = get_recommendation(agrontology_summary, "Current Ontology")
    
    detailed_scores = []
    if indicator_matrix is not None:
        row = indicator_matrix[indicator_matrix['pdf_name'].str.lower().str.strip().str.replace(".pdf", "", regex=False) == target_sn.lower().strip()]
        if not row.empty:
            row = row.iloc[0]
            cols = [c for c in indicator_matrix.columns if c != "pdf_name"]
            
            p_dict = {}
            for c in cols:
                parts = c.split(" | ")
                if len(parts) >= 3:
                    p = parts[1].strip()
                    ind = parts[2].strip()
                    val = row[c]
                    val = float(val) if pd.notnull(val) else 0.0
                    
                    if p not in p_dict:
                        p_dict[p] = []
                    p_dict[p].append({"name": ind, "score": val})
                    
            for p, inds in p_dict.items():
                detailed_scores.append({"principle": p, "indicators": inds})
                
    if mponela_summary or agrontology_summary:
        res = {
            "status": "success",
            "framework": target_sn,
            "mponela": {
                "scores": mponela_summary,
                "design_scores": mponela_design,
                "recommendation": mponela_rec
            },
            "agrontology": {
                "scores": agrontology_summary,
                "design_scores": agrontology_design,
                "recommendation": agrontology_rec,
                "terms": []
            },
            "detailed": detailed_scores,
            "scores": mponela_summary,
            "design_scores": mponela_design,
            "recommendation": mponela_rec
        }
        
        # Add Agrontology terms if available
        if os.path.exists(EXTRACTED_TERMS_PATH):
            try:
                with open(EXTRACTED_TERMS_PATH, "r", encoding="utf-8") as f:
                    all_extracted = json.load(f)
                    match_key = next((k for k in all_extracted.keys() if k.lower() == target_sn.lower() or k.lower().replace('.pdf','').strip() == target_sn.lower().strip()), None)
                    if match_key:
                        res["agrontology"]["terms"] = all_extracted[match_key].get("terms_found", [])
            except Exception as e:
                print(f"Error loading extracted terms: {e}")
                
        return res
        
    return {"status": "error", "message": f"Framework data not found for: {target_sn}"}

# ── Predefined clusters from Integrated framework R4 ──────────────────
# Maps pdf_name (as it appears in principle_matrix) → cluster ID (1–5)
# Cluster themes:
#   1 = Agroecology & ecosystem
#   1 = Domain 1: Diagnostics (Soil-health Assessment)
#   2 = Domain 2: Stewardship (Soil Management)
#   3 = Domain 3: Safeguards (Agroecological & Ecosystem)
#   4 = Domain 4: Embedding (Integrated Landscape & Livelihood)
#   5 = Domain 5: Iterative Learning (Policy & Outcome)
PREDEFINED_CLUSTERS = {
    # Domain 2 – Stewardship (Soil Management) (10)
    "cornell-cash":          2, "nestle-raf":         2,
    "eea-smeitsha":          2, "fao-agroecology":    2,
    "ejp-siren":             2, "ftf_gsiaf":          2,
    "ifdc-fsha":             2, "eu-ss2030":          2,
    "fao-vgssm":             2, "teeb":               2,
    # Alternate casings for robustness
    "Cornell-CASH":          2, "nestle-RAF":         2,
    "EEA-SMEITSHA":          2, "FAO-agroecology":    2,
    "EJP-SIREN":             2, "FtF_GSIAF":          2,
    "IFDC-FSHA":             2, "EU-SS2030":          2,
    "FAO-VGSSM":             2, "TEEB":               2,

    # Domain 1 – Diagnostics (Soil Health Assessment) (16)
    "deel-semwise":          1, "covind-dus":         1,
    "ifa-g4rnutstewf":       1, "ros-oshafssm":       1,
    "andrews-smaf":          1, "fao-passm":          1,
    "ghimire-sham4wle":      1, "nunes-shape":        1,
    "lehmann-fpsh":          1, "steve-aesshf":       1,
    "stockdale-cfmsh":       1, "usda-cfshag":        1,
    "arshad-sqi":            1, "jian-dgsha":         1,
    "devine-rscfish":        1, "montg-shohph":       1,
    # Alternate casings
    "Deel-SEMWISE":          1, "govind-DUS":         1,
    "IFA-G4RNutStewF":       1, "Ros-OSHAFSSM":       1,
    "Andrews-SMAF":          1, "FAO-PASSM":          1,
    "Gwimire-SHAM4WLE":      1, "Nunes-SHAPE":        1,
    "Lehmann-FPSH":          1, "Steve-AESSHF":       1,
    "Stockdale-CFMSH":       1, "USDA-CFSHAG":        1,
    "Arshad-SQI":            1, "Jian-DGSHA":         1,
    "Devine-RSCFISH":        1, "Montg-SHOHPH":       1,

    # Domain 3 – Safeguards (Agroecological & Ecosystem-Based) (12)
    "ciat-isfm":             3, "fao-esfsi":          3,
    "permaculture":          3, "fao-tape":           3,
    "tittonel-sysageco":     3, "caadp":              3,
    "mea":                   3, "wri-ehwb":           3,
    "common_4returns":       3, "fao-almsfa":         3,
    "common-4returns":       3, "unccd-ldn":          3,
    # Alternate casings
    "CIAT-ISFM":             3, "FAO-ESFSI":          3,
    "Permaculture":          3, "FAO-TAPE":           3,
    "Tittonel-sysageco":     3, "CAADP":              3,
    "MEA":                   3, "WRI-EHWB":           3,
    "Common-4returns":       3, "FAO-ALMSFA":         3,
    "UNCCD-LDN":             3,

    # Domain 4 – Embedding (Integrated Landscape & Livelihood) (23)
    "ski-lstoolkit":         4, "sayer_la":           4,
    "fao-gspaf":             4, "ifpri-gr":           4,
    "cices":                 4, "4rns-inue":          4,
    "ldn_cf_journal":        4, "birner-pepsa":        4,
    "la4aa":                 4, "si4af":              4,
    "mesmis":                4, "wezel-tape":         4,
    "ids-srlf":              4, "fsat":               4,
    "posthumus-fsdst":       4, "unccd-ilm":          4,
    "cgiar-ll":              4, "mn-shaf":            4,
    "ilm-practical":         4, "ipes-food":          4,
    "cbd-nea":               4, "ploeg-peae":         4,
    "ilm-tool-guide":        4,
    # Alternate casings
    "SKI-LStoolkit":         4, "sayer-LA":           4,
    "FAO-GSPAF":             4, "IFPRI-GR":           4,
    "CICES":                 4, "4RNS-INUE":          4,
    "LDN_CF_journal":        4, "Birner-PEPSA":        4,
    "LA4AA":                 4, "SI4AF":              4,
    "MESMIS":                4, "Wezel-TAPE":         4,
    "IDS-SRLF":              4, "FSAT":               4,
    "Posthumus-FSDST":       4, "UNCCD-ILM":          4,
    "cgiar-ll":              4, "MN-SHAF":            4,
    "ILM-Practical":         4, "IPES-FOOD":          4,
    "CBD-NEA":               4, "Ploeg-PEAE":         4,
    "ILM_Tool_Guide":        4, "ILM-tool-guide":     4,

    # Domain 5 – Iterative Learning (Policy-Outcome Oriented) (4)
    "ejp-shttas":            5, "caadpresult":        5,
    "sai-raag":              5, "cbd":                5,
    # Alternate casings
    "ejp-SHTTAS":            5, "CAADPresult":        5,
    "SAI-RAAG":              5, "CBD":                5,
}

CLUSTER_THEMES = {
    1: "Domain 1: Diagnostics (Soil-health Assessment)",
    2: "Domain 2: Stewardship (Soil Management)",
    3: "Domain 3: Safeguards (Agroecological & Ecosystem)",
    4: "Domain 4: Embedding (Integrated Landscape & Livelihood)",
    5: "Domain 5: Iterative Learning (Policy & Outcome)"
}

PRINCIPLE_GROUP_NAMES = {
    1: "Environmental/Ecological",
    2: "Socio-Economic/Governance",
    3: "Institutional/Knowledge"
}

@app.get("/analyse/cluster")
def cluster_analysis():
    if principle_matrix is None:
        return {"status": "error", "message": "Matrix not loaded"}

    # 1. Clean and normalize
    mat = principle_matrix.iloc[:, 1:14].copy()
    mat.index = principle_matrix['pdf_name']
    mat_z = (mat - mat.mean()) / mat.std().replace(0, 1)
    mat_plot = mat_z.clip(-3, 3).fillna(0)

    # 2. Row Clustering (Frameworks) -> k=5
    dist_row = pdist(mat_plot.values, metric="euclidean")
    hc_row = linkage(dist_row, method="complete")
    distM_row = squareform(dist_row)
    
    row_cl_dyn = run_dynamic_cut(hc_row, distM_row, deep_split=2, min_cluster_size=3)
    row_cl5 = merge_to_k(mat_plot.values, row_cl_dyn, k=5, hc_linkage=hc_row)

    # 3. Column Clustering (Principles) -> k=3
    dist_col = pdist(mat_plot.values.T, metric="euclidean")
    hc_col = linkage(dist_col, method="complete")
    distM_col = squareform(dist_col)
    
    col_cl_dyn = run_dynamic_cut(hc_col, distM_col, deep_split=2, min_cluster_size=2)
    col_cl3 = merge_to_k(mat_plot.values.T, col_cl_dyn, k=3, hc_linkage=hc_col)

    # 4. Map back to themes and names
    all_fws = list_fws_internal()
    from collections import defaultdict
    groups = defaultdict(list)
    
    for i, sn in enumerate(mat.index):
        cl_id = int(row_cl5[i])
        match = next(
            (f for f in all_fws
             if f["filename"] and re.sub(r'\.pdf$', '', f["filename"]).lower().strip() == sn.lower().strip()),
            None
        )
        display_name = match["name"] if match else sn
        groups[cl_id].append(display_name)

    cluster_list = []
    for cl_id in sorted(groups.keys()):
        cluster_list.append({
            "group": cl_id,
            "theme": CLUSTER_THEMES.get(cl_id, f"Cluster {cl_id}"),
            "frameworks": sorted(groups[cl_id])
        })

    # Add principle groupings for the dashboard
    principle_groups = []
    principles = mat.columns.tolist()
    for i in range(1, 4):
        p_list = [principles[j] for j, cid in enumerate(col_cl3) if cid == i]
        principle_groups.append({
            "group": i,
            "name": PRINCIPLE_GROUP_NAMES.get(i, f"Group {i}"),
            "principles": [str(p).replace('\xa0', ' ').strip() for p in p_list]
        })

    return {
        "framework_clusters": cluster_list,
        "principle_groups": principle_groups
    }

@app.get("/analyse/nlp-cluster")
def nlp_cluster_analysis():
    docs = execute_query(
        "SELECT d.framework_id, d.extracted_text, f.name "
        "FROM documents d "
        "JOIN frameworks f ON d.framework_id = f.id "
        "WHERE d.extracted_text IS NOT NULL AND trim(d.extracted_text) != ''"
    )
    if not docs:
        return {"status": "error", "message": "No extracted text found in database."}

    def clean_text_ai(text):
        if not text: return ""
        # 1. Basic Cleaning
        text = text.lower()
        text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', ' ', text) # Emails
        text = re.sub(r'https?://\S+|www\.\S+', ' ', text) # URLs
        text = re.sub(r'10\.\d{4,9}/\S+', ' ', text) # DOIs
        text = re.sub(r'\b\d{4,}\b', ' ', text) # Long numbers
        
        # 2. Expansion of abbreviations
        abbrev_map = {
            "sq": "soil quality", "ldn": "land degradation neutrality",
            "es": "ecosystem services", "soc": "soil organic carbon",
            "ghg": "greenhouse gas", "sdg": "sustainable development goals"
        }
        for ab, full in abbrev_map.items():
            text = re.sub(r'\b' + ab + r'\b', full, text)

        # 3. Remove special chars
        text = re.sub(r'[^a-z\s]', ' ', text)
        
        # 4. Tokenize and Filter
        noise = {
            "soil", "health", "framework", "indicator", "indicators", "principles", "principle",
            "assessment", "management", "system", "systems", "agricultural", "agriculture",
            "farm", "farming", "data", "based", "use", "used", "using", "study", "research",
            "method", "methods", "analysis", "approach", "model", "table", "figure", "fig",
            "page", "journal", "abstract", "keywords", "introduction", "conclusion",
            "references", "copyright", "rights", "reserved", "author", "authors", "et", "al",
            "vol", "issn", "isbn", "doi", "university", "department", "provided", "available",
            "may", "eu", "jsp", "toolkit", "tool", "tools", "cice", "cices", "apply", "applying", 
            "developed", "developing", "provides", "providing", "identify", "identifying", 
            "evaluate", "evaluating", "implement", "implementing", "include", "including", 
            "support", "supporting", "examine", "examining", "establish", "establishing",
            "shall", "should", "must", "can", "could", "will", "would", "also", "many", "much",
            "example", "examples", "one", "two"
        }
        
        words = text.split()
        clean_words = []
        for w in words:
            # Basic lemmatization (remove 's')
            if len(w) > 4 and w.endswith('s') and not w.endswith('ss'):
                w = w[:-1]
            
            if w not in noise and len(w) > 2: # Also filter out short tokens < 3 chars
                clean_words.append(w)
                
        return " ".join(clean_words)

    # Preprocess all texts
    cleaned_texts = [clean_text_ai(doc["extracted_text"]) for doc in docs]
    names = [doc["name"] for doc in docs]

    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    
    # Use TF-IDF with max_df/min_df for automatic noise filtering
    vectorizer = TfidfVectorizer(
        stop_words=list(ENGLISH_STOP_WORDS), 
        max_features=1000,
        max_df=0.85, # Remove words that appear in more than 85% of docs (corpus-wide noise)
        min_df=2     # Only keep words that appear in at least 2 docs
    )
    
    try:
        X = vectorizer.fit_transform(cleaned_texts)
    except ValueError:
        return {"status": "error", "message": "Could not extract vocabulary after advanced cleaning."}
        
    terms = vectorizer.get_feature_names_out()
    
    # --- Dynamic Clustering (Free Clustering) ---
    max_k = min(10, len(cleaned_texts) - 1)
    if max_k < 2:
        num_clusters = 1
    else:
        best_k = 2
        best_score = -1
        for k in range(2, max_k + 1):
            km = KMeans(n_clusters=k, random_state=42, n_init='auto')
            labels = km.fit_predict(X)
            score = silhouette_score(X, labels)
            if score > best_score:
                best_score = score
                best_k = k
        num_clusters = best_k

    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
    kmeans.fit(X)

    # --- Dendrogram Generation ---
    try:
        from scipy.cluster.hierarchy import linkage, dendrogram
        Z = linkage(X.toarray(), 'ward')
        plt.figure(figsize=(12, 8))
        dendrogram(Z, labels=names, leaf_rotation=90)
        plt.title("NLP Document Clustering Dendrogram")
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "nlp_dendrogram.png"))
        plt.close()
    except Exception as e:
        print(f"Dendrogram error: {e}")

    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    
    cluster_list = []
    for i in range(num_clusters):
        top_terms = [terms[ind] for ind in order_centroids[i, :10]] # Get top 10
        cluster_frameworks = [names[j] for j in range(len(names)) if kmeans.labels_[j] == i]
        
        if cluster_frameworks:
            # Generate Word Cloud for this cluster
            try:
                cluster_text = " ".join([cleaned_texts[j] for j in range(len(cleaned_texts)) if kmeans.labels_[j] == i])
                wc = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(cluster_text)
                wc_path = os.path.join(RESULTS_DIR, f"nlp_cluster_{i+1}.png")
                wc.to_file(wc_path)
            except Exception as e:
                print(f"WordCloud error for cluster {i+1}: {e}")

            # AGROVOC Enrichment
            agrovoc_tags = batch_enrich_terms(top_terms[:8])

            cluster_list.append({
                "group": i + 1,
                "theme": ", ".join(top_terms[:5]).title(), # Use top 5 for theme name
                "frameworks": sorted(cluster_frameworks),
                "wordcloud": f"/results/nlp_cluster_{i+1}.png",
                "agrovoc_tags": agrovoc_tags
            })

    cluster_list.sort(key=lambda x: len(x["frameworks"]), reverse=True)
    for idx, c in enumerate(cluster_list):
        c["group"] = idx + 1

    return {
        "status": "success",
        "num_clusters": num_clusters,
        "dendrogram": "/results/nlp_dendrogram.png",
        "framework_clusters": cluster_list
    }

@app.get("/analyse/summary")
def get_summary():
    if principle_matrix is None:
        return {"status": "error", "message": "Matrix not loaded"}
    
    # Use a fixed order for consistency in Radar charts
    PRINCIPLE_ORDER = [
        "Recycling", "Input Reduction", "Soil Health", "Animal Health", 
        "Biodiversity", "Synergy", "Economic Diversification", 
        "Co-creation of Knowledge", "Social Values and Diets", 
        "Fairness", "Connectivity", "Land and Natural Resource Governance", 
        "Participation"
    ]
    
    data_mat = principle_matrix.iloc[:, 1:14].copy()
    # Clean the column names (remove \xa0 and strip)
    data_mat.columns = [str(c).replace('\xa0', ' ').strip() for c in data_mat.columns]
    
    avg_scores = data_mat.mean()
    
    summary = []
    for p in PRINCIPLE_ORDER:
        # Match case-insensitively
        matching_col = next((c for c in avg_scores.index if c.lower() == p.lower()), None)
        if matching_col:
            s = avg_scores[matching_col]
            score = min(1.0, float(s) / 100.0) if pd.notnull(s) else 0.0
            summary.append({"principle": p, "score": score})
        else:
            summary.append({"principle": p, "score": 0.0})
            
    return summary

@app.get("/analyse/agrontology-summary")
def get_agrontology_summary():
    if agrontology_matrix is None:
        return {"status": "error", "message": "Agrontology matrix not loaded"}
    
    principle_cols = [c for c in agrontology_matrix.columns if c.startswith('P_')]
    data_mat = agrontology_matrix[principle_cols]
    avg_scores = data_mat.mean()
    
    def normalize_principle_name(p):
        p = str(p).replace('P_', '').strip()
        mapping = {
            "animal health": "Animal Health",
            "biodiversity": "Biodiversity",
            "co-creation of knowledge": "Co-creation of Knowledge",
            "connectivity": "Connectivity",
            "economic diversification": "Economic Diversification",
            "fairness": "Fairness",
            "input reduction": "Input Reduction",
            "land governance": "Land and Natural Resource Governance",
            "land and natural resource governance": "Land and Natural Resource Governance",
            "participation": "Participation",
            "recycling": "Recycling",
            "social values and diets": "Social Values and Diets",
            "soil health": "Soil Health",
            "synergy": "Synergy"
        }
        return mapping.get(p.lower(), p)

    PRINCIPLE_ORDER = [
        "Recycling", "Input Reduction", "Soil Health", "Animal Health", 
        "Biodiversity", "Synergy", "Economic Diversification", 
        "Co-creation of Knowledge", "Social Values and Diets", 
        "Fairness", "Connectivity", "Land and Natural Resource Governance", 
        "Participation"
    ]
    
    summary = []
    # Maximum value across all principles in agrontology_matrix for normalization
    overall_max = data_mat.max().max() if not data_mat.empty else 1.0
    
    for p in PRINCIPLE_ORDER:
        matching_col = next((c for c in avg_scores.index if normalize_principle_name(c).lower() == p.lower()), None)
        if matching_col:
            s = avg_scores[matching_col]
            # Normalize to overall max for consistent radar scale
            score = min(1.0, float(s) / overall_max) if pd.notnull(s) and overall_max > 0 else 0.0
            summary.append({"principle": p, "score": score})
        else:
            summary.append({"principle": p, "score": 0.0})
            
    return summary

@app.get("/analyse/agrontology-design-summary")
def get_agrontology_design_summary():
    if agrontology_matrix is None:
        return {"status": "error", "message": "Agrontology matrix not loaded"}
    
    # Get the normalized principle scores
    principle_scores = get_agrontology_summary()
    
    design_summary = []
    for dp, relevant_agro in design_mapping.items():
        display_name = dp.split(" (")[1].replace(")", "") if " (" in dp else dp
        scores_subset = [s["score"] for s in principle_scores if s["principle"].lower() in [ra.lower() for ra in relevant_agro]]
        avg_score = sum(scores_subset) / len(scores_subset) if scores_subset else 0.0
        design_summary.append({"principle": display_name, "score": avg_score})
        
    return design_summary

@app.get("/analyse/design-summary")
def get_design_summary():
    if principle_matrix is None:
        return {"status": "error", "message": "Matrix not loaded"}
    
    data_mat = principle_matrix.iloc[:, 1:14].copy()
    data_mat.columns = [str(c).replace('\xa0', ' ').strip() for c in data_mat.columns]
    avg_scores = data_mat.mean()
    
    # Calculate design scores based on the global averages of the 13 principles
    summary_scores = []
    for p, s in avg_scores.items():
        score = min(1.0, float(s) / 100.0) if pd.notnull(s) else 0.0
        summary_scores.append({"principle": p, "score": score})
        
    design_summary = []
    for dp, relevant_agro in design_mapping.items():
        # Handle the names carefully (Diagnostics, Stewardship, etc.)
        display_name = dp.split(" (")[1].replace(")", "") if " (" in dp else dp
        
        scores_subset = [s["score"] for s in summary_scores if s["principle"].lower() in [ra.lower() for ra in relevant_agro]]
        avg_score = sum(scores_subset) / len(scores_subset) if scores_subset else 0.0
        design_summary.append({"principle": display_name, "score": avg_score})
        
    return design_summary

@app.get("/analyse/generate-figures")
def generate_figures():
    try:
        scripts = [
            "generate_figure2.py",
            "generate_figure3.py",
            "generate_figure4.py"
        ]
        results = []
        for script in scripts:
            script_path = os.path.join(BASE_PATH, "api", "analysis", script)
            process = subprocess.run(["python", script_path], capture_output=True, text=True)
            if process.returncode != 0:
                results.append({"script": script, "status": "error", "message": process.stderr})
            else:
                results.append({"script": script, "status": "success", "message": process.stdout})
        
        return {
            "status": "success",
            "results": results,
            "images": [
                "/results/figure2a_orientation.png",
                "/results/figure2b_evolution.png",
                "/results/figure3_heatmap.png",
                "/results/figure4_programming_cycle.png"
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/db/status")
def db_status():
    try:
        fw_count = execute_query("SELECT COUNT(*) as n FROM frameworks")[0]["n"]
        doc_count = execute_query("SELECT COUNT(*) as n FROM documents")[0]["n"]
        processed = execute_query("SELECT COUNT(*) as n FROM documents WHERE status = 'processed'")[0]["n"]
        errors = execute_query("SELECT COUNT(*) as n FROM documents WHERE status = 'error'")[0]["n"]
        missing = execute_query("SELECT COUNT(*) as n FROM documents WHERE status = 'missing'")[0]["n"]
        ok = True
    except Exception:
        ok = False
        
    return {
        "connected": ok,
        "database": "SQLite",
        "path": "db/soil_health.sqlite",
        "frameworks": fw_count if ok else 0,
        "documents": {
            "total": doc_count if ok else 0,
            "processed": processed if ok else 0,
            "errors": errors if ok else 0,
            "missing": missing if ok else 0
        }
    }

@app.post("/db/refresh")
def refresh_db():
    try:
        added, processed = link_pdfs_logic()
        return {
            "status": "success", 
            "message": f"Sync complete. Added {added} frameworks, processed {processed} documents.",
            "added": added,
            "processed": processed
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/documents/search")
def search_documents(q: str = Query("")):
    if len(q) < 2:
        return {"status": "error", "message": "Query must be at least 2 characters"}
        
    results = execute_query(
        """SELECT d.id, d.filename, d.status, f.name, f.title, f.author_date
           FROM documents d
           LEFT JOIN frameworks f ON d.framework_id = f.id
           WHERE d.extracted_text LIKE ? OR f.name LIKE ? OR f.title LIKE ?""",
        (f"%{q}%", f"%{q}%", f"%{q}%")
    )
    return {"status": "success", "count": len(results), "results": results}

@app.get("/documents/stats")
def documents_stats():
    stats = execute_query(
        """SELECT 
             d.id, d.filename, d.status, d.processed_at,
             LENGTH(d.extracted_text) as text_length,
             f.name as framework_name, f.author_date
           FROM documents d
           LEFT JOIN frameworks f ON d.framework_id = f.id
           ORDER BY f.name"""
    )
    return stats

@app.get("/metadata/indicators-hierarchy")
def get_indicators_hierarchy():
    # Provide the authoritative HLPE principles and their corresponding indicator terms (synonyms)
    OPERATIONAL_CATEGORIES = {
        "Improving Resource Efficiency": ["Recycling", "Input reduction"],
        "Strengthening Resilience": ["Soil health", "Animal health", "Biodiversity", "Synergy", "Economic diversification"],
        "Securing Social Equity/Responsibility": ["Co-creation of knowledge", "Social values and diets", "Fairness", "Connectivity", "Land and natural resource governance", "Participation"]
    }
    
    SYNONYMS_MAPPING = {
        "Recycling": ["recycling", "nutrient cycling", "cycles", "cycling", "recovery", "biomass", "organic", "waste", "wastewater", "greywater", "reuse", "water", "reclamation", "rainwater", "harvesting", "reusable", "recyclable"],
        "Input reduction": ["reduction", "preventative", "preventive", "practices", "nitrogen fixing", "nitrogen fixation", "leguminous", "biological", "natural control", "conservation", "storage", "retention", "efficient", "efficiency", "renewable", "generate", "sustainable", "farm-saved"],
        "Soil health": ["soil", "health", "microbial", "manure", "vermicomposting", "worm", "composting", "permaculture", "permanent", "organic farming", "mulching", "soil cover", "organic matter", "soil amendment", "cover crops", "biochar", "crop residues"],
        "Animal health": ["animal health", "resilient breed", "indigenous breed", "carrying capacity", "alignment", "matching", "resource", "balance"],
        "Biodiversity": ["biodiversity", "diversity", "crop diversity", "species", "pollinators", "pollinating", "insects", "pest", "natural preditors", "rotation", "forest", "woodland"],
        "Synergy": ["synergy", "agroecological", "agroecology", "redesign", "ecological", "diversification", "biodiversity", "variety", "planting", "intercropping", "mixed", "cropping", "integrated", "holistic", "circular", "habitat", "ecosystem", "stewardship", "landscape"],
        "Economic diversification": ["economic", "economic diversification", "value chains"],
        "Co-creation of knowledge": ["co-creation", "knowledge", "farmer-to-farmer", "learning", "peer", "information", "sharing", "transfer", "traditional", "indigenous knowledge", "dissemination", "wisdom"],
        "Social values and diets": ["social", "diets", "cultural foods", "indigenous crops", "heritage", "uniqueness", "tradition", "customs", "culturally", "traditional", "relevant", "healthy", "nutritious", "balanced diet"],
        "Fairness": ["fairness", "fair trade", "equitable", "power", "relations", "network", "just", "fair price", "market", "decent jobs", "respectable", "quality", "working conditions", "labor", "employment", "protection", "preservation", "safeguarding", "intellectual", "property rights", "rights", "laws"],
        "Connectivity": ["consumers and producers", "food chain", "procurement", "cooperatives", "organisations", "community group", "connections", "proximity", "local market", "short food chain", "direct marketing"],
        "Land and natural resource governance": ["land", "tenure", "access", "governance", "natural resources", "rights", "commons", "customary rights", "land security", "resource access"],
        "Participation": ["equitable", "ownership", "inclusive", "participation", "broad", "diverse", "marginalized", "groups", "underrepresented", "decision-making", "policy-making", "governance", "community-based", "participatory"]
    }
    hierarchy = {
        "categories": OPERATIONAL_CATEGORIES,
        "mapping": SYNONYMS_MAPPING
    }
    
    return hierarchy

@app.get("/metadata/ontology-mapping-snapshot")
def get_ontology_mapping_snapshot():
    # Return a sample of the pre-computed mappings
    p_map = load_principles_map()
    
    # Take a sample (e.g., 50 items) or group by principle for display
    snapshot = {}
    for uri, data in p_map.items():
        principles = data.get("principles", [])
        label = data.get("prefLabel", "")
        for p in principles:
            if p not in snapshot:
                snapshot[p] = []
            if len(snapshot[p]) < 10: # Limit to 10 per principle for snapshot
                snapshot[p].append({"label": label, "uri": uri})
                
    return snapshot

@app.post("/suggestions")
def submit_suggestion(sub: SuggestionSubmission):
    execute_statement(
        """INSERT INTO suggestions (type, action, target_name, parent_target, evidence_url, contact_details)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (sub.type, sub.action, sub.target_name, sub.parent_target, sub.evidence_url, sub.contact_details)
    )
    return {"status": "success"}

@app.get("/suggestions")
def list_suggestions():
    suggestions = execute_query("SELECT * FROM suggestions ORDER BY created_at DESC")
    return suggestions

@app.get("/portfolio/profile")
def get_portfolio_profile():
    path = os.path.join(BASE_PATH, "api", "data", "portfolio_data.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["profile"]
    return {"status": "error", "message": "Portfolio data not found"}

@app.get("/portfolio/publications")
def get_portfolio_publications():
    path = os.path.join(BASE_PATH, "api", "data", "portfolio_data.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["publications"]
    return []

@app.get("/portfolio/stats")
def get_portfolio_stats():
    path = os.path.join(BASE_PATH, "api", "data", "portfolio_data.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Calculate pubs per year
        years = [p["year"] for p in data["publications"]]
        unique_years = sorted(list(set(years)))
        pubs_per_year = [{"year": y, "count": years.count(y)} for y in unique_years]
        
        return {
            "metrics": data["metrics"],
            "pubs_per_year": pubs_per_year
        }
    return {"status": "error", "message": "Portfolio data not found"}

@app.patch("/suggestions/{suggestion_id}")
def update_suggestion(suggestion_id: int, action: SuggestionAction):
    execute_statement(
        "UPDATE suggestions SET status = ?, dev_response = ?, updated_at = datetime('now') WHERE id = ?",
        (action.status, action.dev_response, suggestion_id)
    )
    return {"status": "success"}
@app.get("/ontology/master")
def get_master_ontology():
    if os.path.exists(MASTER_ONTOLOGY_PATH):
        try:
            with open(MASTER_ONTOLOGY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading master ontology: {e}")
    raise HTTPException(status_code=404, detail="Master ontology file not found")
