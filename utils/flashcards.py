# utils/flashcards.py
from utils.notes_db import save_flashcard
import re

def generate_flashcards_from_text(text, max_cards=30):
    """
    Very simple flashcard generation: pick sentences with 'is', 'are', definitions or 'term — definition' patterns.
    More advanced NLP (NER, keyphrase extraction) can be added.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    cards = []
    for sent in sentences:
        if len(cards) >= max_cards:
            break
        # heuristics for definition
        if ' is ' in sent.lower() or ' are ' in sent.lower() or ':' in sent:
            front = sent.strip()
            back = "Recall details / explanation: " + sent.strip()
            cards.append((front, back))
            save_flashcard(front, back)
    return cards
