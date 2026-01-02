"""
FAISS-based retriever for movie recommendations
Uses semantic search to find relevant movies based on query
"""
import faiss
import numpy as np
import joblib
import pandas as pd
from sentence_transformers import SentenceTransformer
from typing import List, Optional
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Lazy loading
_model = None
_faiss_index = None
_movies = None

def get_model():
    """Lazy load the sentence transformer model"""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_faiss_index():
    """Lazy load the FAISS index"""
    global _faiss_index
    if _faiss_index is None:
        _faiss_index = faiss.read_index(str(PROJECT_ROOT / "embeddings" / "faiss_index" / "items.index"))
    return _faiss_index

def get_movies():
    """Lazy load the movies dataframe"""
    global _movies
    if _movies is None:
        _movies = joblib.load(str(PROJECT_ROOT / "embeddings" / "faiss_index" / "movies.pkl"))
    return _movies

def retrieve_movies(
    query: str,
    genres: Optional[List[str]] = None,
    top_k: int = 50
) -> pd.DataFrame:
    """
    Retrieve relevant movies using FAISS semantic search.
    
    Args:
        query: Natural language query or genre names
        genres: List of genres to focus on (will be added to query)
        top_k: Number of candidates to retrieve
        
    Returns:
        DataFrame with retrieved movies
    """
    model = get_model()
    index = get_faiss_index()
    movies = get_movies()
    
    # Build enhanced query
    search_text = query
    if genres:
        # Add genres to improve retrieval
        search_text = f"{query} {' '.join(genres)}"
    
    # Generate query embedding
    query_embedding = model.encode([search_text])
    
    # Search FAISS index
    distances, indices = index.search(np.array(query_embedding), top_k)
    
    # Get retrieved movies
    retrieved = movies.iloc[indices[0]].copy()
    retrieved['similarity_score'] = 1 / (1 + distances[0])  # Convert distance to similarity
    
    return retrieved

def filter_by_genre(movies_df: pd.DataFrame, genres: List[str]) -> pd.DataFrame:
    """
    Filter movies by genres. A movie matches if it contains ANY of the specified genres.
    
    Args:
        movies_df: DataFrame with movies
        genres: List of genres to filter by
        
    Returns:
        Filtered DataFrame
    """
    if not genres:
        return movies_df
    
    # Create a mask that checks if any of the genres appear in the movie's genres
    def has_genre(row_genres):
        if pd.isna(row_genres):
            return False
        movie_genres = [g.strip().lower() for g in str(row_genres).split('|')]
        return any(g.lower() in movie_genres for g in genres)
    
    mask = movies_df['genres'].apply(has_genre)
    return movies_df[mask]

def filter_by_exclusions(movies_df: pd.DataFrame, exclude_tags: List[str]) -> pd.DataFrame:
    """
    Filter out movies that match exclusion criteria.
    Uses simple keyword matching against title and genres.
    
    Args:
        movies_df: DataFrame with movies
        exclude_tags: List of tags/keywords to exclude
        
    Returns:
        Filtered DataFrame
    """
    if not exclude_tags:
        return movies_df
    
    # Map common exclusion tags to genre/keyword patterns
    exclusion_map = {
        "violent": ["war", "crime", "action"],
        "violence": ["war", "crime", "action"],
        "sad": ["drama", "tragedy"],
        "scary": ["horror", "thriller"],
        "slow": ["documentary", "drama"],
        "dark": ["horror", "thriller", "noir"],
        "serious": ["documentary", "biography"]
    }
    
    # Expand exclusions using the map
    expanded_exclusions = []
    for tag in exclude_tags:
        tag_lower = tag.lower()
        expanded_exclusions.append(tag_lower)
        if tag_lower in exclusion_map:
            expanded_exclusions.extend(exclusion_map[tag_lower])
    
    # Filter out movies matching any exclusion
    def should_exclude(row):
        text = f"{row.get('title', '')} {row.get('genres', '')}".lower()
        return any(exc in text for exc in expanded_exclusions)
    
    mask = ~movies_df.apply(should_exclude, axis=1)
    return movies_df[mask]

def filter_by_year(
    movies_df: pd.DataFrame,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None
) -> pd.DataFrame:
    """
    Filter movies by release year if year information is available.
    
    Args:
        movies_df: DataFrame with movies
        min_year: Minimum year (inclusive)
        max_year: Maximum year (inclusive)
        
    Returns:
        Filtered DataFrame
    """
    if 'year' not in movies_df.columns:
        return movies_df
    
    filtered = movies_df.copy()
    
    # Ensure year is numeric and filter out NaN values
    filtered = filtered[filtered['year'].notna()]
    
    if min_year is not None:
        filtered = filtered[filtered['year'] >= min_year]
    
    if max_year is not None:
        filtered = filtered[filtered['year'] <= max_year]
    
    return filtered
