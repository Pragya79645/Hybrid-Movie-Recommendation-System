from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, Dict
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.inference.recommend import recommend, mf_model
from src.profiles.profile_manager import build_user_profile, apply_profile_boost
import numpy as np
import json

router = APIRouter()

class CustomPreferences(BaseModel):
    liked_movies: Optional[list[int]] = None
    genres: Optional[Dict[str, float]] = None

def load_user_profiles():
    """Load saved user profiles from JSON file"""
    profile_path = "profiles/user_profiles.json"
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            return json.load(f)
    return {}

@router.get("/recommend")
def get_recommendations(
    user_id: Optional[int] = Query(None, description="User ID for personalized recommendations"),
    top_k: int = Query(5, description="Number of recommendations to return")
):
    """Get recommendations for a specific user or anonymous user"""
    
    # Generate base user vector
    user_vector = np.random.rand(mf_model.n_components)
    
    # Get base recommendations
    recs = recommend(user_vector, top_k=top_k * 2)  # Get more to allow for filtering
    
    # Try to apply user profile if user_id is provided
    profile = None
    profile_applied = False
    
    if user_id is not None:
        # Try to load from saved profiles first
        user_profiles = load_user_profiles()
        if str(user_id) in user_profiles:
            profile = user_profiles[str(user_id)]
            profile_applied = True
        else:
            # Try to build from interaction history
            try:
                profile = build_user_profile(user_id)
                if profile:
                    profile_applied = True
            except:
                pass
    
    # Apply profile boost if available
    if profile:
        recs = apply_profile_boost(recs, profile)
    
    # Return top_k recommendations
    recs = recs.head(top_k)
    
    return {
        "user_id": user_id,
        "recommendations": recs[["title", "genres"]].to_dict(orient="records"),
        "profile_applied": profile_applied,
        "profile": profile if profile_applied else None
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
        "recommendations": recs[["title", "genres"]].to_dict(orient="records"),
        "custom_profile": custom_profile
    }
