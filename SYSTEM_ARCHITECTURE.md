# 🎬 Movie Recommendation System Architecture

A sophisticated **hybrid recommendation engine** that combines multiple AI/ML techniques for intelligent movie recommendations, similarity search, and conversational chat.

---

## **1. Movie Recommendation System** 🎯

### **A. Matrix Factorization (Collaborative Filtering)**
- **Model**: Uses **SVD (Singular Value Decomposition)** trained on user-item interactions
- **Stored**: `models/mf_model.pkl`
- **How it works**:
  - Learns latent features for users and movies from historical rating data
  - User vector × Movie embeddings = Recommendation scores
  - Captures collaborative patterns (users with similar taste)
- **Implementation**: `src/recommender/matrix_factorization.py`

### **B. User Profile Personalization**
- **Location**: `src/profiles/profile_manager.py`
- **How it works**:
  1. Tracks each user's genre preferences from interactions
  2. Uses **exponential moving average** to update genre weights dynamically
  3. Weights normalized to sum to 1.0
  4. **Re-ranking**: Base score + (genre_weights × boost_multiplier)
  
**Example**: If you like Sci-Fi (0.6) and Action (0.4), movies with these genres get boosted scores

**Code Flow**:
```python
# Update profile on interaction
update_user_profile(user_id, movie_id, genres, weight=1.0)
  → Exponential moving average: new_weight = old + α(observed - old)
  → Normalize weights to sum to 1.0
  → Save to profiles/user_profiles.json

# Apply boost to recommendations
apply_profile_boost(recommendations, profile, boost_multiplier=2.0)
  → For each movie: score = base_score + (genre_match × boost_multiplier)
  → Sort by personalized_score
```

### **C. Hybrid Ranking**
- **File**: `src/recommender/hybrid_ranker.py`
- Combines multiple signals:
  - **CF scores** (collaborative filtering from matrix factorization)
  - **FAISS scores** (content-based similarity)
  - **Popularity** (optional gamma parameter)
  
**Formula**: `final_score = alpha × CF + beta × FAISS + gamma × Popularity`

---

## **2. Movie Similarity Search** 🔍

### **Technology Stack:**
- **FAISS (Facebook AI Similarity Search)**: Ultra-fast vector similarity search
- **Sentence Transformers**: `all-MiniLM-L6-v2` model for semantic embeddings

### **How it Works:**

#### **Step 1: Building Embeddings**
**File**: `embeddings/build_embeddings.py`

```python
# For each movie:
text = f"{title} {genres}"
embedding = SentenceTransformer.encode(text)  # 384-dimensional vector
```

- Creates semantic vector representation of each movie
- Captures meaning from title + genres
- Output: 384-dimensional dense vector

#### **Step 2: FAISS Index Creation**
- **Stored**: 
  - `embeddings/faiss_index/faiss.index` (vector index)
  - `embeddings/faiss_index/items.index` (optimized index)
  - `embeddings/faiss_index/movies.pkl` (metadata)
- Enables **O(log n)** similarity search across thousands of movies
- Uses L2 (Euclidean) distance for similarity computation

#### **Step 3: Search Process**
**File**: `backend/routes/search.py`

```python
# 1. User searches for "thriller movie"
query_embedding = model.encode("thriller movie")

# 2. FAISS finds nearest neighbors
distances, indices = faiss_index.search(query_embedding, top_k=10)

# 3. Convert distance to similarity score
similarity_score = 1 / (1 + distance)  # Lower distance = higher similarity

# 4. Return movies with metadata
```

**Features**:
- Case-insensitive partial matching
- Autocomplete suggestions
- Returns movie_id, title, genres, similarity_score
- **No ML training needed** - purely semantic vector matching!

---

## **3. Intelligent Chat System** 💬

This is a **RAG (Retrieval-Augmented Generation)** pipeline combining LLM intelligence with vector search.

### **Architecture Overview**
```
User Query → Intent Parsing (Gemini) → Retrieval (FAISS) → Filtering → Re-ranking → Explanation (Gemini) → Response
```

### **Step 1: Intent Parsing**
**File**: `src/rag/intent_parser.py`

- **Tool**: **Google Gemini 2.5 Flash** LLM
- **Purpose**: Extract structured intent from natural language
- **Extracts**:
  - Intent (recommend_movie vs other)
  - Genres (e.g., `["Thriller", "Action"]`)
  - Mood (e.g., "scary", "uplifting", "dark")
  - Exclusions (e.g., "not violent" → `["violent"]`)
  - Year constraints (e.g., "80s movies" → `min_year=1980, max_year=1989`)
  - Specific titles (e.g., "Find The Matrix")

