import pandas as pd
import json
import os
from typing import List, Dict
from collections import defaultdict

PROFILE_PATH = "profiles/user_profiles.json"

def load_profiles() -> Dict:
    """Load all user profiles from JSON file"""
    if os.path.exists(PROFILE_PATH):
        try:
            with open(PROFILE_PATH, 'r') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return {}
        except (json.JSONDecodeError, ValueError):
            # File is corrupted or empty, return empty dict
            return {}
    return {}

def save_profiles(profiles: Dict):
    """Save all user profiles to JSON file"""
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    with open(PROFILE_PATH, 'w') as f:
        json.dump(profiles, f, indent=2)

def update_user_profile(user_id: str, movie_id: int, genres: List[str], weight: float = 1.0) -> Dict:
    """
    Update user profile based on interaction with a movie.
    Uses exponential moving average to update genre weights.
    
    Args:
        user_id: User identifier
        movie_id: Movie that was interacted with
        genres: List of genres for the movie
        weight: Weight of this interaction (default 1.0)
    
    Returns:
        Updated user profile
    """
    profiles = load_profiles()
    
    # Get or create user profile
    if user_id not in profiles:
        profiles[user_id] = {
            "genre_weights": {},
            "interaction_count": 0
        }
    
    user_profile = profiles[user_id]
    current_weights = user_profile.get("genre_weights", {})
    interaction_count = user_profile.get("interaction_count", 0)
    
    # Calculate learning rate (decreases as user has more interactions)
    # This prevents old preferences from being overwritten too quickly
    alpha = 0.3 if interaction_count < 10 else 0.1
    
    # Update genre weights using exponential moving average
    updated_weights = current_weights.copy()
    for genre in genres:
        current_weight = updated_weights.get(genre, 0.0)
        # Increase weight for interacted genre
        updated_weights[genre] = current_weight + alpha * (weight - current_weight)
    
    # Normalize weights to sum to 1.0
    total = sum(updated_weights.values())
    if total > 0:
        updated_weights = {k: v/total for k, v in updated_weights.items()}
    
    # Update profile
    user_profile["genre_weights"] = updated_weights
    user_profile["interaction_count"] = interaction_count + 1
    user_profile["last_interaction"] = {"movie_id": movie_id, "genres": genres}
    
    profiles[user_id] = user_profile
    save_profiles(profiles)
    
    return user_profile

def get_user_profile(user_id: str) -> Dict:
    """Get user profile by ID"""
    profiles = load_profiles()
    return profiles.get(user_id, None)

def build_user_profile(user_id, interactions_path="data/processed/train.csv", items_path="data/processed/items.csv"):
    """Build user profile from historical interaction data"""
    ratings = pd.read_csv(interactions_path)
    items = pd.read_csv(items_path)
    
    user_movies = ratings[ratings['user_id']==user_id].merge(items, on='movie_id')
    if user_movies.empty:
        return None
    
    genres = user_movies['genres'].str.split("|").explode()
    profile = genres.value_counts(normalize=True).to_dict()
    return profile

def apply_profile_boost(recommendations, profile, boost_multiplier: float = 2.0):
    """
    Apply personalized scoring to recommendations based on user profile.
    
    Args:
        recommendations: DataFrame with movie recommendations
        profile: User profile dict or genre weights dict
        boost_multiplier: How much to weight user preferences (default 2.0)
    
    Returns:
        Re-ranked recommendations DataFrame
    """
    if not profile:
        return recommendations
    
    # Handle both profile dict and direct genre weights
    if isinstance(profile, dict) and "genre_weights" in profile:
        genre_weights = profile["genre_weights"]
    else:
        genre_weights = profile
    
    if not genre_weights:
        return recommendations

    def calculate_score(row):
        """Calculate personalized score for a movie"""
        # Base score (could be from collaborative filtering, popularity, etc.)
        base_score = 1.0
        
        # Genre boost from user profile
        user_genre_weight = sum(
            genre_weights.get(g, 0) for g in row["genres"].split("|")
        )
        
        # Combined score: base_score + boosted user preference
        return base_score + (user_genre_weight * boost_multiplier)

    recommendations["personalized_score"] = recommendations.apply(calculate_score, axis=1)
    return recommendations.sort_values("personalized_score", ascending=False)
