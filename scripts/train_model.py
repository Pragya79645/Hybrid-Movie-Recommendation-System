import joblib
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
import pandas as pd

# Load processed data
ratings = pd.read_csv("data/processed/train.csv")
users = ratings['user_id'].unique()
movies = ratings['movie_id'].unique()

user_map = {u: i for i, u in enumerate(users)}
movie_map = {m: i for i, m in enumerate(movies)}

ratings['user_idx'] = ratings['user_id'].map(user_map)
ratings['movie_idx'] = ratings['movie_id'].map(movie_map)

matrix = csr_matrix((ratings.rating, (ratings.user_idx, ratings.movie_idx)))

svd = TruncatedSVD(n_components=50, random_state=42)
user_embeddings = svd.fit_transform(matrix)
movie_embeddings = svd.components_.T

joblib.dump(svd, "models/mf_model.pkl")
print("MF model saved!")
