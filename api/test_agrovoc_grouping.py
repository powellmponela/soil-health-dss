import sys
import os

# Add api directory to path
sys.path.append(os.path.join(os.getcwd(), "api"))
from agrovoc_utils import search_agrovoc

terms_to_test = ["composting", "biodiversity", "market", "policy"]

print("Testing AGROVOC Principle Grouping:")
for term in terms_to_test:
    result = search_agrovoc(term)
    if result:
        principles = result.get('principles', [])
        print(f"Term: {term:15} | AGROVOC: {result['prefLabel']:20} | Principles: {', '.join(principles) if principles else 'None'}")
    else:
        print(f"Term: {term:15} | No Match")
