# Movie Recommendation System

## What this project does
This project helps users discover relevant movies through a hybrid recommendation engine, fast semantic similarity search, and a conversational RAG chat assistant. It combines collaborative filtering, vector search, and LLM-based intent parsing to return personalized and explainable results.

## Problem it solves
Finding the right movie is hard when preferences are fuzzy (genre, mood, era). This system interprets user intent, finds semantically similar titles, and re-ranks results based on user profiles and behavior to deliver more relevant recommendations.

## Technical approach
- Hybrid recommender: matrix factorization (collaborative filtering) + FAISS semantic similarity + optional popularity weighting.
- User profile personalization: genre preference tracking with exponential moving averages for re-ranking.
- RAG chat: intent parsing (Gemini) -> FAISS retrieval -> filtering (genre/exclusion/year) -> explanation generation.
- API + UI: FastAPI backend with Next.js (TypeScript) frontend.

## Repository layout
- backend/: FastAPI app and API routes.
- frontend/: Next.js app (UI).
- src/: ML and RAG logic (profiles, retriever, intent parser, explainer).
- embeddings/: FAISS index and embedding utilities.
- data/: raw and processed datasets.
- profiles/: stored user profiles.

## Setup

### Prerequisites
- Python 3.10+ (recommended)
- Node.js 18+
- pnpm (or npm if you prefer)

### 1) Backend setup
1. Create and activate a Python virtual environment (name it however you like).
2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Start the API server from the repository root:

```bash
python -m uvicorn backend.app:app --reload --port 8000
```

### 2) Frontend setup
1. Install dependencies:

```bash
cd frontend
pnpm install
```

2. Start the UI:

```bash
pnpm dev
```

3. Open http://localhost:3000

## Environment variables (.env files)

### Root .env (backend)
Create a .env file in the repository root (same level as backend/ and frontend/). You can copy from .env.example and replace the value:

- .env.example -> .env
- Required:
  - GEMINI_API_KEY=your_api_key_here

The backend loads this using python-dotenv.

### Frontend .env.local
Create frontend/.env.local with the backend base URL:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Key API endpoints
- GET /recommend?user_id=...&top_k=... : personalized or fallback recommendations.
- POST /recommend/custom : recommendations from custom preferences.
- POST /chat : RAG-based conversational recommendations.
- GET /search/similar?movie_name=... : semantic similarity search.

## Notes
- If FAISS indices are missing, rebuild embeddings with:

```bash
python embeddings/build_embeddings.py
```

- User profiles are stored in profiles/user_profiles.json.

## Troubleshooting
- Ensure the backend is running on http://localhost:8000 before starting the frontend.
- If LLM features fail, confirm GEMINI_API_KEY is set in the root .env file.
