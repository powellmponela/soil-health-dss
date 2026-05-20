# WB Indicator Concept Normaliser - Final Pass
# Applies family-based normalization: groups entire WB indicator families
# into their canonical concept name, then strips all demographic variants.
import re
from collections import defaultdict

INPUT_FILE  = r"c:\SOIL HEALTH\principles_indicators\offline_storage\world_bank\terms.txt"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\world_bank\terms_keywords.txt"

# ── FAMILY NORMALISERS ────────────────────────────────────────────────────────
# (pattern, canonical_concept_name)  - applied BEFORE anything else
FAMILY_NORMS = [
    # Student proficiency families -> subject keyword
    (re.compile(r'proficiency level in (reading)', re.I),          "Student proficiency in reading"),
    (re.compile(r'proficiency level in (mathematics|math)', re.I), "Student proficiency in mathematics"),
    (re.compile(r'proficiency level in (science)', re.I),          "Student proficiency in science"),
    (re.compile(r'proficiency level in (numeracy)', re.I),         "Functional numeracy skills"),
    (re.compile(r'proficiency level in (literacy)', re.I),         "Functional literacy skills"),
    (re.compile(r'(reading|mathematics|math|science|numeracy|literacy) proficiency level', re.I),
        lambda m: f"Student proficiency in {m.group(1).lower()}"),

    # Youth idle rate family
    (re.compile(r'^Youth idle rate', re.I),                        "Youth idle rate"),

    # Poverty headcount / gap / severity families
    (re.compile(r'^Poverty (Headcount|Gap|Severity)', re.I),       lambda m: f"Poverty {m.group(1)}"),
    (re.compile(r'^Middle Class .* Headcount', re.I),              "Middle class headcount"),
    (re.compile(r'^Vulnerable .* Headcount', re.I),                "Vulnerable population headcount"),
    (re.compile(r'^Official Moderate Poverty Rate', re.I),         "Official moderate poverty rate"),

    # PISA / TIMSS / LLECE / SACMEQ assessment families
    (re.compile(r'^PISA \d{4}.*\bmath\b', re.I),                  "PISA mathematics assessment"),
    (re.compile(r'^PISA \d{4}.*\breading\b', re.I),               "PISA reading assessment"),
    (re.compile(r'^PISA \d{4}.*\bscience\b', re.I),               "PISA science assessment"),
    (re.compile(r'^TIMSS.*\bmath\b', re.I),                        "TIMSS mathematics achievement"),
    (re.compile(r'^TIMSS.*\bscience\b', re.I),                     "TIMSS science achievement"),
    (re.compile(r'^TIMSS.*\bmath\b', re.I),                        "TIMSS mathematics achievement"),
    (re.compile(r'^LLECE.*\bmath', re.I),                          "LLECE mathematics assessment"),
    (re.compile(r'^LLECE.*\breading\b', re.I),                     "LLECE reading assessment"),
    (re.compile(r'^SACMEQ.*\bmath', re.I),                         "SACMEQ mathematics assessment"),
    (re.compile(r'^SACMEQ.*\breading\b', re.I),                    "SACMEQ reading assessment"),

    # Barro-Lee schooling families
    (re.compile(r'^Barro-Lee:.*years of (primary) schooling', re.I),   "Average years of primary schooling"),
    (re.compile(r'^Barro-Lee:.*years of (secondary) schooling', re.I), "Average years of secondary schooling"),
    (re.compile(r'^Barro-Lee:.*years of (tertiary) schooling', re.I),  "Average years of tertiary schooling"),
    (re.compile(r'^Barro-Lee:.*years of (total) schooling', re.I),     "Average years of total schooling"),
    (re.compile(r'^Barro-Lee:.*no education', re.I),                   "Population with no formal education"),
    (re.compile(r'^Barro-Lee:.*primary schooling.*Completed', re.I),   "Population completing primary education"),
    (re.compile(r'^Barro-Lee:.*secondary schooling.*Completed', re.I), "Population completing secondary education"),
    (re.compile(r'^Barro-Lee:.*tertiary schooling.*Completed', re.I),  "Population completing tertiary education"),

    # DHS attendance/completion families
    (re.compile(r'^DHS: Gross attendance rate\. Post Secondary', re.I), "DHS post-secondary attendance rate"),
    (re.compile(r'^DHS: Net attendance rate\. Primary', re.I),          "DHS primary net attendance rate"),
    (re.compile(r'^DHS: Net attendance rate\. Secondary', re.I),        "DHS secondary net attendance rate"),
    (re.compile(r'^DHS: Primary completion rate', re.I),               "DHS primary completion rate"),
    (re.compile(r'^DHS: Secondary completion rate', re.I),             "DHS secondary completion rate"),
    (re.compile(r'^DHS: Net intake rate', re.I),                       "DHS net intake rate"),
    (re.compile(r'^DHS: Proportion of out-of-school', re.I),           "DHS out-of-school rate"),
    (re.compile(r'^DHS: Transition rate', re.I),                       "DHS primary-to-secondary transition rate"),
    (re.compile(r'^DHS: Typology.*Dropped out', re.I),                 "DHS school dropout rate"),
    (re.compile(r'^DHS: Typology.*Late entry', re.I),                  "DHS late school entry rate"),
    (re.compile(r'^DHS: Typology.*Never in school', re.I),             "DHS never-enrolled rate"),

    # HOI families
    (re.compile(r'^HOI: Electricity', re.I),                           "HOI: Access to electricity"),
    (re.compile(r'^HOI: Internet', re.I),                              "HOI: Internet access"),
    (re.compile(r'^HOI: Water', re.I),                                 "HOI: Access to safe water"),
    (re.compile(r'^HOI: Sanitation', re.I),                            "HOI: Access to sanitation"),
    (re.compile(r'^HOI: Mobile Phone', re.I),                          "HOI: Mobile phone access"),
    (re.compile(r'^HOI: Finished Primary School', re.I),               "HOI: Primary school completion"),
    (re.compile(r'^HOI: School Enrollment', re.I),                     "HOI: School enrollment"),
    (re.compile(r'^HOI: Mathematics Proficiency', re.I),               "HOI: Mathematics proficiency"),
    (re.compile(r'^HOI: Reading Proficiency', re.I),                   "HOI: Reading proficiency"),
    (re.compile(r'^HOI: Science Proficiency', re.I),                   "HOI: Science proficiency"),

    # Emission families  
    (re.compile(r'^Emission Totals.*AFOLU', re.I),                     "Agricultural emissions - AFOLU"),
    (re.compile(r'^Emission Totals.*Enteric Fermentation', re.I),      "Emissions from enteric fermentation"),
    (re.compile(r'^Emission Totals.*Manure Management', re.I),         "Emissions from manure management"),
    (re.compile(r'^Emission Totals.*Synthetic Fertilizers', re.I),     "Emissions from synthetic fertilizers"),
    (re.compile(r'^Emission Totals.*Rice Cultivation', re.I),          "Emissions from rice cultivation"),
    (re.compile(r'^Emission Totals.*Forest fires', re.I),              "Emissions from forest fires"),
    (re.compile(r'^Emission Totals.*On-farm energy use', re.I),        "On-farm energy use emissions"),
    (re.compile(r'^Emission Totals.*Crop Residues', re.I),             "Emissions from crop residues"),
    (re.compile(r'^Emission Totals.*Land Use change', re.I),           "Land use change emissions"),

    # Nonrenewable natural capital
    (re.compile(r'^Nonrenewable natural capital.*coal', re.I),         "Nonrenewable natural capital - coal"),
    (re.compile(r'^Nonrenewable natural capital.*natural gas', re.I),  "Nonrenewable natural capital - natural gas"),
    (re.compile(r'^Nonrenewable natural capital.*oil', re.I),          "Nonrenewable natural capital - oil"),
    (re.compile(r'^Nonrenewable natural capital.*metals', re.I),       "Nonrenewable natural capital - metals and minerals"),
    (re.compile(r'^Nonrenewable natural capital$', re.I),              "Nonrenewable natural capital"),

    # Renewable natural capital
    (re.compile(r'^Renewable natural capital.*agricultural land', re.I), "Renewable natural capital - agricultural land"),
    (re.compile(r'^Renewable natural capital.*fisheries', re.I),         "Renewable natural capital - fisheries"),
    (re.compile(r'^Renewable natural capital.*timber', re.I),            "Renewable natural capital - timber"),
    (re.compile(r'^Renewable natural capital.*mangroves', re.I),         "Renewable natural capital - mangroves"),
    (re.compile(r'^Renewable natural capital.*forest water', re.I),      "Forest water ecosystem services"),
    (re.compile(r'^Renewable natural capital.*nonwood forest', re.I),    "Nonwood forest protection services"),

    # Government expenditure on education
    (re.compile(r'^Government expenditure on (lower secondary) education as', re.I), "Government expenditure - lower secondary education"),
    (re.compile(r'^Government expenditure on (upper secondary) education as', re.I), "Government expenditure - upper secondary education"),
    (re.compile(r'^Government expenditure on (pre-primary) education as', re.I),     "Government expenditure - pre-primary education"),
    (re.compile(r'^Government expenditure on (primary) education as', re.I),         "Government expenditure - primary education"),
    (re.compile(r'^Government expenditure on (secondary) education as', re.I),       "Government expenditure - secondary education"),
    (re.compile(r'^Government expenditure on (tertiary) education as', re.I),        "Government expenditure - tertiary education"),
    (re.compile(r'^Government expenditure on education', re.I),                      "Government expenditure on education"),

    # Initial government/household funding per student
    (re.compile(r'^Initial government funding per (primary) student as', re.I),   "Government funding per primary student"),
    (re.compile(r'^Initial government funding per (secondary) student as', re.I),  "Government funding per secondary student"),
    (re.compile(r'^Initial government funding per (tertiary) student as', re.I),   "Government funding per tertiary student"),
    (re.compile(r'^Initial household funding per (primary) student as', re.I),     "Household funding per primary student"),
    (re.compile(r'^Initial household funding per (secondary) student as', re.I),   "Household funding per secondary student"),
    (re.compile(r'^Initial household funding per (tertiary) student as', re.I),    "Household funding per tertiary student"),

    # Annual statutory teacher salaries (keep level)
    (re.compile(r'^Annual statutory teacher salaries.*Lower Secondary', re.I), "Teacher salary - lower secondary"),
    (re.compile(r'^Annual statutory teacher salaries.*Upper Secondary', re.I), "Teacher salary - upper secondary"),
    (re.compile(r'^Annual statutory teacher salaries.*Pre-Primary', re.I),     "Teacher salary - pre-primary"),
    (re.compile(r'^Annual statutory teacher salaries.*Primary', re.I),         "Teacher salary - primary"),

    # Functional difficulty (youth idle rate family)
    (re.compile(r'functional (difficulty|disability)', re.I),     "Functional difficulty"),
    (re.compile(r'mobility difficulty', re.I),                     "Mobility difficulty"),
    (re.compile(r'seeing difficulty', re.I),                       "Seeing difficulty"),
    (re.compile(r'selfcare difficulty', re.I),                     "Selfcare difficulty"),

    # Population by level of proficiency in functional skills
    (re.compile(r'functional (numeracy) skills?', re.I),           "Functional numeracy skills"),
    (re.compile(r'functional (literacy) skills?', re.I),           "Functional literacy skills"),

    # School feeding
    (re.compile(r'School Feeding', re.I),                          "School feeding programme"),
    (re.compile(r'Adjusted net attendance rate.*primary entry', re.I), "Net attendance rate - pre-primary"),

    # Proportion of students achieving proficiency (short form)
    (re.compile(r'^Proportion of students.*mathematics', re.I),    "Student proficiency in mathematics"),
    (re.compile(r'^Proportion of students.*reading', re.I),        "Student proficiency in reading"),
    (re.compile(r'^Proportion of students.*science', re.I),        "Student proficiency in science"),
    (re.compile(r'^Proportion of population achieving.*numeracy', re.I),  "Functional numeracy proficiency"),
    (re.compile(r'^Proportion of population achieving.*literacy', re.I),  "Functional literacy proficiency"),
    (re.compile(r'^Proportion of population achieving.*reading', re.I),   "Reading proficiency"),
    (re.compile(r'^Proportion of population achieving.*math', re.I),      "Mathematics proficiency"),
    (re.compile(r'^Proportion of population achieving.*science', re.I),   "Science proficiency"),

    # Natural disaster
    (re.compile(r'^Natural disaster.*Damage to home or livestock', re.I), "Natural disaster damage to home or livestock"),
]

