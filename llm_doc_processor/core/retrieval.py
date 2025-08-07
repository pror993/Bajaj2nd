import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

def load_index_and_segments():
    index = faiss.read_index("models/faiss.index")
    embeddings = np.load("models/embeddings.npy")
    with open("models/segments.txt", encoding="utf8") as f:
        segments = [line.strip() for line in f.readlines()]
    return index, embeddings, segments

def retrieve_relevant_segments(query, top_k=5):
    index, embeddings, segments = load_index_and_segments()
    query_emb = EMBED_MODEL.encode([query])
    D, I = index.search(query_emb, top_k)
    results = []
    for idx, score in zip(I[0], D[0]):
        if idx < len(segments):
            results.append({"clause_id": idx, "text": segments[idx], "score": float(score)})
    return results
