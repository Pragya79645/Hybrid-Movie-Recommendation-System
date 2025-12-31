from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
import sys
import os
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.rag.intent_parser import parse_intent
from src.inference.recommend import recommend
from src.profiles.profile_manager import apply_profile_boost
import joblib
import re

# Load movies dataset for title/search matching
movies = joblib.load("embeddings/faiss_index/movies.pkl")

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat_endpoint(
    request: ChatRequest,
    user_id: Optional[int] = Query(None, description="User ID for context")
):
    """Chat with the movie recommendation assistant using Gemini for intent extraction"""
    
    # Parse user intent and preferences using Gemini
    parsed = parse_intent(request.message)

    # If Gemini didn't detect a recommend intent, return a helpful prompt
    if parsed.get("intent") != "recommend_movie":
        return {
            "response": "I can help you find movies you'll enjoy! 😊 Tell me what kind of movies you like.",
            "recommendations": []
        }

    # If an exact title or search_query was extracted, try to find matching movie(s)
    search_text = parsed.get("title") or parsed.get("search_query")
    if search_text:
        q = str(search_text).strip().lower()
        # Normalize text for more robust matching (handles variants like "Matrix, The (1999)")
        def normalize_text(s: str) -> str:
            return re.sub(r'[^a-z0-9\s]', '', str(s).lower()).strip()

        q_norm = normalize_text(q)
        title_norms = movies['title'].fillna('').apply(normalize_text)

        # Match when normalized title contains the normalized query OR all query words appear in title
        mask = title_norms.str.contains(q_norm, na=False) | title_norms.apply(lambda t: all(w in t.split() for w in q_norm.split()))
        matches = movies[mask]
        if not matches.empty:
            # Apply any genre-based boosts
            if parsed.get("genres"):
                profile = {g: 1.0 for g in parsed.get("genres", [])}
                matches = apply_profile_boost(matches, profile)

            response = f"Here are matches for \"{search_text}\" you might be looking for 🎬"
            return {
                "response": response,
                "recommendations": matches.head(10).to_dict(orient="records")
            }

    # Build temporary profile from extracted preferences
    profile = {genre: 1.0 for genre in parsed.get("genres", [])}

    # Generate user vector (dummy for now, can be enhanced with user_id later)
    user_vector = np.random.rand(50)

    # Get recommendations from the recommendation engine
    recs = recommend(user_vector)

    # Apply profile boost based on extracted preferences
    if profile:
        recs = apply_profile_boost(recs, profile)

    # Build natural language response
    genre_text = ", ".join(parsed.get("genres", [])) if parsed.get("genres") else "great"
    mood_text = f" with a {parsed.get('mood')} mood" if parsed.get("mood") else ""

    response = f"Here are some {genre_text} movies{mood_text} you might like 🎬"

    return {
        "response": response,
        "recommendations": recs.head(10).to_dict(orient="records") if hasattr(recs, 'to_dict') else []
    }