# ── HARD DISCARD patterns ────────────────────────────────────────────────────
DISCARD_PATTERNS = [
    re.compile(r'^\d{3,4}_'),
    re.compile(r'#V[A-Z]{3,}_\d+'),
    re.compile(r'^9\d{6,}:'),
    re.compile(r'Adequacy of (benefits|social safety) in \d', re.I),
    re.compile(r'Beneficiary incidence in \d', re.I),
    re.compile(r'Benefits incidence in \d', re.I),
    re.compile(r'Coverage in \d', re.I),
    re.compile(r'^All staff compensation as', re.I),
    re.compile(r'^Capital expenditure as %', re.I),
    re.compile(r'^Current (education )?expenditure (other|as %)', re.I),
    re.compile(r'^(End|Start|Ending|Starting) (month|year)', re.I),
    re.compile(r'International aid disbursed to basic education, [A-Z]{2,}', re.I),
    re.compile(r'Cross-country public sector pay comparison', re.I),
    re.compile(r'Average per capita transfer held by \d', re.I),
    re.compile(r'Avg per capita transfer held by \d', re.I),
    re.compile(r'(Individuals|Females|Males) with \w+ education as a share', re.I),
    re.compile(r'Number of people (pushed|spending)', re.I),
    re.compile(r'^About (one|two) months can be covered', re.I),
    re.compile(r'Proportion of population (facing|further|pushed)', re.I),
    re.compile(r'Deposited money.*\b(less than|monthly|weekly|Never)\b', re.I),
    re.compile(r'Coverage of .* in \d', re.I),
    re.compile(r'Government expenditure per student', re.I),
    re.compile(r'Emission Totals - (Emissions from (CH4|N2O)|Direct|Indirect)', re.I),
]

