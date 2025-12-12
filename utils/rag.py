# utils/rag.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

RAG_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve(query, index, embeddings, chunks, top_k=5):
    """
    Return top_k chunks and scores. Uses FAISS index for speed,
    then returns chunk texts + normalized scores.
    """
    q_emb = RAG_MODEL.encode([query], convert_to_numpy=True).astype("float32")
    # normalize for cosine with the index already normalized
    faiss_scores, idxs = index.search(q_emb, top_k)
    # faiss returns inner product values; convert to 0..1 roughly
    raw_scores = faiss_scores[0].tolist()
    result = []
    for i, score in zip(idxs[0], raw_scores):
        if i < 0:
            continue
        result.append({"chunk": chunks[i], "index": int(i), "score": float(score)})
    # normalized mapping
    max_s = max([r['score'] for r in result]) if result else 1.0
    for r in result:
        r['norm_score'] = r['score'] / max_s if max_s else r['score']
    return result
