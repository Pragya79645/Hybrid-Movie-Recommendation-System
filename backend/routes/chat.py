from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.rag.intent_parser import parse_intent
from src.rag.retriever import retrieve_movies, filter_by_genre, filter_by_exclusions, filter_by_year
from src.rag.explainer import generate_explanations, generate_chat_response
from src.profiles.profile_manager import apply_profile_boost, get_user_profile

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat_endpoint(
    request: ChatRequest,
    user_id: Optional[str] = Query(None, description="User ID for personalization")
):
    """
    Intelligent chat endpoint for movie recommendations.
    
    Flow:
    1. Extract intent from user message (Gemini)
    2. Retrieve candidates using FAISS semantic search
    3. Filter by constraints (genre, exclusions, year)
    4. Re-rank using user profile if available
    5. Generate explanations (Gemini)
    """
    
    # Step 1: Parse intent using Gemini
    print(f"🔍 Parsing intent from: {request.message}")
    intent = parse_intent(request.message)
    print(f"📋 Intent: {intent}")
    
    # If not a recommendation request, return helpful message
    if intent.get("intent") != "recommend_movie":
        return {
            "response": "I can help you find movies you'll enjoy! 😊 Tell me what kind of movies you like, or describe the mood you're in.",
            "recommendations": []
        }
    
    # Step 2: Retrieve candidates using FAISS
    # Build query from genres and mood
    query_parts = []
    if intent.get("genres"):
        query_parts.extend(intent["genres"])
    if intent.get("mood"):
        query_parts.append(intent["mood"])
    
    search_query = " ".join(query_parts) if query_parts else "movie"
    
    print(f"🔎 FAISS search query: {search_query}")
    candidates = retrieve_movies(
        query=search_query,
        genres=intent.get("genres"),
        top_k=100  # Get many candidates for filtering
    )
    print(f"📦 Retrieved {len(candidates)} candidates from FAISS")
    
    # Step 3: Apply filters
    # Filter by genre (strict matching)
    if intent.get("genres"):
        candidates = filter_by_genre(candidates, intent["genres"])
        print(f"🎭 After genre filter: {len(candidates)} movies")
    
    # Filter by exclusions (remove unwanted content)
    if intent.get("exclude_tags"):
        candidates = filter_by_exclusions(candidates, intent["exclude_tags"])
        print(f"🚫 After exclusion filter: {len(candidates)} movies")
    
    # Filter by year constraints
    if intent.get("min_year") or intent.get("max_year"):
        candidates = filter_by_year(
            candidates,
            min_year=intent.get("min_year"),
            max_year=intent.get("max_year")
        )
        print(f"📅 After year filter: {len(candidates)} movies")
    
    if candidates.empty:
        return {
            "response": "I couldn't find any movies matching your criteria. Try being less specific or adjusting your preferences!",
            "recommendations": []
        }
    
    # Step 4: Re-rank using user profile if available
    if user_id:
        profile = get_user_profile(user_id)
        if profile and profile.get("genre_weights"):
            print(f"👤 Applying personalization for user: {user_id}")
            candidates = apply_profile_boost(candidates, profile, boost_multiplier=1.5)
        else:
            # Sort by similarity score from FAISS
            candidates = candidates.sort_values("similarity_score", ascending=False)
    else:
        # Sort by similarity score from FAISS
        candidates = candidates.sort_values("similarity_score", ascending=False)
    
    # Get top recommendations
    top_k = 10
    recommendations = candidates.head(top_k)
    
    print(f"⭐ Final recommendations: {len(recommendations)} movies")
    
    # Step 5: Generate explanations using Gemini
    recs_list = recommendations.to_dict(orient="records")
    recs_with_explanations = generate_explanations(
        movies=recs_list,
        user_query=request.message,
        intent=intent,
        max_movies=5  # Explain top 5
    )
    
    # Generate chat response
    response_text = generate_chat_response(
        user_query=request.message,
        intent=intent,
        num_recommendations=len(recs_with_explanations)
    )
    
    return {
        "response": response_text,
        "recommendations": recs_with_explanations
    }