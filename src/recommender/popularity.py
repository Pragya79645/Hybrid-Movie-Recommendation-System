import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

def get_popularity_recommendations(top_k=5):
    """
    Get popular movie recommendations as a fallback for new users.
    Returns movies sorted by a simple popularity metric.
    
    Args:
        top_k: Number of recommendations to return
    
    Returns:
        DataFrame with popular movie recommendations
    """
    try:
        # Load movies data
        movies = joblib.load(str(PROJECT_ROOT / "embeddings" / "faiss_index" / "movies.pkl"))
        
        # Try to load interactions to compute popularity
        try:
            interactions = pd.read_csv(str(PROJECT_ROOT / "data" / "raw" / "interactions.csv"))
            
            # Calculate popularity score: count of interactions per movie
            popularity = interactions.groupby('movie_id').size().reset_index(name='interaction_count')
            
            # Merge with movie details
            popular_movies = movies.merge(popularity, on='movie_id', how='left')
            popular_movies['interaction_count'] = popular_movies['interaction_count'].fillna(0)
            
            # Sort by popularity and return top_k
            popular_movies = popular_movies.sort_values('interaction_count', ascending=False)
            
        except FileNotFoundError:
            # If no interactions data, return random sample as fallback
            print("⚠️ No interactions data found, returning random sample")
            popular_movies = movies.sample(frac=1, random_state=42)  # Shuffle with seed for consistency
        
        # Return top_k movies
        return popular_movies.head(top_k)[["movie_id", "title", "genres"]].reset_index(drop=True)
        
    except Exception as e:
        print(f"❌ Error getting popularity recommendations: {e}")
        # Ultimate fallback: return empty DataFrame
        return pd.DataFrame(columns=["movie_id", "title", "genres"])
