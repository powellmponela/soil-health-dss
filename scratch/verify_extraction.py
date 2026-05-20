content = open(r'c:\SOIL HEALTH\principles_indicators\framework_word_by_word_extraction.txt', encoding='utf-8').read()
lines = content.splitlines()

wb_terms = ['Youth idle rate', 'Functional numeracy', 'Student proficiency',
            'School feeding programme', 'Functional difficulty', 'HOI:']

print('=== Refined WB terms appearing in extraction ===')
for kw in wb_terms:
    hits = [l for l in lines if kw.lower() in l.lower()]
    print(f'  {kw}: {len(hits)} occurrences')

old_terms = ['Youth idle rate (% of persons living',
             'Proportion of students at the end of primary education achieving at least']
print('\n=== Old verbose terms (should be GONE) ===')
for kw in old_terms:
    hits = [l for l in lines if kw.lower() in l.lower()]
    print(f'  "{kw[:55]}...": {len(hits)} occurrences')

fw_start = [i for i,l in enumerate(lines) if l.startswith('=') and 'Framework:' in l]
if fw_start:
    idx = fw_start[0]
    print('\n=== Sample framework output (first 12 lines) ===')
    for l in lines[idx:idx+12]:
        print(l)
