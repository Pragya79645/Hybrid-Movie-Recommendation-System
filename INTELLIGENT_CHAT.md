# Intelligent Chat System 🤖

## Overview
The chat system uses a **multi-stage pipeline** that combines LLM intelligence with traditional recommendation techniques. This prevents LLM hallucinations while providing natural language interaction.

## 🔥 Key Innovation: Chat Does NOT Recommend Directly

**❌ Bad Approach (Hallucination-prone):**
```
User: "I want a thriller"
LLM: "Try The Departed, Shutter Island, Gone Girl"
     ↑ LLM might make up movies or give wrong genres
```

**✅ Good Approach (Grounded in Data):**
```
User: "I want a thriller but not very violent"
     ↓
Intent Extraction: {"genre": "Thriller", "exclude": ["violent"]}
     ↓
FAISS Retrieval: Fetch thriller movies from vector store
     ↓
Filtering: Remove violent content
     ↓
Re-ranking: Apply user preferences
     ↓
Explanation: LLM explains WHY each movie matches
```

## Architecture

### 5-Stage Pipeline

```
┌─────────────────┐
│  User Message   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ 1. Intent Extraction    │  ← Gemini extracts structured intent
│    (Gemini)             │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ 2. FAISS Retrieval      │  ← Semantic search for candidates
│    (Vector Search)      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ 3. Constraint Filtering │  ← Apply genre/year/exclusion filters
│    (Rule-based)         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ 4. Re-ranking           │  ← Personalization + similarity scoring
│    (Profile-based)      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ 5. Explanation          │  ← Gemini explains each recommendation
│    (Gemini)             │
└────────┬────────────────┘
         │
         ▼
    Final Results
```

## Stage Details

### Stage 1: Intent Extraction 🧠

**Module:** [src/rag/intent_parser.py](src/rag/intent_parser.py)

Gemini extracts structured intent from natural language:

**Input:**
```
"I want a thriller but not very violent"
```

**Output:**
```json
{
  "intent": "recommend_movie",
  "genres": ["Thriller"],
  "mood": null,
  "exclude_tags": ["violent"],
  "min_year": null,
  "max_year": null
}
```

**Supported Constraints:**
- `genres`: List of genres (Thriller, Action, Sci-Fi, etc.)
- `mood`: Descriptive mood (scary, uplifting, dark, etc.)
- `exclude_tags`: Things to avoid (violent, sad, slow, dark)
- `min_year` / `max_year`: Year constraints
- `title` / `search_query`: Specific movie mentions

### Stage 2: FAISS Retrieval 🔍

**Module:** [src/rag/retriever.py](src/rag/retriever.py)

Uses semantic search to find relevant candidates:

```python
from src.rag.retriever import retrieve_movies

candidates = retrieve_movies(
    query="Thriller",
    genres=["Thriller"],
    top_k=100  # Get many candidates for filtering
)
```

**How it works:**
1. Builds search query from genres + mood
2. Generates embedding using SentenceTransformer
3. Searches FAISS index for similar movies
4. Returns top-k candidates with similarity scores

### Stage 3: Constraint Filtering 🚫

**Module:** [src/rag/retriever.py](src/rag/retriever.py)

Applies filters to narrow down candidates:

**Filter Functions:**
- `filter_by_genre()` - Keep only movies matching genres
- `filter_by_exclusions()` - Remove unwanted content
- `filter_by_year()` - Apply year constraints

**Example:**
```python
# Start with 100 FAISS candidates
candidates = retrieve_movies(...)  # 100 movies

# Filter by genre (strict)
candidates = filter_by_genre(candidates, ["Thriller"])  # 60 movies

# Remove violent content
candidates = filter_by_exclusions(candidates, ["violent"])  # 40 movies

# Recent movies only
candidates = filter_by_year(candidates, min_year=2010)  # 25 movies
```

**Exclusion Mapping:**
The system intelligently maps exclusion tags to genre patterns:
- `violent` → excludes War, Crime, Action
- `sad` → excludes Drama, Tragedy
- `scary` → excludes Horror, Thriller
- `dark` → excludes Horror, Thriller, Noir

### Stage 4: Re-ranking 📊

**Module:** [src/profiles/profile_manager.py](src/profiles/profile_manager.py)

Re-ranks filtered candidates using:

1. **User Profile** (if user_id provided):
   ```python
   score = base_score + (user_genre_weight × boost_multiplier)
   ```

2. **Similarity Score** (from FAISS):
   ```python
   similarity = 1 / (1 + distance)
   ```

**Personalization:**
- If user has interaction history, boost genres they like
- Otherwise, sort by FAISS similarity score

### Stage 5: Explanation Generation 💡

**Module:** [src/rag/explainer.py](src/rag/explainer.py)

Gemini generates personalized explanations for top recommendations:

**Input:**
```python
generate_explanations(
    movies=[...],
    user_query="I want a thriller but not very violent",
    intent={"genres": ["Thriller"], "exclude_tags": ["violent"]},
    max_movies=5
)
```

