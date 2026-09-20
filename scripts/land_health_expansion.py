#!/usr/bin/env python3
"""Land Health expansion routine for the Soil Health DSS.

This routine is intentionally separate from the publication-faithful
Mponela et al. (2026) workflow. It does not change or overwrite the
publication extraction, principle matrices, clustering outputs, or figures.

It scans framework PDFs against configurable Land Health evidence domains,
retains page-level term/context evidence, aggregates transparent coverage
statistics, and optionally appends a *separate* crosswalk to the published
13-principle matrix. The crosswalk is reported as provenance only and is not
combined with keyword coverage into a synthetic Land Health index.

Outputs
-------
api/results/land_health/land_health_term_evidence.csv
api/results/land_health/land_health_domain_profile.csv
api/results/land_health/land_health_summary.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_DIR = ROOT / "Frameworks"
CONFIG_PATH = ROOT / "data" / "land_health_domains.json"
PUBLICATION_MATRIX_PATH = ROOT / "principles_indicators" / "principle_matrix.xlsx"
OUTPUT_DIR = ROOT / "api" / "results" / "land_health"

EVIDENCE_PATH = OUTPUT_DIR / "land_health_term_evidence.csv"
PROFILE_PATH = OUTPUT_DIR / "land_health_domain_profile.csv"
SUMMARY_PATH = OUTPUT_DIR / "land_health_summary.json"


def normalize_label(value: object) -> str:
    value = str(value).replace("\xa0", " ").replace("P_", " ")
    value = re.sub(r"\s+", " ", value).strip().lower()
    mapping = {
        "land governance": "land and natural resource governance",
        "land and nr governance": "land and natural resource governance",
    }
    return mapping.get(value, value)


def phrase_pattern(term: str) -> re.Pattern:
    words = [re.escape(w) for w in re.split(r"\s+", term.strip()) if w]
    expr = r"\s+".join(words)
    return re.compile(rf"(?<!\w){expr}(?!\w)", flags=re.IGNORECASE)


def context_snippet(text: str, start: int, end: int, radius: int = 180) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    snippet = re.sub(r"\s+", " ", text[left:right]).strip()
    return snippet


def load_config(path: Path = CONFIG_PATH) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    if not config.get("domains"):
        raise ValueError(f"No Land Health domains found in {path}")
    return config


def iter_frameworks(folder: Path, framework_filter: str | None = None) -> Iterable[Path]:
    files = sorted(folder.glob("*.pdf"))
    if framework_filter:
        key = framework_filter.lower().strip()
        files = [path for path in files if key in path.name.lower()]
    return files


def scan_pdf(pdf_path: Path, domains: List[dict], max_contexts_per_term_page: int = 5) -> Tuple[List[dict], Dict[str, dict]]:
    records: List[dict] = []
    aggregates: Dict[str, dict] = defaultdict(
        lambda: {
            "total_matches": 0,
            "terms": set(),
            "pages": set(),
        }
    )

    compiled = {
        domain["id"]: [(term, phrase_pattern(term)) for term in domain.get("terms", [])]
        for domain in domains
    }

    reader = PdfReader(str(pdf_path))
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if not text.strip():
            continue

        for domain in domains:
            domain_id = domain["id"]
            page_term_contexts: Dict[str, int] = defaultdict(int)

            for term, pattern in compiled[domain_id]:
                matches = list(pattern.finditer(text))
                if not matches:
                    continue

                agg = aggregates[domain_id]
                agg["total_matches"] += len(matches)
                agg["terms"].add(term)
                agg["pages"].add(page_number)

                for match in matches:
                    if page_term_contexts[term] >= max_contexts_per_term_page:
                        continue
                    records.append(
                        {
                            "framework": pdf_path.name,
                            "page": page_number,
                            "domain_id": domain_id,
                            "domain": domain["label"],
                            "term": term,
                            "context": context_snippet(text, match.start(), match.end()),
                        }
                    )
                    page_term_contexts[term] += 1

    return records, aggregates


def load_publication_crosswalk(domains: List[dict]) -> pd.DataFrame:
    """Read the published matrix without modifying it.

    The returned values are domain-level means of the available published
    principles. They remain separate provenance fields and are never blended
    with Land Health keyword coverage.
    """
    if not PUBLICATION_MATRIX_PATH.exists():
        return pd.DataFrame()

    matrix = pd.read_excel(PUBLICATION_MATRIX_PATH)
    if matrix.empty:
        return pd.DataFrame()

    first_col = matrix.columns[0]
    matrix = matrix.rename(columns={first_col: "pdf_name"})
    normalized_cols = {normalize_label(col): col for col in matrix.columns[1:]}

    out = pd.DataFrame({"framework": matrix["pdf_name"].astype(str)})
    for domain in domains:
        matched_cols = []
        for principle in domain.get("mponela_principles", []):
            col = normalized_cols.get(normalize_label(principle))
            if col is not None:
                matched_cols.append(col)

        if matched_cols:
            numeric = matrix[matched_cols].apply(pd.to_numeric, errors="coerce")
            out[f"{domain['id']}__publication_mean"] = numeric.mean(axis=1)
            out[f"{domain['id']}__publication_n_principles"] = numeric.notna().sum(axis=1)
        else:
            out[f"{domain['id']}__publication_mean"] = pd.NA
            out[f"{domain['id']}__publication_n_principles"] = 0

    out["framework_key"] = (
        out["framework"].str.lower().str.strip().str.replace(".pdf", "", regex=False)
    )
    return out


def build_profiles(frameworks: List[Path], domains: List[dict], all_aggregates: Dict[str, Dict[str, dict]]) -> pd.DataFrame:
    rows = []
    for pdf_path in frameworks:
        framework_agg = all_aggregates.get(pdf_path.name, {})
        for domain in domains:
            stats = framework_agg.get(
                domain["id"], {"total_matches": 0, "terms": set(), "pages": set()}
            )
            configured_terms = len(domain.get("terms", []))
            unique_terms = len(stats["terms"])
            rows.append(
                {
                    "framework": pdf_path.name,
                    "domain_id": domain["id"],
                    "domain": domain["label"],
                    "total_matches": int(stats["total_matches"]),
                    "unique_terms": int(unique_terms),
                    "pages_with_matches": int(len(stats["pages"])),
                    "configured_terms": int(configured_terms),
                    "term_coverage": round(unique_terms / configured_terms, 4)
                    if configured_terms
                    else 0.0,
                }
            )
    return pd.DataFrame(rows)


def add_publication_provenance(profile: pd.DataFrame, publication: pd.DataFrame) -> pd.DataFrame:
    if profile.empty or publication.empty:
        profile["publication_principle_mean"] = pd.NA
        profile["publication_principles_available"] = 0
        return profile

    publication = publication.copy()
    lookup = publication.set_index("framework_key")
    means = []
    counts = []

    for _, row in profile.iterrows():
        key = str(row["framework"]).lower().strip().replace(".pdf", "")
        domain_id = row["domain_id"]
        if key in lookup.index:
            item = lookup.loc[key]
            if isinstance(item, pd.DataFrame):
                item = item.iloc[0]
            means.append(item.get(f"{domain_id}__publication_mean", pd.NA))
            counts.append(item.get(f"{domain_id}__publication_n_principles", 0))
        else:
            means.append(pd.NA)
            counts.append(0)

    profile["publication_principle_mean"] = means
    profile["publication_principles_available"] = counts
    return profile


def summarize(profile: pd.DataFrame, domains: List[dict], framework_count: int) -> dict:
    domain_summary = []
    for domain in domains:
        subset = profile[profile["domain_id"] == domain["id"]]
        frameworks_with_matches = int((subset["total_matches"] > 0).sum()) if not subset.empty else 0
        domain_summary.append(
            {
                "id": domain["id"],
                "label": domain["label"],
                "description": domain.get("description", ""),
                "frameworks_with_matches": frameworks_with_matches,
                "framework_coverage": round(frameworks_with_matches / framework_count, 4)
                if framework_count
                else 0.0,
                "total_matches": int(subset["total_matches"].sum()) if not subset.empty else 0,
                "mean_term_coverage": round(float(subset["term_coverage"].mean()), 4)
                if not subset.empty
                else 0.0,
                "mponela_principles": domain.get("mponela_principles", []),
            }
        )

    return {
        "status": "success",
        "routine": "Land Health expansion",
        "version": "1.0",
        "publication_baseline": "Mponela et al. (2026) retained unchanged",
        "scope_note": (
            "Land Health results are an extension. Keyword evidence and publication "
            "crosswalk values are reported separately and are not combined into a "
            "synthetic index."
        ),
        "frameworks_scanned": framework_count,
        "domains": domain_summary,
        "outputs": {
            "term_evidence": str(EVIDENCE_PATH.relative_to(ROOT)).replace("\\", "/"),
            "domain_profile": str(PROFILE_PATH.relative_to(ROOT)).replace("\\", "/"),
            "summary": str(SUMMARY_PATH.relative_to(ROOT)).replace("\\", "/"),
        },
    }


def run(framework_filter: str | None = None) -> dict:
    config = load_config()
    domains = config["domains"]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    frameworks = list(iter_frameworks(FRAMEWORK_DIR, framework_filter))
    all_records: List[dict] = []
    all_aggregates: Dict[str, Dict[str, dict]] = {}

    for pdf_path in frameworks:
        try:
            records, aggregates = scan_pdf(pdf_path, domains)
            all_records.extend(records)
            all_aggregates[pdf_path.name] = aggregates
            print(f"[land-health] scanned {pdf_path.name}: {len(records)} evidence records")
        except Exception as exc:
            print(f"[land-health] ERROR {pdf_path.name}: {exc}")
            all_aggregates[pdf_path.name] = {}

    evidence_columns = ["framework", "page", "domain_id", "domain", "term", "context"]
    evidence = pd.DataFrame(all_records, columns=evidence_columns)
    evidence.to_csv(EVIDENCE_PATH, index=False)

    profile = build_profiles(frameworks, domains, all_aggregates)
    publication = load_publication_crosswalk(domains)
    profile = add_publication_provenance(profile, publication)
    profile.to_csv(PROFILE_PATH, index=False)

    summary = summarize(profile, domains, len(frameworks))
    with SUMMARY_PATH.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)

    print(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the non-destructive Land Health expansion.")
    parser.add_argument(
        "--framework",
        default=None,
        help="Optional case-insensitive filename substring to scan a subset of frameworks.",
    )
    args = parser.parse_args()
    run(framework_filter=args.framework)


if __name__ == "__main__":
    main()
