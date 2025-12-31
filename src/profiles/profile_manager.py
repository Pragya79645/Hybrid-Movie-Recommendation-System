import pandas as pd

def build_user_profile(user_id, interactions_path="data/processed/train.csv", items_path="data/processed/items.csv"):
    ratings = pd.read_csv(interactions_path)
    items = pd.read_csv(items_path)
    
    user_movies = ratings[ratings['user_id']==user_id].merge(items, on='movie_id')
    if user_movies.empty:
        return None
    
    genres = user_movies['genres'].str.split("|").explode()
    profile = genres.value_counts(normalize=True).to_dict()
    return profile

def apply_profile_boost(recommendations, profile):
    if not profile:
        return recommendations

    def score(row):
        return sum(profile.get(g, 0) for g in row["genres"].split("|"))

    recommendations["profile_score"] = recommendations.apply(score, axis=1)
    return recommendations.sort_values("profile_score", ascending=False)
