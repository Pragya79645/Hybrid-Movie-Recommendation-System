from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import faiss
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
import os
from pathlib import Path

router = APIRouter()

# Load FAISS index and movie data
FAISS_INDEX_PATH = Path(__file__).parent.parent.parent / "embeddings" / "faiss_index" / "items.index"
MOVIES_PKL_PATH = Path(__file__).parent.parent.parent / "embeddings" / "faiss_index" / "movies.pkl"

# Initialize model and load FAISS index
model = SentenceTransformer("all-MiniLM-L6-v2")
faiss_index = None
movies_df = None

def load_faiss_resources():
    """Load FAISS index and movies data"""
    global faiss_index, movies_df
    
    if faiss_index is None:
        if not FAISS_INDEX_PATH.exists():
            raise FileNotFoundError(f"FAISS index not found at {FAISS_INDEX_PATH}")
        faiss_index = faiss.read_index(str(FAISS_INDEX_PATH))
    
    if movies_df is None:
        if not MOVIES_PKL_PATH.exists():
            raise FileNotFoundError(f"Movies pickle not found at {MOVIES_PKL_PATH}")
        movies_df = joblib.load(str(MOVIES_PKL_PATH))
    
    return faiss_index, movies_df

class SimilarMovie(BaseModel):
    movie_id: int
    title: str
    genres: str
    similarity_score: float

class SearchResponse(BaseModel):
    query_movie: str
    similar_movies: List[SimilarMovie]
    total_results: int

@router.get("/search/similar", response_model=SearchResponse)
def search_similar_movies(
    movie_name: str = Query(..., description="Name of the movie to search for"),
    top_k: int = Query(10, ge=1, le=50, description="Number of similar movies to return")
):
    """
    Search for similar movies based on movie name using FAISS similarity search.
    
    Flow:
    1. Find movie_id for the given movie name
    2. Get its embedding from FAISS index
    3. FAISS search for top K nearest neighbors
    4. Return movie metadata
    
    This is content-based recommendation using:
    - Plot/Overview
    - Genres
    - Keywords
    - Themes
    
    No LLM required - pure vector similarity search.
    """
    try:
        # Load FAISS resources
        index, movies = load_faiss_resources()
        
        # Step 1: Find movie by name (case-insensitive partial match)
        # Escape special regex characters in movie_name
        import re
        escaped_name = re.escape(movie_name)
        movie_matches = movies[movies['title'].str.contains(escaped_name, case=False, na=False, regex=True)]
        
        if movie_matches.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Movie '{movie_name}' not found. Please try a different title."
            )
        
        # Get the first match (or best match)
        query_movie = movie_matches.iloc[0]
        query_movie_idx = movie_matches.index[0]
        query_movie_title = query_movie['title']
        
        # Step 2: Get embedding for this movie
        # Recreate the text representation used during embedding creation
        query_text = f"{query_movie['title']} {query_movie['genres']}"
        query_embedding = model.encode([query_text])
        
        # Step 3: FAISS search for nearest neighbors
        # Search for top_k + 1 because the first result will be the query movie itself
        distances, indices = index.search(np.array(query_embedding, dtype=np.float32), top_k + 1)
        
        # Step 4: Return movie metadata
        # First, add the searched movie itself with 100% similarity
        similar_movies = [SimilarMovie(
            movie_id=int(query_movie['movie_id']),
            title=query_movie['title'],
            genres=query_movie['genres'],
            similarity_score=1.0000
        )]
        
        # Then add similar movies
        for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            # Skip the query movie itself (it's already added as first result)
            if idx == query_movie_idx:
                continue
            
            if len(similar_movies) > top_k:
                break
            
            movie = movies.iloc[idx]
            
            # Convert L2 distance to similarity score (inverse relationship)
            # Lower distance = higher similarity
            similarity_score = 1 / (1 + float(distance))
            
            similar_movies.append(SimilarMovie(
                movie_id=int(movie['movie_id']),
                title=movie['title'],
                genres=movie['genres'],
                similarity_score=round(similarity_score, 4)
            ))
        
        return SearchResponse(
            query_movie=query_movie_title,
            similar_movies=similar_movies,
            total_results=len(similar_movies)
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) as-is
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/search/autocomplete")
def autocomplete_movies(
    query: str = Query(..., min_length=1, description="Partial movie title to search for"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions")
):
    """
    Autocomplete movie titles for search suggestions.
    Returns a list of movie titles that match the query.
    """
    try:
        _, movies = load_faiss_resources()
        
        # Find movies that contain the query string (case-insensitive)
        # Escape special regex characters
        import re
        escaped_query = re.escape(query)
        matches = movies[movies['title'].str.contains(escaped_query, case=False, na=False, regex=True)]
        
        # Return top matches
        suggestions = matches.head(limit)[['movie_id', 'title', 'genres']].to_dict(orient='records')
        
        return {
            "query": query,
            "suggestions": suggestions,
            "count": len(suggestions)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autocomplete error: {str(e)}")