# ── DEMOGRAPHIC TAIL stripper ─────────────────────────────────────────────────
STRIP_TAIL = re.compile(
    r'[,\s]+(female|male|rural|urban|total|both sexes|areas?|'
    r'adjusted (gender|location|wealth|native|language|speaks) parity index|'
    r'Q[1-5]|in laborforce|out of laborforce|'
    r'primary education (or less|and below)|secondary education (or more|and above)|'
    r'poorest( \d+%)?|richest( \d+%)?|'
    r'(first|second|third|fourth|fifth|middle) quintile|'
    r'young|older|women|men|ages? [\d\-]+|'
    r'above primary( education)?|primary and below|'
    r'constant (PPP|US)\$?|PPP\$?|US\$?|local currency unit|PPP dollars|'
    r'age-standardized|'
    r'(high|low|all|none|immigrant|non-immigrant) (socio-economic|background)|'
    r'very (affluent|poor) socioeconomic background|'
    r'did not speak the language.*|spoke the language.*|'
    r'not speak.*|speak.*).*$',
    re.IGNORECASE
)
STRIP_PARENS = re.compile(r'\s*\([^)]{0,150}\)\s*')
STRIP_CODES  = re.compile(r'\s*[_#][A-Z0-9_]{2,}$')

STOPWORDS = {
    'of','in','to','for','and','or','the','a','an','by','at','as','with',
    'is','are','per','on','from','that','this','be','was','were','has',
    'have','had','do','does','not','but','if','its','it','no','nor',
    'so','yet','both','either','than','into','total','all','only','any',
    'more','less','which','where','when','how','what','who','whether',
    'proportion','percentage','number'
}

