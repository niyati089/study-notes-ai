# utils/embed.py
import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# model for embeddings
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

def semantic_chunks(text, max_words=450):
    """Create semantic chunks by sentence boundaries, not breaking sentences mid-way."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current = [], ""
    for s in sentences:
        if len((current + " " + s).split()) <= max_words:
            current = (current + " " + s).strip()
        else:
            if current:
                chunks.append(current.strip())
            current = s
    if current:
        chunks.append(current.strip())
    return chunks

def build_faiss_index(chunks):
    emb = embed_model.encode(chunks, convert_to_numpy=True)
    emb = emb.astype("float32")
    # normalized inner product for cosine
    faiss.normalize_L2(emb)
    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(emb)
    return index, emb
