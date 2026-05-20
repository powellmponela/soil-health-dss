import re
from collections import Counter
import json

INPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\wocat_all_sentences.txt"
OUTPUT_FILE = r"c:\SOIL HEALTH\principles_indicators\offline_storage\wocat\wocat_word_frequencies.json"

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        text = f.read().lower()
    
    # Tokenize words (alphanumeric only)
    words = re.findall(r'\b\w+\b', text)
    
    # Filter out common stopwords (basic list)
    stopwords = set(["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "of", "is", "are", "was", "were", "it", "this", "that", "these", "those", "from", "as", "into", "can", "will", "has", "have", "had", "be", "been", "which", "who", "whom", "where", "when", "why", "how"])
    
    filtered_words = [w for w in words if w not in stopwords and len(w) > 2]
    
    counts = Counter(filtered_words)
    
    # Get top 2000 words
    top_words = counts.most_common(2000)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(top_words, f, indent=4)
        
    print(f"Calculated frequencies for {len(counts)} unique words.")
    print(f"Top words saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
