import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import joblib

movies = pd.read_csv("data/processed/items.csv")
movies["text"] = movies["title"] + " " + movies["genres"]

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(movies["text"].tolist(), show_progress_bar=True)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

faiss.write_index(index, "embeddings/faiss_index/items.index")
joblib.dump(movies, "embeddings/faiss_index/movies.pkl")
print("FAISS index saved!")
