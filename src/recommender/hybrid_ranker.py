import joblib
import numpy as np
import faiss
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

mf_model = joblib.load(str(PROJECT_ROOT / "models" / "mf_model.pkl"))
movie_embeddings = mf_model.components_.T
index = faiss.read_index(str(PROJECT_ROOT / "embeddings" / "faiss_index" / "items.index"))
movies = joblib.load(str(PROJECT_ROOT / "embeddings" / "faiss_index" / "movies.pkl"))

def recommend(user_idx, user_emb, top_k=5, profile=None, alpha=0.5, beta=0.4, gamma=0.1):
    # CF Score
    cf_scores = movie_embeddings @ user_emb

    # FAISS Score
    if profile:
        query = " ".join(profile.keys())
        query_emb = mf_model.transform([query])[0]  # or semantic embedding
        D, I = index.search(np.array([query_emb]), top_k)
        faiss_scores = np.zeros_like(cf_scores)
        faiss_scores[I[0]] = 1
    else:
        faiss_scores = np.zeros_like(cf_scores)

    # Hybrid
    final_scores = alpha*cf_scores + beta*faiss_scores + gamma*0  # gamma=popularity fallback
    top_movies_idx = np.argsort(final_scores)[-top_k:][::-1]
    return movies.iloc[top_movies_idx]
