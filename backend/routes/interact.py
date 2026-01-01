from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.profiles.profile_manager import update_user_profile

router = APIRouter()

class InteractionRequest(BaseModel):
    user_id: str
    movie_id: int
    genres: List[str]

@router.post("/interact")
def track_interaction(interaction: InteractionRequest):
    """Track user interaction and update their profile"""
    
    # Update user profile with this interaction
    profile = update_user_profile(
        user_id=interaction.user_id,
        movie_id=interaction.movie_id,
        genres=interaction.genres
    )
    
    return {
        "success": True,
        "user_id": interaction.user_id,
        "updated_profile": profile
    }
