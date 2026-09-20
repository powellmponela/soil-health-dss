import json
import math
import os
import re
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from db_utils import execute_query, get_db_connection


router = APIRouter(prefix="/analytics/thematic", tags=["tailored thematic analysis"])

BASE_PATH = os.path.join(os.path.dirname(__file__), "..")
RESULTS_DIR = os.path.join(BASE_PATH, "api", "results", "tailored")
os.makedirs(RESULTS_DIR, exist_ok=True)


class TailoredPrincipleInput(BaseModel):
    name: str
    objective: Optional[str] = ""
    indicators: List[str] = []


class TailoredDocumentInput(BaseModel):
    name: str
    citation: Optional[str] = ""
    source_url: Optional[str] = ""
    extracted_text: str


class TailoredStudyCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    stakeholder: Optional[str] = ""
    principles: List[TailoredPrincipleInput]
    framework_ids: List[int] = []
    custom_frameworks: List[TailoredDocumentInput] = []


def _study_or_404(study_id: int) -> Dict[str, Any]:
    rows = execute_query("SELECT * FROM thematic_studies WHERE id = ?", (study_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Tailored thematic study not found")
    return rows[0]


def _clean_indicator_terms(terms: List[str]) -> List[str]:
    seen = set()
    cleaned = []
    for term in terms:
        value = re.sub(r"\s+", " ", str(term or "")).strip()
        key = value.lower()
        if value and key not in seen:
            cleaned.append(value)
            seen.add(key)
    return cleaned


def _contexts_for_term(text: str, pattern: re.Pattern, limit: int = 5, window: int = 90) -> List[str]:
    contexts = []
    for match in pattern.finditer(text):
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        snippet = re.sub(r"\s+", " ", text[start:end]).strip()
        contexts.append(snippet)
        if len(contexts) >= limit:
            break
    return contexts


def _term_pattern(term: str) -> re.Pattern:
    parts = [re.escape(part) for part in re.split(r"\s+", term.strip()) if part]
    phrase = r"\s+".join(parts)
    return re.compile(rf"(?<!\w){phrase}(?!\w)", re.IGNORECASE)


def _tokenize_for_words(text: str) -> List[str]:
    tokens = re.findall(r"\b[a-z][a-z-]{2,}\b", (text or "").lower())
    noise = set(ENGLISH_STOP_WORDS).union({
        "soil", "health", "framework", "frameworks", "indicator", "indicators",
        "principle", "principles", "study", "studies", "analysis", "method",
        "methods", "table", "figure", "published", "document", "documents"
    })
    return [token for token in tokens if token not in noise]


def _get_principles(study_id: int) -> List[Dict[str, Any]]:
    rows = execute_query(
        """SELECT p.id, p.name, p.objective, p.sort_order, i.id AS indicator_id, i.term
           FROM thematic_principles p
           LEFT JOIN thematic_indicators i ON i.principle_id = p.id
           WHERE p.study_id = ?
           ORDER BY p.sort_order, p.id, i.term""",
        (study_id,)
    )
    by_id: Dict[int, Dict[str, Any]] = {}
    for row in rows:
        pid = row["id"]
        if pid not in by_id:
            by_id[pid] = {
                "id": pid,
                "name": row["name"],
                "objective": row.get("objective") or "",
                "sort_order": row.get("sort_order") or 0,
                "indicators": []
            }
        if row.get("indicator_id"):
            by_id[pid]["indicators"].append({
                "id": row["indicator_id"],
                "term": row["term"]
            })
    return list(by_id.values())


def _get_sources(study_id: int) -> List[Dict[str, Any]]:
    mponela_sources = execute_query(
        """SELECT
             'mponela:' || f.id AS source_key,
             f.id AS framework_id,
             f.name AS source_name,
             f.title,
             f.author_date,
             f.filename,
             COALESCE(d.extracted_text, '') AS extracted_text,
             COALESCE(d.status, 'missing') AS status,
             'mponela' AS origin
           FROM thematic_study_frameworks tsf
           JOIN frameworks f ON f.id = tsf.framework_id
           LEFT JOIN documents d ON d.framework_id = f.id
           WHERE tsf.study_id = ?
           ORDER BY f.name""",
        (study_id,)
    )
    custom_sources = execute_query(
        """SELECT
             'custom:' || id AS source_key,
             NULL AS framework_id,
             name AS source_name,
             citation AS title,
             citation AS author_date,
             source_url AS filename,
             extracted_text,
             'processed' AS status,
             'stakeholder' AS origin
           FROM thematic_documents
           WHERE study_id = ?
           ORDER BY name""",
        (study_id,)
    )
    return mponela_sources + custom_sources


def _json_list(value: Optional[str]) -> List[Any]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def _build_summary(study_id: int) -> Dict[str, Any]:
    rows = execute_query(
        """SELECT e.source_key, e.source_name, e.term, e.match_count,
                  p.id AS principle_id, p.name AS principle_name
           FROM thematic_word_extractions e
           JOIN thematic_principles p ON p.id = e.principle_id
           WHERE e.study_id = ?""",
        (study_id,)
    )

    total_matches = int(sum(row["match_count"] or 0 for row in rows))
    total_sources = len({row["source_key"] for row in rows})
    principles: Dict[int, Dict[str, Any]] = {}

    for row in rows:
        pid = row["principle_id"]
        if pid not in principles:
            principles[pid] = {
                "principle": row["principle_name"],
                "total_matches": 0,
                "sources": set(),
                "terms": Counter()
            }
        count = int(row["match_count"] or 0)
        principles[pid]["total_matches"] += count
        principles[pid]["sources"].add(row["source_key"])
        principles[pid]["terms"][row["term"]] += count

    principle_summary = []
    for value in principles.values():
        source_count = len(value["sources"])
        principle_summary.append({
            "principle": value["principle"],
            "total_matches": value["total_matches"],
            "sources": source_count,
            "coverage": round(source_count / total_sources, 3) if total_sources else 0,
            "top_terms": [
                {"term": term, "count": int(count)}
                for term, count in value["terms"].most_common(10)
            ]
        })
    principle_summary.sort(key=lambda item: item["total_matches"], reverse=True)

    source_counts = Counter()
    for row in rows:
        source_counts[row["source_name"]] += int(row["match_count"] or 0)

    return {
        "total_matches": total_matches,
        "matched_sources": total_sources,
        "principles": principle_summary,
        "top_sources": [
            {"source": source, "count": int(count)}
            for source, count in source_counts.most_common(10)
        ]
    }


def _build_clusters(study_id: int) -> List[Dict[str, Any]]:
    rows = execute_query(
        """SELECT cluster_group, theme, source_keys, source_names, top_terms, size
           FROM thematic_clusters
           WHERE study_id = ?
           ORDER BY cluster_group""",
        (study_id,)
    )
    clusters = []
    for row in rows:
        clusters.append({
            "group": row["cluster_group"],
            "theme": row["theme"],
            "source_keys": _json_list(row.get("source_keys")),
            "source_names": _json_list(row.get("source_names")),
            "top_terms": _json_list(row.get("top_terms")),
            "size": row["size"]
        })
    return clusters


def _matrix_from_extractions(study_id: int) -> pd.DataFrame:
    sources = _get_sources(study_id)
    principles = _get_principles(study_id)
    if not sources or not principles:
        return pd.DataFrame()

    source_names = {source["source_key"]: source["source_name"] for source in sources}
    principle_names = {principle["id"]: principle["name"] for principle in principles}
    matrix = pd.DataFrame(
        0.0,
        index=[source["source_key"] for source in sources],
        columns=[principle["name"] for principle in principles]
    )
    matrix.insert(0, "source_name", [source["source_name"] for source in sources])

    rows = execute_query(
        """SELECT source_key, principle_id, SUM(match_count) AS total
           FROM thematic_word_extractions
           WHERE study_id = ?
           GROUP BY source_key, principle_id""",
        (study_id,)
    )
    for row in rows:
        source_key = row["source_key"]
        principle_name = principle_names.get(row["principle_id"])
        if source_key in matrix.index and principle_name in matrix.columns:
            matrix.loc[source_key, principle_name] = float(row["total"] or 0)

    matrix.index.name = "source_key"
    matrix["source_name"] = matrix.index.map(source_names)
    return matrix


@router.get("/framework-options")
def framework_options():
    rows = execute_query(
        """SELECT f.id, f.name, f.title, f.author_date, f.publisher, f.filename,
                  f.objective, COALESCE(d.status, 'missing') AS document_status,
                  LENGTH(COALESCE(d.extracted_text, '')) AS text_length
           FROM frameworks f
           LEFT JOIN documents d ON d.framework_id = f.id
           ORDER BY f.name"""
    )
    return {
        "status": "success",
        "source": "Mponela published framework database",
        "frameworks": rows
    }


@router.get("/studies")
def list_studies():
    studies = execute_query(
        """SELECT s.*,
                  COUNT(DISTINCT tsf.framework_id) AS mponela_frameworks,
                  COUNT(DISTINCT td.id) AS custom_frameworks,
                  COUNT(DISTINCT p.id) AS principles,
                  COUNT(DISTINCT e.id) AS extraction_rows,
                  COUNT(DISTINCT c.id) AS clusters
           FROM thematic_studies s
           LEFT JOIN thematic_study_frameworks tsf ON tsf.study_id = s.id
           LEFT JOIN thematic_documents td ON td.study_id = s.id
           LEFT JOIN thematic_principles p ON p.study_id = s.id
           LEFT JOIN thematic_word_extractions e ON e.study_id = s.id
           LEFT JOIN thematic_clusters c ON c.study_id = s.id
           GROUP BY s.id
           ORDER BY s.updated_at DESC, s.created_at DESC"""
    )
    return {"status": "success", "studies": studies}


@router.post("/studies")
def create_study(payload: TailoredStudyCreate):
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Study title is required")

    principles = [
        principle for principle in payload.principles
        if principle.name.strip()
    ]
    if not principles:
        raise HTTPException(status_code=400, detail="At least one principle objective is required")

    indicator_count = sum(
        len(_clean_indicator_terms(principle.indicators))
        for principle in principles
    )
    if indicator_count == 0:
        raise HTTPException(status_code=400, detail="Load at least one indicator term before extraction")

    custom_docs = [
        doc for doc in payload.custom_frameworks
        if doc.name.strip() and doc.extracted_text.strip()
    ]
    framework_ids = sorted({int(fid) for fid in payload.framework_ids if int(fid) > 0})
    if not framework_ids and not custom_docs:
        raise HTTPException(status_code=400, detail="Select a Mponela framework or add a stakeholder document")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO thematic_studies (title, description, stakeholder, status)
               VALUES (?, ?, ?, ?)""",
            (title, payload.description or "", payload.stakeholder or "", "configured")
        )
        study_id = cursor.lastrowid

        for framework_id in framework_ids:
            cursor.execute(
                """INSERT OR IGNORE INTO thematic_study_frameworks (study_id, framework_id, origin)
                   VALUES (?, ?, ?)""",
                (study_id, framework_id, "mponela")
            )

        for doc in custom_docs:
            cursor.execute(
                """INSERT INTO thematic_documents
                     (study_id, name, citation, source_url, extracted_text)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    study_id,
                    doc.name.strip(),
                    doc.citation or "",
                    doc.source_url or "",
                    doc.extracted_text.strip()
                )
            )

        for idx, principle in enumerate(principles):
            cursor.execute(
                """INSERT INTO thematic_principles (study_id, name, objective, sort_order)
                   VALUES (?, ?, ?, ?)""",
                (study_id, principle.name.strip(), principle.objective or "", idx)
            )
            principle_id = cursor.lastrowid
            for term in _clean_indicator_terms(principle.indicators):
                cursor.execute(
                    "INSERT INTO thematic_indicators (principle_id, term) VALUES (?, ?)",
                    (principle_id, term)
                )

        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating tailored study: {exc}")
    finally:
        conn.close()

    return get_study(study_id)