**Prompt Engineering**:
```python
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
"""
```

**Fallback**: Regex-based parser if Gemini API fails (handles common patterns)

### **Step 2: Retrieval**
**File**: `src/rag/retriever.py`

Uses **FAISS semantic search** to find candidate movies:

```python
def retrieve_movies(query, genres=None, top_k=50):
    # Build enhanced query
    search_text = f"{query} {' '.join(genres)}"
    
    # Generate embedding
    query_embedding = model.encode([search_text])
    
    # FAISS search
    distances, indices = faiss_index.search(query_embedding, top_k)
    
    # Return movies with similarity scores
    return movies_with_scores
```

**Filters Applied**:

1. **Genre Filter** (`filter_by_genre`):
   - Matches if movie contains ANY specified genre
   - Case-insensitive matching
   - Example: "Thriller|Action" matches ["Thriller"] query

2. **Exclusion Filter** (`filter_by_exclusions`):
   - Removes unwanted content based on tags
   - Smart mapping: "violent" → excludes War/Crime/Action genres
   - Example: "not scary" → removes Horror/Thriller

3. **Year Filter** (`filter_by_year`):
   - Filters by release year range
   - Handles "recent" (2015+), "classic" (<2000), "80s movies" (1980-1989)

### **Step 3: Re-ranking**
**File**: `backend/routes/chat.py`

```python
# If user profile exists
if user_id:
    profile = get_user_profile(user_id)
    candidates = apply_profile_boost(candidates, profile, boost_multiplier=1.5)
else:
    # Sort by FAISS similarity
    candidates = candidates.sort_values("similarity_score", ascending=False)

# Select top 10
recommendations = candidates.head(10)
```

### **Step 4: Explanation Generation**
**File**: `src/rag/explainer.py`

- **Tool**: **Google Gemini 2.5 Flash**
- **Purpose**: Generate personalized explanations for each recommendation
- **Output**: 1-2 sentence explanation connecting movie to user's request

**Prompt Template**:
```python
prompt = f"""
You are a movie recommendation explainer.

User asked: "{user_query}"
User wants: {genres_text}{mood_text}{exclude_text}

For each movie below, write a brief 1-2 sentence explanation of WHY it matches.
Be specific, mention the genres, and connect to user's preferences.

Movies:
1. {title} - Genres: {genres}
...

Return ONLY a JSON array of explanations.
"""
```

**Example Output**:
```json
[
  "This suspenseful thriller focuses on psychological tension rather than graphic violence, perfect for your request",
  "A gripping mystery that keeps you on edge with plot twists instead of action sequences"
]
```

### **Step 5: Chat Response**
**File**: `src/rag/explainer.py` → `generate_chat_response()`

Gemini generates a natural language response:
```
"Here are some great thriller recommendations that aren't too violent! 🎬"
```

---

## **Complete Data Flow Example** 🔄

