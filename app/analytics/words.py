import re
from collections import Counter

STOPWORDS = {
    "the", "is", "and", "to", "of", "in", "for", "on",
    "with", "a", "an", "this", "that", "it", "as", "are"
}

def extract_word_frequencies(texts, top_n=50):
    words = []

    for text in texts:
        tokens = re.findall(r"[a-zA-Z]{3,}", text.lower())
        words.extend([t for t in tokens if t not in STOPWORDS])

    return Counter(words).most_common(top_n)