def normalise(raw):
    """Try family normalisers first; return canonical name if matched."""
    for pat, canon in FAMILY_NORMS:
        m = pat.search(raw)
        if m:
            if callable(canon):
                return canon(m)
            return canon
    return None

def should_discard(raw):
    for pat in DISCARD_PATTERNS:
        if pat.search(raw):
            return True
    return False

def clean_generic(raw):
    """Generic cleaning: strip parens, tail demographics, codes."""
    t = STRIP_PARENS.sub(' ', raw.strip())
    t = STRIP_TAIL.sub('', t)
    t = STRIP_CODES.sub('', t)
    t = re.sub(r'[-–]\s*(rural|urban|national|global|total|male|female|world|oecd|'
               r'low income|middle income|high income).*$', '', t, flags=re.I)
    t = re.sub(r'\s+', ' ', t).strip().rstrip('.,;:-|_ ')
    return t

def is_meaningful(t):
    if len(t) < 6:
        return False
    if re.match(r'^[\d\W]+$', t):
        return False
    words = t.lower().split()
    ok = [w for w in words if w not in STOPWORDS and len(w) > 2 and not w.isdigit()]
    return len(ok) >= 1

def main():
    print("Loading...")
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

            raw_term, _, principles_str = line.partition('|')
            raw_term = raw_term.strip()
            principles = [p.strip() for p in principles_str.split(',') if p.strip()]

            if should_discard(raw_term):
                continue

            # Try family normalisers first
            concept = normalise(raw_term)
            # Fall back to generic cleaning
            if not concept:
                concept = clean_generic(raw_term)

            if concept and is_meaningful(concept):
                for p in principles:
                    term_principles[concept].add(p)

    print(f"Raw lines         : {raw_count:,}")
    print(f"Unique concepts   : {len(term_principles):,}")

    by_principle = defaultdict(list)
    for term, principles in sorted(term_principles.items()):
        primary = sorted(principles)[0]
        by_principle[primary].append((term, sorted(principles)))

    total = 0
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for principle in sorted(by_principle.keys()):
            terms_list = sorted(by_principle[principle], key=lambda x: x[0].lower())
            f.write(f"=== {principle} ({len(terms_list)} terms) ===\n")
            for term, all_p in terms_list:
                tag = f" | {', '.join(all_p)}" if len(all_p) > 1 else ""
                f.write(f"  {term}{tag}\n")
                total += 1
            f.write("\n")

    print(f"Written           : {total:,} unique concept keywords")
    print(f"Saved to          : {OUTPUT_FILE}")
    print("\n--- Count by Principle ---")
    for p in sorted(by_principle.keys()):
        print(f"  {p}: {len(by_principle[p])}")

if __name__ == "__main__":
    main()
