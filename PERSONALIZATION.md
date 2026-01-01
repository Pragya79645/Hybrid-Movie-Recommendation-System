# Personalization Feature 🎯

## Overview
The recommendation system now includes **truly personalized recommendations** based on user interactions. Each user gets different results for the same genre based on their viewing preferences.

## How It Works

### 1. User Interaction Tracking
When a user clicks on any movie card, the system automatically tracks their interaction:
- **Endpoint**: `POST /interact`
- **Data Tracked**: `user_id`, `movie_id`, `genres`
- **Storage**: `profiles/user_profiles.json` (no database needed)

### 2. Dynamic Profile Building
Each user has a profile that evolves based on their interactions:
```json
{
  "user123": {
    "genre_weights": {
      "Thriller": 0.45,
      "Crime": 0.35,
      "Drama": 0.20
    },
    "interaction_count": 15,
    "last_interaction": {
      "movie_id": 23,
      "genres": ["Thriller", "Crime"]
    }
  }
}
```

### 3. Personalized Scoring
Recommendations are re-ranked using:
```
personalized_score = base_score + (user_genre_weight × boost_multiplier)
```

Where:
- `base_score` = 1.0 (from collaborative filtering)
- `user_genre_weight` = sum of weights for movie's genres
- `boost_multiplier` = 2.0 (configurable)

### 4. Adaptive Learning
- Uses **exponential moving average** for genre weights
- Learning rate decreases as user has more interactions
- Prevents old preferences from being overwritten too quickly

## API Usage

### Track Interaction
```bash
POST http://localhost:8000/interact
Content-Type: application/json

{
  "user_id": "user123",
  "movie_id": 23,
  "genres": ["Thriller", "Crime"]
}
```

Response:
```json
{
  "success": true,
  "user_id": "user123",
  "updated_profile": {
    "genre_weights": {...},
    "interaction_count": 16
  }
}
```

### Get Personalized Recommendations
```bash
GET http://localhost:8000/recommend?user_id=user123&top_k=10
```

Response:
```json
{
  "user_id": "user123",
  "recommendations": [
    {
      "movie_id": 45,
      "title": "The Departed",
      "genres": "Crime|Thriller|Drama"
    }
  ],
  "personalized": true,
  "profile": {
    "Thriller": 0.45,
    "Crime": 0.35,
    "Drama": 0.20
  }
}
```

## Frontend Integration

### Automatic Tracking
Movie cards automatically track clicks when:
- User ID is provided
- Movie ID is available
- User clicks on any recommendation card

```tsx
<RecommendationCard 
  movie={movie}
  userId="user123"
  movieId={movie.movie_id}
/>
```

### User ID Input
Both pages include a User ID input field:
- **Home Page**: Browse recommendations
- **Chat Page**: Conversational recommendations

Users can enter any string as their ID (e.g., "user123", "alice", "bob")

## Benefits

✅ **Truly Personalized**: Same button, different results per user  
✅ **No Database**: Simple JSON file storage  
✅ **Real-time**: Immediate profile updates after interactions  
✅ **Adaptive**: Learning rate adjusts based on interaction count  
✅ **Privacy-Friendly**: User controls their ID  

## Example Scenario

**User "alice"**:
1. Clicks on "Inception" (Sci-Fi, Thriller)
2. Clicks on "The Matrix" (Sci-Fi, Action)
3. Clicks on "Interstellar" (Sci-Fi, Drama)

Her profile now heavily weights Sci-Fi → future recommendations favor Sci-Fi movies

**User "bob"**:
1. Clicks on "The Godfather" (Crime, Drama)
2. Clicks on "Goodfellas" (Crime, Drama)
3. Clicks on "Casino" (Crime, Drama)

His profile now heavily weights Crime/Drama → future recommendations favor Crime/Drama movies

**Result**: Clicking the same "Get Recommendations" button shows completely different results!

## Configuration

Adjust personalization behavior in [profile_manager.py](src/profiles/profile_manager.py):

```python
# Learning rate for new interactions
alpha = 0.3 if interaction_count < 10 else 0.1

# Boost multiplier for genre preferences
boost_multiplier = 2.0
```

## Files Modified

### Backend
- ✅ `backend/routes/interact.py` - New interaction endpoint
- ✅ `backend/app.py` - Register interact router
- ✅ `backend/routes/recommend.py` - Use personalized scoring
- ✅ `src/profiles/profile_manager.py` - Enhanced profile management
- ✅ `src/inference/recommend.py` - Include movie_id in responses

### Frontend
- ✅ `frontend/src/services/api.ts` - New trackInteraction function
- ✅ `frontend/src/components/RecommendationCard.tsx` - Click tracking
- ✅ `frontend/src/app/page.tsx` - Pass userId and movieId
- ✅ `frontend/src/app/chat/page.tsx` - String userId support
- ✅ `frontend/src/components/ChatBox.tsx` - String userId support

## Next Steps

🚀 **Potential Enhancements**:
- Add click-through rate tracking
- Implement time decay for old interactions
- Add explicit rating system (thumbs up/down)
- Visualize user profile in UI
- Export/import user profiles
- A/B testing for different boost multipliers
