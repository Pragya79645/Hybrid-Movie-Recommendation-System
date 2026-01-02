import joblib
import pandas as pd
import numpy as np
import faiss
import os
from pathlib import Path
from src.profiles.profile_manager import apply_profile_boost

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load artifacts with absolute paths
mf_model = joblib.load(str(PROJECT_ROOT / "models" / "mf_model.pkl"))
movies = joblib.load(str(PROJECT_ROOT / "embeddings" / "faiss_index" / "movies.pkl"))
faiss_index = faiss.read_index(str(PROJECT_ROOT / "embeddings" / "faiss_index" / "items.index"))

def recommend(user_vector, top_k=5):
    scores = mf_model.components_.T @ user_vector
    top_idx = np.argsort(scores)[-top_k:][::-1]
    return movies.iloc[top_idx][["movie_id", "title", "genres"]]

if __name__ == "__main__":
    dummy_user_vector = np.random.rand(mf_model.n_components)
    recs = recommend(dummy_user_vector)
    
    # Apply profile personalization
    profile = {"Sci-Fi": 0.6, "Action": 0.4}
    recs = apply_profile_boost(recs, profile)
    
    print(recs)