@router.get("/studies/{study_id}")
def get_study(study_id: int):
    study = _study_or_404(study_id)
    return {
        "status": "success",
        "study": study,
        "frameworks": _get_sources(study_id),
        "principles": _get_principles(study_id),
        "summary": _build_summary(study_id),
        "clusters": _build_clusters(study_id)
    }


@router.post("/studies/{study_id}/extract")
def extract_words(study_id: int):
    study = _study_or_404(study_id)
    sources = _get_sources(study_id)
    principles = _get_principles(study_id)
    if not sources:
        raise HTTPException(status_code=400, detail="No frameworks are linked to this tailored study")
    if not principles:
        raise HTTPException(status_code=400, detail="No principle objectives are configured for this tailored study")

    extraction_rows = []
    skipped_sources = []

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM thematic_word_extractions WHERE study_id = ?", (study_id,))
        cursor.execute("DELETE FROM thematic_clusters WHERE study_id = ?", (study_id,))

        for source in sources:
            text = source.get("extracted_text") or ""
            if not text.strip():
                skipped_sources.append({
                    "source_key": source["source_key"],
                    "source_name": source["source_name"],
                    "reason": source.get("status") or "no text"
                })
                continue

            for principle in principles:
                for indicator in principle["indicators"]:
                    term = indicator["term"]
                    pattern = _term_pattern(term)
                    matches = list(pattern.finditer(text))
                    if not matches:
                        continue
                    contexts = _contexts_for_term(text, pattern)
                    count = len(matches)
                    cursor.execute(
                        """INSERT INTO thematic_word_extractions
                             (study_id, source_key, source_name, principle_id, indicator_id, term, match_count, contexts)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            study_id,
                            source["source_key"],
                            source["source_name"],
                            principle["id"],
                            indicator["id"],
                            term,
                            count,
                            json.dumps(contexts)
                        )
                    )
                    extraction_rows.append({
                        "source_key": source["source_key"],
                        "source_name": source["source_name"],
                        "origin": source["origin"],
                        "principle": principle["name"],
                        "term": term,
                        "count": count,
                        "contexts": contexts
                    })

        cursor.execute(
            "UPDATE thematic_studies SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            ("extracted", study_id)
        )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error extracting tailored words: {exc}")
    finally:
        conn.close()

    extraction_path = os.path.join(RESULTS_DIR, f"tailored_study_{study_id}_extractions.csv")
    pd.DataFrame(extraction_rows).to_csv(extraction_path, index=False)

    matrix = _matrix_from_extractions(study_id)
    matrix_path = os.path.join(RESULTS_DIR, f"tailored_study_{study_id}_matrix.csv")
    if not matrix.empty:
        matrix.reset_index().to_csv(matrix_path, index=False)

    return {
        "status": "success",
        "study": study,
        "rows": len(extraction_rows),
        "skipped_sources": skipped_sources,
        "summary": _build_summary(study_id),
        "files": {
            "extractions": f"/results/tailored/tailored_study_{study_id}_extractions.csv",
            "matrix": f"/results/tailored/tailored_study_{study_id}_matrix.csv"
        }
    }


@router.post("/studies/{study_id}/cluster")
def cluster_study(study_id: int):
    _study_or_404(study_id)
    matrix = _matrix_from_extractions(study_id)
    if matrix.empty:
        raise HTTPException(status_code=400, detail="Run extraction before clustering this tailored study")

    feature_cols = [col for col in matrix.columns if col != "source_name"]
    feature_matrix = matrix[feature_cols].astype(float)
    if float(feature_matrix.values.sum()) == 0:
        raise HTTPException(status_code=400, detail="No extracted indicator matches are available for clustering")

    source_keys = matrix.index.tolist()
    source_names = matrix["source_name"].tolist()
    values = feature_matrix.values
    means = values.mean(axis=0)
    stds = values.std(axis=0)
    stds[stds == 0] = 1
    scaled = (values - means) / stds
    scaled = np.nan_to_num(scaled)

    if len(source_keys) == 1:
        labels = np.array([1])
    else:
        distances = pdist(scaled, metric="euclidean")
        if np.allclose(distances, 0):
            labels = np.ones(len(source_keys), dtype=int)
        else:
            hierarchy = linkage(distances, method="complete")
            target_clusters = min(4, len(source_keys))
            labels = fcluster(hierarchy, target_clusters, criterion="maxclust")

    extraction_rows = execute_query(
        """SELECT source_key, term, match_count, p.name AS principle_name
           FROM thematic_word_extractions e
           JOIN thematic_principles p ON p.id = e.principle_id
           WHERE e.study_id = ?""",
        (study_id,)
    )

    rows_by_source = defaultdict(list)
    for row in extraction_rows:
        rows_by_source[row["source_key"]].append(row)

    clusters = []
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM thematic_clusters WHERE study_id = ?", (study_id,))

        for cluster_id in sorted(set(int(label) for label in labels)):
            member_indices = [idx for idx, label in enumerate(labels) if int(label) == cluster_id]
            member_keys = [source_keys[idx] for idx in member_indices]
            member_names = [source_names[idx] for idx in member_indices]

            term_counts = Counter()
            principle_counts = Counter()
            for source_key in member_keys:
                for row in rows_by_source.get(source_key, []):
                    count = int(row["match_count"] or 0)
                    term_counts[row["term"]] += count
                    principle_counts[row["principle_name"]] += count

            top_terms = [
                {"term": term, "count": int(count)}
                for term, count in term_counts.most_common(8)
            ]
            top_principles = [name for name, _ in principle_counts.most_common(2)]
            theme = ", ".join(top_principles) if top_principles else f"Cluster {cluster_id}"
            if top_terms:
                theme = f"{theme}: {', '.join(item['term'] for item in top_terms[:3])}"

            cursor.execute(
                """INSERT INTO thematic_clusters
                     (study_id, cluster_group, theme, source_keys, source_names, top_terms, size)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    study_id,
                    cluster_id,
                    theme,
                    json.dumps(member_keys),
                    json.dumps(member_names),
                    json.dumps(top_terms),
                    len(member_keys)
                )
            )
            clusters.append({
                "group": cluster_id,
                "theme": theme,
                "source_keys": member_keys,
                "source_names": member_names,
                "top_terms": top_terms,
                "size": len(member_keys)
            })

        cursor.execute(
            "UPDATE thematic_studies SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            ("clustered", study_id)
        )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error clustering tailored study: {exc}")
    finally:
        conn.close()

    heatmap_path = None
    try:
        import matplotlib.pyplot as plt

        width = max(7, len(feature_cols) * 0.7)
        height = max(4, len(source_names) * 0.35)
        fig, ax = plt.subplots(figsize=(width, height))
        image = ax.imshow(feature_matrix.values, aspect="auto", cmap="YlGnBu")
        ax.set_xticks(range(len(feature_cols)))
        ax.set_xticklabels(feature_cols, rotation=45, ha="right")
        ax.set_yticks(range(len(source_names)))
        ax.set_yticklabels(source_names)
        ax.set_title("Tailored Thematic Indicator Matches")
        fig.colorbar(image, ax=ax, fraction=0.026, pad=0.02)
        plt.tight_layout()
        heatmap_file = f"tailored_study_{study_id}_heatmap.png"
        plt.savefig(os.path.join(RESULTS_DIR, heatmap_file), dpi=180, bbox_inches="tight")
        plt.close(fig)
        heatmap_path = f"/results/tailored/{heatmap_file}"
    except Exception:
        heatmap_path = None

    matrix.reset_index().to_csv(
        os.path.join(RESULTS_DIR, f"tailored_study_{study_id}_matrix.csv"),
        index=False
    )

    return {
        "status": "success",
        "clusters": clusters,
        "summary": _build_summary(study_id),
        "files": {
            "matrix": f"/results/tailored/tailored_study_{study_id}_matrix.csv",
            "heatmap": heatmap_path
        }
    }
