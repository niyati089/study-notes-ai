# utils/preprocess.py
import re
from collections import Counter

def clean_text(text):
    text = text.replace("\xa0", " ").strip()
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text

def split_sentences(text):
    # Simple sentence splitter without NLTK
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def detect_topics(text, top_n=10):
    """Naive keyword-frequency topic detection for TOC generation."""
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    freq = Counter(words)
    common = [w for w, _ in freq.most_common(top_n)]
    return common
