"""
Gemini-based explanation generator for movie recommendations
"""
import os
from google.genai import Client
from typing import List, Dict

# Lazy initialization
_client = None

def get_client():
    global _client
    if _client is None:
        _client = Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client

def generate_explanations(
    movies: List[Dict],
    user_query: str,
    intent: Dict,
    max_movies: int = 5
) -> List[Dict]:
    """
    Generate personalized explanations for why each movie was recommended.
    
    Args:
        movies: List of movie dicts with title, genres, etc.
        user_query: Original user query
        intent: Parsed intent dictionary
        max_movies: Maximum number of movies to explain
        
    Returns:
        List of movie dicts with added 'explanation' field
    """
    if not movies:
        return []
    
    # Limit to first max_movies to avoid token limits
    movies_to_explain = movies[:max_movies]
    
    # Build context for Gemini
    genres_text = ", ".join(intent.get("genres", [])) if intent.get("genres") else "any genre"
    mood_text = f" with a {intent.get('mood')} mood" if intent.get("mood") else ""
    exclude_text = f" (avoiding {', '.join(intent.get('exclude_tags', []))})" if intent.get("exclude_tags") else ""
    
    prompt = f"""You are a movie recommendation explainer.

User asked: "{user_query}"
User wants: {genres_text}{mood_text}{exclude_text}

For each movie below, write a brief 1-2 sentence explanation of WHY it matches what the user wants.
Be specific, mention the genres, and connect to the user's preferences.

Movies:
"""
    
    for i, movie in enumerate(movies_to_explain, 1):
        prompt += f"\n{i}. {movie.get('title', 'Unknown')} - Genres: {movie.get('genres', 'Unknown')}"
    
    prompt += "\n\nReturn ONLY a JSON array of explanations in this format:\n"
    prompt += '[\n  "explanation for movie 1",\n  "explanation for movie 2",\n  ...\n]\n'
    prompt += "\nMake explanations concise, engaging, and personalized to the user's request."
    
    try:
        client = get_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # Extract JSON array from response
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        import json
        explanations = json.loads(response_text)
        
        # Add explanations to movies
        result = []
        for i, movie in enumerate(movies_to_explain):
            movie_copy = movie.copy()
            if i < len(explanations):
                movie_copy['explanation'] = explanations[i]
            else:
                movie_copy['explanation'] = "A great match for your preferences!"
            result.append(movie_copy)
        
        # Add remaining movies without explanations
        for movie in movies[max_movies:]:
            result.append(movie)
        
        return result
        
    except Exception as e:
        print(f"Error generating explanations: {e}")
        # Return movies with generic explanations on error
        return [
            {**movie, 'explanation': 'Recommended based on your preferences'}
            for movie in movies
        ]

def generate_chat_response(
    user_query: str,
    intent: Dict,
    num_recommendations: int
) -> str:
    """
    Generate a natural language response for the chat.
    
    Args:
        user_query: Original user query
        intent: Parsed intent dictionary
        num_recommendations: Number of movies being recommended
        
    Returns:
        Natural language response string
    """
    genres_text = ", ".join(intent.get("genres", [])) if intent.get("genres") else "great"
    mood_text = f" with a {intent.get('mood')} mood" if intent.get("mood") else ""
    exclude_text = f", avoiding {' and '.join(intent.get('exclude_tags', []))}" if intent.get("exclude_tags") else ""
    
    if num_recommendations == 0:
        return f"I couldn't find any {genres_text} movies{mood_text}{exclude_text}. Try adjusting your criteria!"
    
    return f"Found {num_recommendations} {genres_text} movies{mood_text}{exclude_text} for you! 🎬"
