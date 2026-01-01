from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, Dict
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.inference.recommend import recommend, mf_model
from src.profiles.profile_manager import build_user_profile, apply_profile_boost, get_user_profile
import numpy as np
import json

router = APIRouter()

class CustomPreferences(BaseModel):
    liked_movies: Optional[list[int]] = None
    genres: Optional[Dict[str, float]] = None

@router.get("/recommend")
def get_recommendations(
    user_id: Optional[str] = Query(None, description="User ID for personalized recommendations"),
    top_k: int = Query(5, description="Number of recommendations to return")
):
    """Get personalized recommendations for a user"""
    
    # Generate base user vector
    user_vector = np.random.rand(mf_model.n_components)
    
    # Get base recommendations (get more to allow for re-ranking)
    recs = recommend(user_vector, top_k=top_k * 3)
    
    # Try to apply user profile if user_id is provided
    profile = None
    profile_applied = False
    
    if user_id is not None:
        # Load user profile from saved profiles
        profile = get_user_profile(user_id)
        if profile and profile.get("genre_weights"):
            profile_applied = True
            # Apply personalized scoring: base_score + user_genre_weight
            recs = apply_profile_boost(recs, profile, boost_multiplier=2.0)
    
    # Return top_k recommendations
    recs = recs.head(top_k)
    
    return {
        "user_id": user_id,
        "recommendations": recs[["movie_id", "title", "genres"]].to_dict(orient="records"),
        "personalized": profile_applied,
        "profile": profile.get("genre_weights") if profile else None
    }

@router.post("/recommend/custom")
def get_custom_recommendations(
    preferences: CustomPreferences,
    top_k: int = Query(5, description="Number of recommendations to return")
):
    """Get recommendations based on custom preferences (genres or liked movies)"""
    
    # Generate base user vector
    user_vector = np.random.rand(mf_model.n_components)
    
    # Get base recommendations
    recs = recommend(user_vector, top_k=top_k * 3)  # Get more to allow for filtering
    
    # Apply custom genre preferences
    custom_profile = preferences.genres if preferences.genres else {}
    
    if custom_profile:
        recs = apply_profile_boost(recs, custom_profile)
    
    # Return top_k recommendations
    recs = recs.head(top_k)
    
    return {
        "recommendations": recs[["movie_id", "title", "genres"]].to_dict(orient="records"),
        "custom_profile": custom_profile
    }