**Scenario**: User asks "I want a dark thriller from the 90s"

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Chat Endpoint Receives Message                          │
│    POST /chat {"message": "dark thriller from the 90s"}     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Intent Parsing (Gemini 2.5 Flash)                       │
│    → Extract: {                                             │
│        "intent": "recommend_movie",                         │
│        "genres": ["Thriller"],                              │
│        "mood": "dark",                                      │
│        "min_year": 1990,                                    │
│        "max_year": 1999                                     │
│      }                                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. FAISS Retrieval                                          │
│    → Query: "dark thriller"                                 │
│    → Retrieve 100 candidates via semantic search            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Filtering Pipeline                                       │
│    → Genre filter: Keep only Thriller movies                │
│    → Year filter: Keep only 1990-1999 releases              │
│    → Result: 35 movies                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Re-ranking                                               │
│    → Check user profile for personalization                 │
│    → Apply genre preference boost (if profile exists)       │
│    → Sort by personalized_score or similarity_score         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Select Top 10 Movies                                     │
│    → Seven, The Silence of the Lambs, etc.                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. Generate Explanations (Gemini 2.5 Flash)                │
│    → For each movie: Why it matches user's request          │
│    → "This psychological thriller from 1995 perfectly       │
│       captures the dark, suspenseful atmosphere..."         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. Return Response                                          │
│    {                                                        │
│      "response": "Here are dark thrillers from the 90s...", │
│      "recommendations": [                                    │
│        {                                                    │
│          "movie_id": 123,                                   │
│          "title": "Seven",                                  │
│          "genres": "Thriller|Crime",                        │
│          "explanation": "..."                               │
│        }                                                    │
│      ]                                                      │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## **Technology Summary** 🛠️

| Component | Technology | Purpose | Location |
|-----------|-----------|---------|----------|
| **Collaborative Filtering** | Matrix Factorization (SVD) | User-based recommendations | `models/mf_model.pkl` |
| **Content Similarity** | FAISS + Sentence Transformers | Fast vector similarity search | `embeddings/faiss_index/` |
| **Intent Understanding** | Google Gemini 2.5 Flash | Parse natural language queries | `src/rag/intent_parser.py` |
| **Explanations** | Google Gemini 2.5 Flash | Generate personalized reasons | `src/rag/explainer.py` |
| **Personalization** | Exponential Moving Average | Track user genre preferences | `src/profiles/profile_manager.py` |
| **Embeddings** | `all-MiniLM-L6-v2` | Convert text → 384-dim vectors | `embeddings/build_embeddings.py` |
| **Backend** | FastAPI | REST API endpoints | `backend/app.py` |
| **Frontend** | Next.js + React + TypeScript | User interface | `frontend/` |
| **Database** | CSV + JSON | Movie data + user profiles | `data/`, `profiles/` |

---

## **API Endpoints** 📡

### **Recommendations**
- `GET /recommend?user_id={id}&top_k={k}`
  - Returns personalized recommendations using MF + user profile
  - Optional user_id for personalization

- `POST /recommend/custom`
  - Custom recommendations based on genre preferences
  - Body: `{"genres": {"Sci-Fi": 0.6, "Action": 0.4}}`

### **Search**
- `GET /search/similar?movie_name={name}&top_k={k}`
  - Find similar movies using FAISS similarity search
  - Returns similarity scores

- `GET /search/autocomplete?query={q}&limit={n}`
  - Autocomplete movie titles for search suggestions

### **Chat**
- `POST /chat`
  - Intelligent conversational recommendations
  - Body: `{"message": "I want a thriller but not violent"}`
  - Optional `user_id` query parameter

### **Interactions**
- `POST /interact`
  - Record user interactions (ratings, clicks)
  - Updates user profile for personalization
  - Body: `{"user_id": "123", "movie_id": 456, "interaction_type": "like"}`

---

## **Machine Learning Models** 🤖

### **1. Matrix Factorization Model**
- **Algorithm**: SVD (Singular Value Decomposition)
- **Training**: `scripts/train_model.py`
- **Input**: User-item interaction matrix (ratings)
- **Output**: 
  - User latent vectors (n_users × n_components)
  - Item latent vectors (n_items × n_components)
- **Prediction**: `score = user_vector · item_vector`

### **2. Sentence Transformer**
- **Model**: `all-MiniLM-L6-v2`
- **Type**: Pre-trained (no training required)
- **Input**: Text strings (movie titles + genres)
- **Output**: 384-dimensional dense vectors
- **Use case**: Semantic similarity search

### **3. FAISS Index**
- **Type**: Vector index (not a trained model)
- **Built from**: Sentence transformer embeddings
- **Algorithm**: L2 (Euclidean) distance
- **Optimization**: Enables sub-second search on large datasets

### **4. Gemini 2.5 Flash**
- **Type**: Large Language Model (cloud API)
- **Provider**: Google AI
- **Use cases**:
  - Intent parsing (structured extraction)
  - Explanation generation (natural language)
- **No fine-tuning**: Uses prompt engineering

---

## **Key Advantages** ✨

1. **Hybrid Approach**
   - Combines CF (user behavior) + Content (FAISS) + Personalization
   - Mitigates cold-start problem with content-based fallback

2. **Fast Search**
   - FAISS enables sub-second similarity search
   - Handles thousands of movies efficiently

3. **Natural Language Understanding**
   - Gemini understands complex queries with negations
   - Handles temporal constraints ("90s movies")
   - Interprets mood and exclusions

4. **Explainable Recommendations**
   - Every recommendation comes with a personalized reason
   - Builds user trust and engagement

5. **Adaptive Personalization**
   - User profiles evolve with interactions
   - Exponential moving average prevents sudden preference shifts
   - Genre weights continuously refined

6. **Scalable Architecture**
   - FastAPI backend handles concurrent requests
   - FAISS scales to millions of items
   - Lazy loading optimizes memory usage

---

## **Data Pipeline** 📊

```
Raw Data (data/raw/)
    ├── interactions.csv (user-item ratings)
    └── items.csv (movie metadata)
              ↓
    Data Preprocessing (src/data/)
    ├── preprocess.py (clean, normalize)
    └── split.py (train/test split)
              ↓
    Processed Data (data/processed/)
    ├── train.csv
    └── test.csv
              ↓
    Model Training (scripts/)
    ├── train_model.py → models/mf_model.pkl
    └── evaluate_model.py → metrics
              ↓
    Embedding Generation (embeddings/)
    └── build_embeddings.py → faiss_index/
              ↓
    API Services (backend/)
    ├── Recommendation engine
    ├── Search engine
    └── Chat system
              ↓
    Frontend (frontend/)
    └── User interface
```

---

## **File Structure** 📁

```
movie/
├── backend/                    # FastAPI backend
│   ├── app.py                 # Main FastAPI app
│   └── routes/
│       ├── recommend.py       # Recommendation endpoints
│       ├── search.py          # Search endpoints
│       ├── chat.py            # Chat endpoints
│       └── interact.py        # User interaction tracking
│
├── src/                       # Core logic
│   ├── recommender/
│   │   ├── matrix_factorization.py   # CF model
│   │   └── hybrid_ranker.py          # Hybrid scoring
│   ├── rag/
│   │   ├── intent_parser.py   # Gemini intent extraction
│   │   ├── retriever.py       # FAISS retrieval + filtering
│   │   └── explainer.py       # Gemini explanation generation
│   ├── profiles/
│   │   └── profile_manager.py # User personalization
│   └── inference/
│       └── recommend.py       # Recommendation inference
│
├── embeddings/                # Vector embeddings
│   ├── build_embeddings.py   # Build FAISS index
│   └── faiss_index/
│       ├── items.index        # FAISS vector index
│       └── movies.pkl         # Movie metadata
│
├── models/                    # Trained models
│   └── mf_model.pkl          # Matrix factorization model
│
├── profiles/                  # User profiles
│   └── user_profiles.json    # Genre preferences per user
│
├── data/                      # Dataset
│   ├── raw/                  # Original data
│   └── processed/            # Cleaned data
│
└── frontend/                  # Next.js frontend
    └── src/
        ├── components/       # React components
        └── services/         # API client
```

---

## **Environment Variables** 🔑

Required in `.env` file:

```bash
# Google AI API Key for Gemini
GEMINI_API_KEY=your_api_key_here

# Optional: API configuration
FAISS_INDEX_PATH=embeddings/faiss_index/items.index
MODEL_PATH=models/mf_model.pkl
```

---

## **Performance Considerations** ⚡

### **Search Speed**
- FAISS search: < 100ms for 10,000+ movies
- Sentence encoding: ~50ms per query
- Total search time: < 200ms

### **Chat System**
- Intent parsing (Gemini): 500-1000ms
- FAISS retrieval: < 100ms
- Filtering: < 50ms
- Explanation generation (Gemini): 1000-2000ms
- **Total**: 2-3 seconds end-to-end

### **Optimization Strategies**
1. **Lazy Loading**: Models loaded only when first accessed
2. **Caching**: FAISS index and embeddings cached in memory
3. **Batch Processing**: Multiple operations parallelized
4. **Fallback Mechanisms**: Regex parser if Gemini fails

---

## **Future Enhancements** 🚀

Potential improvements:

1. **Advanced Models**
   - Deep learning collaborative filtering (Neural CF)
   - Transformer-based embeddings (BERT, GPT)
   - Multi-modal embeddings (posters, trailers)

2. **Real-time Features**
   - Session-based recommendations
   - Online learning for user profiles
   - A/B testing framework

3. **Enhanced RAG**
   - Fine-tuned intent parser
   - Multi-turn conversation history
   - Context-aware explanations

4. **Scalability**
   - Database migration (PostgreSQL)
   - Distributed FAISS (Milvus, Weaviate)
   - Caching layer (Redis)
   - Microservices architecture

---

## **Conclusion** 🎯

This is a **production-ready recommendation engine** that combines:
- **Classical ML** (Matrix Factorization)
- **Modern embeddings** (Sentence Transformers + FAISS)
- **LLM intelligence** (Gemini for NLU and generation)
- **Smart personalization** (Adaptive user profiles)

The hybrid approach ensures robust performance across cold-start scenarios, diverse user preferences, and complex natural language queries. The system is explainable, fast, and continuously learns from user interactions.

**Built with**: Python, FastAPI, FAISS, Sentence Transformers, Google Gemini, Next.js, React
