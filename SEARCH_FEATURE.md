# Movie Similarity Search Feature

## Overview
This feature allows users to search for similar movies based on content similarity using FAISS vector search. It's a content-based recommendation system that doesn't require any LLM or chat logic.

## How It Works

### Flow
1. **User Input**: User types a movie name (e.g., "Avengers")
2. **Movie Lookup**: Backend finds the movie_id for the given title
3. **Embedding Retrieval**: Get the movie's embedding vector
4. **FAISS Search**: Perform similarity search to find top K nearest neighbors
5. **Return Results**: Return similar movies with metadata (title, genres, similarity score)

### Technology Stack
- **FAISS**: Fast similarity search using vector embeddings
- **SentenceTransformers**: `all-MiniLM-L6-v2` model for encoding text
- **No LLM Required**: Pure vector similarity search

### What Powers This?
✅ FAISS index for fast similarity search  
✅ Movie embeddings (based on title + genres)  
✅ Content-based filtering  
❌ No LLM (Gemini/GPT) required  
❌ No chat logic needed  

## Files Created

### Backend
1. **`backend/routes/search.py`**
   - `/search/similar` - Main similarity search endpoint
   - `/search/autocomplete` - Movie title autocomplete

### Frontend
1. **`frontend/src/app/search/page.tsx`**
   - Search interface with autocomplete
   - Results display with similarity scores
   - Responsive design

### API Updates
1. **`frontend/src/services/api.ts`**
   - Added `searchSimilarMovies()` function
   - Added `getMovieAutocomplete()` function
   - TypeScript interfaces for responses

## API Endpoints

### Search Similar Movies
```http
GET /search/similar?movie_name=Avengers&top_k=10
```

**Parameters:**
- `movie_name` (required): Name of the movie to search for
- `top_k` (optional, default=10): Number of similar movies to return (1-50)

**Response:**
```json
{
  "query_movie": "The Avengers",
  "similar_movies": [
    {
      "movie_id": 123,
      "title": "Iron Man",
      "genres": "Action|Adventure|Sci-Fi",
      "similarity_score": 0.8523
    },
    ...
  ],
  "total_results": 10
}
```

### Autocomplete
```http
GET /search/autocomplete?query=Aven&limit=10
```

**Parameters:**
- `query` (required): Partial movie title
- `limit` (optional, default=10): Maximum suggestions (1-20)

**Response:**
```json
{
  "query": "Aven",
  "suggestions": [
    {
      "movie_id": 1,
      "title": "The Avengers",
      "genres": "Action|Adventure|Sci-Fi"
    },
    ...
  ],
  "count": 5
}
```

## Embeddings

### What Embeddings Are Used?
The same embeddings built in Colab, based on:
- **Title**: Movie title
- **Genres**: Genre information
- (Can be extended to include: Overview/plot, Keywords, Tags)

### Files Required
Located in `embeddings/faiss_index/`:
- **`items.index`**: FAISS index file
- **`movies.pkl`**: Movie metadata (DataFrame with movie_id, title, genres)

## Usage

### Backend
1. Make sure embeddings are built:
   ```bash
   python embeddings/build_embeddings.py
   ```

2. Start the backend:
   ```bash
   uvicorn backend.app:app --reload
   ```

### Frontend
1. Navigate to the search page:
   ```
   http://localhost:3000/search
   ```

2. Type a movie name (autocomplete will help)

3. Click "Search" to see similar movies

## Features

### 1. Autocomplete
- Real-time movie title suggestions
- Debounced API calls (300ms)
- Shows title + genres for each suggestion

### 2. Similarity Search
- Vector-based similarity using L2 distance
- Configurable number of results (5, 10, 15, 20)
- Similarity scores (0-100%)
- Genre badges for each result

### 3. UI/UX
- Modern gradient design
- Responsive grid layout
- Loading states
- Error handling
- Visual similarity score bars

## Navigation
The search page is integrated with the main application:
- **Home** → Search Movies button
- **Chat** → Search Movies button
- **Search** → Home and Chat buttons

## Technical Details

### Similarity Calculation
1. Convert L2 distance to similarity score:
   ```python
   similarity_score = 1 / (1 + distance)
   ```
2. Higher score = more similar (range: 0-1)
3. Displayed as percentage in UI

### Performance
- FAISS IndexFlatL2 for exact nearest neighbor search
- Fast lookups even with large movie databases
- Autocomplete debouncing reduces API calls

## Example Queries

**Try searching for:**
- "Avengers" → Find Marvel movies
- "Matrix" → Find sci-fi action movies
- "Toy Story" → Find animated family movies
- "Dark Knight" → Find superhero/crime movies

## Future Enhancements

Potential improvements:
- [ ] Add movie posters/images
- [ ] Include plot/overview in embeddings
- [ ] Add filtering by genre, year, rating
- [ ] Save search history
- [ ] "More like this" button on results
- [ ] Export/share similar movie lists