**Output:**
```json
[
  {
    "title": "The Sixth Sense",
    "genres": "Drama|Mystery|Thriller",
    "explanation": "A psychological thriller that builds suspense through mystery and atmosphere rather than violence, perfect for what you're looking for."
  },
  ...
]
```

## API Usage

### Basic Chat Request

```bash
POST http://localhost:8000/chat
Content-Type: application/json

{
  "message": "I want a thriller but not very violent"
}
```

**Response:**
```json
{
  "response": "Found 10 Thriller movies, avoiding violent for you! 🎬",
  "recommendations": [
    {
      "movie_id": 123,
      "title": "The Sixth Sense",
      "genres": "Drama|Mystery|Thriller",
      "explanation": "A psychological thriller that builds suspense through mystery..."
    }
  ]
}
```

### Personalized Chat Request

```bash
POST http://localhost:8000/chat?user_id=alice
Content-Type: application/json

{
  "message": "Recommend something"
}
```

Results will be re-ranked based on Alice's interaction history.

## Example Conversations

### Example 1: Genre with Constraints
**User:** "I want a thriller but not very violent"

**System Flow:**
1. Intent: `{genres: ["Thriller"], exclude_tags: ["violent"]}`
2. FAISS: Retrieves 100 thriller-related movies
3. Filter: Removes movies with Crime, War, Action genres
4. Re-rank: Sorts by FAISS similarity
5. Explain: Generates personalized explanations

**Response:** 10 thrillers focused on psychological tension rather than action/violence

### Example 2: Mood-based
**User:** "Something scary"

**System Flow:**
1. Intent: `{genres: ["Horror"], mood: "scary"}`
2. FAISS: Searches for "scary Horror" movies
3. Filter: None
4. Re-rank: By similarity
5. Explain: Emphasizes scary elements

**Response:** Horror movies with high scare factor

### Example 3: Time Period
**User:** "Classic sci-fi from the 80s"

**System Flow:**
1. Intent: `{genres: ["Sci-Fi"], min_year: 1980, max_year: 1989}`
2. FAISS: Retrieves sci-fi movies
3. Filter: Year range 1980-1989
4. Re-rank: By similarity
5. Explain: Highlights classic 80s sci-fi elements

**Response:** 80s sci-fi classics

### Example 4: Multiple Genres
**User:** "Action sci-fi movies"

**System Flow:**
1. Intent: `{genres: ["Action", "Sci-Fi"]}`
2. FAISS: Searches for "Action Sci-Fi movie"
3. Filter: Movies with Action OR Sci-Fi genres
4. Re-rank: By similarity
5. Explain: Mentions both genre elements

**Response:** Action-packed sci-fi films

## Why This Approach Works

### ✅ Advantages

1. **No Hallucinations**: LLM never invents movie titles
2. **Grounded in Data**: All recommendations come from actual dataset
3. **Intelligent Filtering**: Natural language → precise constraints
4. **Personalized**: Uses user interaction history
5. **Explainable**: Clear reasoning for each recommendation
6. **Scalable**: FAISS handles large datasets efficiently

### 🎯 Comparison

| Approach | Hallucination Risk | Data Grounding | Scalability |
|----------|-------------------|----------------|-------------|
| Pure LLM | ❌ High | ❌ Low | ✅ High |
| Traditional | ✅ None | ✅ High | ⚠️ Medium |
| **Hybrid (Ours)** | ✅ None | ✅ High | ✅ High |

## Configuration

### Gemini Model
File: [src/rag/intent_parser.py](src/rag/intent_parser.py)

```python
model="gemini-2.0-flash-exp"  # Fast intent extraction
```

### FAISS Parameters
File: [backend/routes/chat.py](backend/routes/chat.py)

```python
top_k=100  # Number of candidates to retrieve
max_movies=5  # Number to explain with Gemini
```

### Personalization Boost
File: [backend/routes/chat.py](backend/routes/chat.py)

```python
boost_multiplier=1.5  # How much to weight user preferences
```

## Files Modified

### New Files Created
- ✅ `src/rag/retriever.py` - FAISS retrieval and filtering
- ✅ `src/rag/explainer.py` - Gemini explanation generation
- ✅ `test_chat_intelligence.py` - Comprehensive test suite

### Files Updated
- ✅ `src/rag/intent_parser.py` - Enhanced with exclusions and year constraints
- ✅ `backend/routes/chat.py` - Complete pipeline implementation

## Testing

Run the comprehensive test:
```bash
python test_chat_intelligence.py
```

This tests:
- Simple genre requests
- Genre with exclusions (the critical feature!)
- Mood-based queries
- Multiple genres
- Time period constraints
- Personalized recommendations
- Non-recommendation queries

## Next Steps

🚀 **Potential Enhancements:**
- Add user feedback loop (thumbs up/down)
- Implement conversation history (multi-turn dialogue)
- Add actor/director constraints
- Implement "similar to X" queries
- Add rating/popularity filters
- Support multiple languages
- Cache FAISS results for common queries
- Add A/B testing for different boost multipliers
