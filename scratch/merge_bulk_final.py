import json
import os

ONTOLOGY_INDEX = "principles_indicators/Ontology_index.json"

def load_list(path):
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("===")]

def merge_bulk():
    if not os.path.exists(ONTOLOGY_INDEX): return
    with open(ONTOLOGY_INDEX, 'r', encoding='utf-8') as f: data = json.load(f)

    # 1. WAHIS -> Animal Health
    wahis_terms = load_list("principles_indicators/offline_storage/wahis/disease_list.txt")
    for t in wahis_terms:
        data["Animal Health"]["sub_concepts"].append({"label": t, "uri": f"https://www.woah.org/en/disease/{t.replace(' ', '-').lower()}", "source": "WAHIS", "sub_concepts": []})

    # 2. TAPE -> Multiple
    tape_lines = load_list("principles_indicators/offline_storage/tape/criteria.txt")
    tape_map = {
        "Diversity": "Biodiversity",
        "Synergies": "Synergy",
        "Efficiency": "Input Reduction",
        "Resilience": "Soil Health",
        "Recycling": "Recycling",
        "Co-creation": "Co-creation of Knowledge",
        "Human/Social values": "Social Values and Diets",
        "Culture/Food traditions": "Social Values and Diets",
        "Responsible governance": "Land Governance",
        "Economy": "Economic Diversification"
    }
    for line in tape_lines:
        for keyword, principle in tape_map.items():
            if keyword in line:
                data[principle]["sub_concepts"].append({"label": line, "uri": "https://www.fao.org/agroecology/overview/tape/en/", "source": "TAPE", "sub_concepts": []})

    # 3. Land Matrix & Prindex -> Land Governance
    lm_terms = load_list("principles_indicators/offline_storage/land_matrix/indicators.txt")
    for t in lm_terms:
        data["Land Governance"]["sub_concepts"].append({"label": t, "uri": "https://landmatrix.org/data/", "source": "Land_Matrix", "sub_concepts": []})
    
    pr_terms = load_list("principles_indicators/offline_storage/prindex/indicators.txt")
    for t in pr_terms:
        data["Land Governance"]["sub_concepts"].append({"label": t, "uri": "https://www.prindex.net/data/", "source": "Prindex", "sub_concepts": []})

    # 4. OpenLCA -> Recycling
    lca_terms = load_list("principles_indicators/offline_storage/openlca/impact_categories.txt")
    for t in lca_terms:
        data["Recycling"]["sub_concepts"].append({"label": t, "uri": "https://www.openlca.org/methods/", "source": "OpenLCA", "sub_concepts": []})

    # 5. UNBIS -> Land Governance
    unbis_terms = load_list("principles_indicators/offline_storage/unbis/indicators.txt")
    for t in unbis_terms:
        data["Land Governance"]["sub_concepts"].append({"label": t, "uri": "https://metadata.un.org/thesaurus/", "source": "UNBIS", "sub_concepts": []})

    # 6. OSM -> Connectivity
    osm_terms = load_list("principles_indicators/offline_storage/openstreetmap/tags.txt")
    for t in osm_terms:
        data["Connectivity"]["sub_concepts"].append({"label": t, "uri": "https://wiki.openstreetmap.org/wiki/Map_features", "source": "OpenStreetMap", "sub_concepts": []})

    with open(ONTOLOGY_INDEX, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print("Bulk merge complete.")

if __name__ == "__main__":
    merge_bulk()
