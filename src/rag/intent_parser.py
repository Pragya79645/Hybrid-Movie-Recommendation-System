import os
import json
import re
from google.genai import Client

# Lazy initialization - client will be created when first needed
_client = None

def get_client():
    global _client
    if _client is None:
        _client = Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client

def parse_intent_fallback(message: str):
    """
    Fallback regex-based intent parser when Gemini API fails.
    Less sophisticated but functional.
    """
    message_lower = message.lower()
    
    # Check if it's a movie recommendation request
    recommendation_keywords = ['recommend', 'suggest', 'want', 'looking for', 'find', 'show me', 'i like']
    is_recommendation = any(keyword in message_lower for keyword in recommendation_keywords)
    
    # Extract genres using common movie genre keywords
    genre_map = {
        'thriller': 'Thriller',
        'action': 'Action', 
        'sci-fi': 'Sci-Fi',
        'scifi': 'Sci-Fi',
        'science fiction': 'Sci-Fi',
        'horror': 'Horror',
        'scary': 'Horror',
        'comedy': 'Comedy',
        'funny': 'Comedy',
        'drama': 'Drama',
        'romance': 'Romance',
        'romantic': 'Romance',
        'adventure': 'Adventure',
        'fantasy': 'Fantasy',
        'crime': 'Crime',
        'mystery': 'Mystery',
        'animation': 'Animation',
        'documentary': 'Documentary',
        'war': 'War',
        'western': 'Western'
    }
    
    genres = []
    for keyword, genre in genre_map.items():
        if keyword in message_lower:
            if genre not in genres:
                genres.append(genre)
    
    # Extract exclusions
    exclude_tags = []
    exclusion_patterns = [
        (r'not\s+(?:very\s+)?violent', 'violent'),
        (r'not\s+(?:too\s+)?dark', 'dark'),
        (r'not\s+(?:too\s+)?sad', 'sad'),
        (r'not\s+(?:too\s+)?scary', 'scary'),
        (r'not\s+(?:too\s+)?slow', 'slow'),
        (r'avoid\s+violence', 'violent'),
        (r'avoid\s+dark', 'dark'),
        (r"isn't\s+(?:too\s+)?dark", 'dark'),
        (r"aren't\s+(?:too\s+)?dark", 'dark'),
    ]
    
    for pattern, tag in exclusion_patterns:
        if re.search(pattern, message_lower):
            if tag not in exclude_tags:
                exclude_tags.append(tag)
    
    # Extract year constraints
    min_year = None
    max_year = None
    
    if 'recent' in message_lower or 'new' in message_lower:
        min_year = 2015
    elif 'classic' in message_lower or 'old' in message_lower:
        max_year = 2000
    
    # Year patterns like "from the 80s" or "1990s"
    year_match = re.search(r'(\d{4})s', message_lower)
    if year_match:
        decade_start = int(year_match.group(1))
        min_year = decade_start
        max_year = decade_start + 9
    
    # Extract mood
    mood = None
    mood_keywords = ['scary', 'uplifting', 'dark', 'funny', 'sad', 'suspenseful', 'exciting']
    for keyword in mood_keywords:
        if keyword in message_lower:
            mood = keyword
            break
    
    intent = "recommend_movie" if (is_recommendation or genres) else "other"
    
    return {
        "intent": intent,
        "genres": genres,
        "mood": mood,
        "exclude_tags": exclude_tags,
        "min_year": min_year,
        "max_year": max_year,
        "title": None,
        "search_query": None
    }

SYSTEM_PROMPT = """
You are an intent extractor for a movie recommendation system.

Extract intent and preferences from the message.
Return ONLY valid JSON.

JSON format:
{
    "intent": "recommend_movie | other",
    "genres": [],
    "mood": null,
    "exclude_tags": [],
    "min_year": null,
    "max_year": null,
    "title": null,
    "search_query": null
}

Important:
- genres: List of movie genres (e.g., ["Thriller", "Action"])
- mood: Descriptive mood if mentioned (e.g., "dark", "uplifting", "suspenseful")
- exclude_tags: Things to avoid (e.g., ["violent", "sad", "slow"])
- min_year/max_year: Year constraints if mentioned
- title/search_query: If user mentions a specific movie title

Examples:
- "I want a thriller movie" → {"intent": "recommend_movie", "genres": ["Thriller"], "mood": null, "exclude_tags": []}
- "Something scary but not too violent" → {"intent": "recommend_movie", "genres": ["Horror"], "mood": "scary", "exclude_tags": ["violent"]}
- "I want a thriller but not very violent" → {"intent": "recommend_movie", "genres": ["Thriller"], "mood": null, "exclude_tags": ["violent"]}
- "Recent action movies" → {"intent": "recommend_movie", "genres": ["Action"], "mood": null, "min_year": 2020}
- "Classic sci-fi from the 80s" → {"intent": "recommend_movie", "genres": ["Sci-Fi"], "mood": null, "min_year": 1980, "max_year": 1989}
- "Hello" → {"intent": "other", "genres": [], "mood": null, "exclude_tags": []}
- "Find The Matrix" → {"intent": "recommend_movie", "genres": [], "mood": null, "title": "The Matrix", "search_query": "The Matrix"}
"""

def parse_intent(message: str):
    """
    Parse user message to extract intent and preferences.
    Uses Gemini API with fallback to regex-based parsing.
    
    Args:
        message: User's natural language message
        
    Returns:
        dict: Parsed intent with genres, mood, and constraints
    """
    try:
        client = get_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=SYSTEM_PROMPT + "\nUser message: " + message
        )
        
        # Extract JSON from response (handle markdown code blocks)
        response_text = response.text.strip()
        print(f"[Intent Parser] Using Gemini API")  # Debug log
        
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
            
        parsed = json.loads(response_text)
        print(f"[Intent Parser] Parsed intent: {parsed}")  # Debug log
        
        # Ensure all expected keys exist with defaults
        parsed.setdefault("exclude_tags", [])
        parsed.setdefault("min_year", None)
        parsed.setdefault("max_year", None)
        parsed.setdefault("title", None)
        parsed.setdefault("search_query", None)
        parsed.setdefault("mood", None)
        
        return parsed
    except Exception as e:
        # Fallback to regex-based parsing on any error
        print(f"[Intent Parser] Gemini failed, using regex fallback: {str(e)[:100]}")
        return parse_intent_fallback(message)
