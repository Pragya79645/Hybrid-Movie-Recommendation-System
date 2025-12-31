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
    
    # Handle non-recommendation intents
    if parsed["intent"] != "recommend_movie":
        return {
            "response": "I can help you find movies you'll enjoy! 😊 Tell me what kind of movies you like.",
            "movies": []
        }
    
    # Build temporary profile from extracted preferences
    profile = {genre: 1.0 for genre in parsed["genres"]}
    
    # Generate user vector (dummy for now, can be enhanced with user_id later)
    user_vector = np.random.rand(50)
    
    # Get recommendations from the recommendation engine
    recs = recommend(user_vector)
    
    # Apply profile boost based on extracted preferences
    if profile:
        recs = apply_profile_boost(recs, profile)
    
    # Build natural language response
    genre_text = ", ".join(parsed["genres"]) if parsed["genres"] else "great"
    mood_text = f" with a {parsed['mood']} mood" if parsed.get("mood") else ""
    
    response = f"Here are some {genre_text} movies{mood_text} you might like 🎬"
    
    return {
        "response": response,
        "recommendations": recs.head(10).to_dict(orient="records") if hasattr(recs, 'to_dict') else []
    }