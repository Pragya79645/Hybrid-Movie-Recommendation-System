import faiss
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

# Load index + metadata
index = faiss.read_index("embeddings/faiss_index/items.index")
movies = joblib.load("embeddings/faiss_index/movies.pkl")

model = SentenceTransformer("all-MiniLM-L6-v2")

def search_similar_movies(query, top_k=10):
    query_vec = model.encode([query])
    distances, indices = index.search(np.array(query_vec), top_k)

    results = movies.iloc[indices[0]][["title", "genres"]]
    return results
