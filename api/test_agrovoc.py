from agrovoc_utils import search_agrovoc, batch_enrich_terms

terms_to_test = ["carbon sequestration", "agroecology", "soil health", "smallholder"]

print("Testing AGROVOC Lookups:")
for term in terms_to_test:
    result = search_agrovoc(term)
    if result:
        print(f"[OK] {term} -> {result['prefLabel']} ({result['uri']})")
    else:
        print(f"[FAIL] {term} -> No match found")

print("\nTesting Batch Enrichment:")
batch_results = batch_enrich_terms(terms_to_test)
print(f"Enriched {len(batch_results)} out of {len(terms_to_test)} terms.")
