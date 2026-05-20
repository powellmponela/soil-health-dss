"""
inject_refined_wb.py
====================
1. Remove all existing World_Bank nodes from Ontology_index.json
2. Inject the refined concept keywords from terms_keywords.txt
3. Save the updated ontology
"""
import json
import re
from collections import defaultdict

ONTOLOGY_FILE = r"c:\SOIL HEALTH\principles_indicators\Ontology_index.json"
KEYWORDS_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\world_bank\terms_keywords.txt"

def load_keywords():
    """Parse terms_keywords.txt → {principle: [(term, all_principles), ...]}"""
    principle_terms = defaultdict(list)  # primary_principle -> [(label, all_principles)]
    
    current_principle = None
    with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            # Header: === Principle Name (N terms) ===
            hdr = re.match(r'^=== (.+?) \(\d+ terms\) ===$', line)
            if hdr:
                current_principle = hdr.group(1).strip()
                continue
            # Term line: "  TERM LABEL | Principle1, Principle2"
            if current_principle and line.startswith('  ') and line.strip():
                content = line.strip()
                if ' | ' in content:
                    label, _, all_p_str = content.partition(' | ')
                    all_principles = [p.strip() for p in all_p_str.split(',')]
                else:
                    label = content
                    all_principles = [current_principle]
                label = label.strip()
                if label:
                    principle_terms[current_principle].append((label, all_principles))
    return principle_terms

def make_wb_node(label, uri_slug):
    """Create a clean WB ontology node."""
    return {
        "uri": f"world_bank_refined:{uri_slug}",
        "label": label,
        "sub_concepts": [],
        "source": "World_Bank"
    }

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')[:60]

def main():
    print("Loading Master Ontology...")
    with open(ONTOLOGY_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Loading refined WB keywords...")
    keyword_map = load_keywords()

    total_removed = 0
    total_added = 0

    for principle, node in data.items():
        # Step 1: remove all old World_Bank nodes
        old_subs = node.get('sub_concepts', [])
        non_wb = [n for n in old_subs if n.get('source') != 'World_Bank']
        removed = len(old_subs) - len(non_wb)
        total_removed += removed

        # Step 2: build new WB nodes from refined keywords for this principle
        new_wb_nodes = []
        seen_labels = {n['label'].lower() for n in non_wb}  # avoid duplication with other sources

        terms_for_principle = keyword_map.get(principle, [])
        for label, all_principles in terms_for_principle:
            if label.lower() not in seen_labels:
                uri_slug = slugify(label)
                new_wb_nodes.append(make_wb_node(label, uri_slug))
                seen_labels.add(label.lower())

        # Step 3: also inject terms where this principle appears in all_principles
        # (multi-mapped terms — inject into all their mapped principles)
        for src_principle, terms in keyword_map.items():
            if src_principle == principle:
                continue  # already handled above
            for label, all_principles in terms:
                if principle in all_principles and label.lower() not in seen_labels:
                    uri_slug = slugify(label)
                    new_wb_nodes.append(make_wb_node(label, uri_slug))
                    seen_labels.add(label.lower())

        node['sub_concepts'] = non_wb + new_wb_nodes
        total_added += len(new_wb_nodes)
        print(f"  {principle}: removed {removed} old, added {len(new_wb_nodes)} refined WB nodes")

    print(f"\nTotal removed: {total_removed:,}")
    print(f"Total added  : {total_added:,}")

    print(f"\nSaving updated ontology to {ONTOLOGY_FILE}...")
    with open(ONTOLOGY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print("Done.")

if __name__ == "__main__":
    main()
