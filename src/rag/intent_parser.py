import os
import json
from google.genai import Client

# Lazy initialization - client will be created when first needed
_client = None

def get_client():
    global _client
    if _client is None:
        _client = Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client

SYSTEM_PROMPT = """
You are an intent extractor for a movie recommendation system.

Extract intent and preferences from the message.
Return ONLY valid JSON.

JSON format:
{
    "intent": "recommend_movie | other",
    "genres": [],
    "mood": null,
    "title": null,
    "search_query": null
}

Examples:
- "I want a thriller movie" → {"intent": "recommend_movie", "genres": ["thriller"], "mood": null}
- "Something scary" → {"intent": "recommend_movie", "genres": ["horror"], "mood": "scary"}
- "Hello" → {"intent": "other", "genres": [], "mood": null}
- "Find The Matrix" → {"intent": "recommend_movie", "genres": [], "mood": null, "title": "The Matrix", "search_query": "The Matrix"}
- "Any good comedy like Groundhog Day?" → {"intent": "recommend_movie", "genres": ["comedy"], "mood": null, "title": "Groundhog Day", "search_query": "Groundhog Day"}
"""

def parse_intent(message: str):
    """
    Parse user message to extract intent and preferences.
    
    Args:
        message: User's natural language message
        
    Returns:
        dict: Parsed intent with genres and mood
    """
    try:
        client = get_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=SYSTEM_PROMPT + "\nUser message: " + message
        )
        
        # Extract JSON from response (handle markdown code blocks)
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
            
        return json.loads(response_text)
    except Exception as e:
        print(f"Error parsing intent: {e}")
        # Return default on error
        return {
            "intent": "other",
            "genres": [],
            "mood": None
        }
