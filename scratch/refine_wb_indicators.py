import re
from collections import defaultdict

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\world_bank\terms.txt"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\world_bank\terms_refined.txt"

# Patterns to strip: demographic disaggregations, percentage qualifiers, currency qualifiers, geographic suffixes
STRIP_PATTERNS = [
    # Remove parenthetical details entirely
    r'\(.*?\)',
    # Remove trailing dashes with qualifiers like -Rural, -Urban, -Male, -Female, -National
    r'\s*-\s*(Rural|Urban|Male|Female|National|Total|All|Ages?\s[\d\-]+)\s*$',
    # Remove leading/trailing whitespace from each part
]

KNOWN_STOPWORDS = {
    'of', 'in', 'to', 'for', 'and', 'or', 'the', 'a', 'an', 'by', 'at', 
    'as', 'with', 'is', 'are', 'per', 'on', 'from', 'that', 'this', 'be',
    'was', 'were', 'has', 'have', 'had', 'do', 'does', 'not', 'but', 'if',
    'its', 'it', 'no', 'nor', 'so', 'yet', 'both', 'either', 'than', 'into',
    'total', 'all', 'both'
}

def clean_term(raw_term):
    """Strip demographic breakdowns and statistical qualifiers to get the core concept."""
    term = raw_term.strip()
    # Remove parenthetical content (%, age ranges, gender, geography, disability qualifiers)
    term = re.sub(r'\s*\(.*?\)\s*', ' ', term)
    # Remove trailing geo/demographic suffixes after dash
    term = re.sub(r'\s*[-–]\s*(Rural|Urban|Male|Female|National|Total|Global|World|OECD|High income|Low income|Middle income).*$', '', term, flags=re.IGNORECASE)
    # Normalize whitespace
    term = re.sub(r'\s+', ' ', term).strip()
    # Remove trailing punctuation
    term = term.rstrip('.,;:')
    return term

def is_meaningful(term):
    """Filter out very short or stop-word-only terms."""
    if len(term) < 4:
        return False
    words = term.lower().split()
    meaningful_words = [w for w in words if w not in KNOWN_STOPWORDS and len(w) > 2]
    return len(meaningful_words) >= 1

def main():
    print(f"Loading {INPUT_FILE}...")
    # Group: cleaned_term -> set of principles
    term_principles = defaultdict(set)
    raw_count = 0

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            raw_count += 1
            if '|' not in line:
                continue
            parts = line.split('|', 1)
            raw_term = parts[0].strip()
            principles_str = parts[1].strip() if len(parts) > 1 else ''
            principles = [p.strip() for p in principles_str.split(',') if p.strip()]

            cleaned = clean_term(raw_term)
            if not is_meaningful(cleaned):
                continue

            for p in principles:
                term_principles[cleaned].add(p)

    # Sort by principle then term
    print(f"Raw lines: {raw_count}")
    print(f"Unique refined terms: {len(term_principles)}")
    
    # Group by primary principle (first one alphabetically for multi-mapped)
    by_principle = defaultdict(list)
    for term, principles in sorted(term_principles.items()):
        primary = sorted(principles)[0]  # deterministic
        by_principle[primary].append((term, sorted(principles)))

    # Write output
    total_written = 0
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for principle in sorted(by_principle.keys()):
            terms_list = sorted(by_principle[principle], key=lambda x: x[0].lower())
            f.write(f"=== {principle} ({len(terms_list)} terms) ===\n")
            for term, all_principles in terms_list:
                if len(all_principles) > 1:
                    f.write(f"  {term} | {', '.join(all_principles)}\n")
                else:
                    f.write(f"  {term}\n")
                total_written += 1
            f.write("\n")

    print(f"Written {total_written} refined terms to {OUTPUT_FILE}")

    # Print summary by principle
    print("\n--- Refined Term Count by Principle ---")
    for principle in sorted(by_principle.keys()):
        print(f"  {principle}: {len(by_principle[principle])}")

if __name__ == "__main__":
    main()
