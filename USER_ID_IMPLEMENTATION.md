# User ID System Implementation

## Overview
This implementation adds a persistent user ID system with profile-based personalization and popularity-based fallback for new users.

## Features

### 1️⃣ Frontend: User ID Generation & Persistence

**Location**: [frontend/src/services/api.ts](frontend/src/services/api.ts)

**Implementation**:
- `getUserId()`: Gets or generates a user ID from localStorage
- User ID format: `user_<timestamp>_<random>`
- Persists across page refreshes using localStorage
- Automatically generated on first visit

**Usage**:
```typescript
import { getUserId } from '@/services/api';

const userId = getUserId(); // Returns existing or generates new
```

### 2️⃣ Frontend: Automatic User ID in API Requests

All API calls automatically include the user ID:

#### Recommendations
```typescript
getRecommendations(userId?, topK?) 
// Uses provided userId or calls getUserId() automatically
```

#### Chat
```typescript
sendChatMessage(message, userId?)
// Uses provided userId or calls getUserId() automatically
```

#### Feedback/Interactions
```typescript
trackInteraction(userId, movieId, genres)
// Uses provided userId or calls getUserId() automatically
```

### 3️⃣ Backend: Profile Management

**Location**: [src/profiles/profile_manager.py](src/profiles/profile_manager.py)

**Functions**:
- `get_user_profile(user_id)`: Load user profile from storage
- `update_user_profile(user_id, movie_id, genres)`: Track interactions and update profile
- `apply_profile_boost(recommendations, profile)`: Re-rank recommendations using user preferences

**Profile Structure**:
```json
{
  "user_id_123": {
    "genre_weights": {
      "Sci-Fi": 0.45,
      "Action": 0.35,
      "Adventure": 0.20
    },
    "interaction_count": 5,
    "last_interaction": {
      "movie_id": 260,
      "genres": ["Sci-Fi", "Action"]
    }
  }
}
```

### 4️⃣ Backend: Personalized vs Popularity Fallback

**Location**: [backend/routes/recommend.py](backend/routes/recommend.py)

**Logic Flow**:
```
1. Receive user_id from request
2. Try to load user profile
3. If profile exists and has genre_weights:
   ✅ Use Matrix Factorization + Profile Boost (Personalized)
4. If no profile:
   🆕 Use Popularity-based recommendations (Fallback)
```

**Popularity Fallback**: [src/recommender/popularity.py](src/recommender/popularity.py)
- Recommends movies based on interaction count
- Used for new users without preference history
- Provides consistent baseline experience

### 5️⃣ Backend Endpoints

#### `/recommend` - Get Recommendations
```python
GET /recommend?user_id=user_123&top_k=5

Response:
{
  "user_id": "user_123",
  "recommendations": [...],
  "personalized": true,  # false for new users
  "profile": {"Sci-Fi": 0.6, "Action": 0.4}  # null for new users
}
```

#### `/interact` - Track Interaction
```python
POST /interact
{
  "user_id": "user_123",
  "movie_id": 260,
  "genres": ["Sci-Fi", "Action"]
}

Response:
{
  "success": true,
  "user_id": "user_123",
  "updated_profile": {
    "genre_weights": {...},
    "interaction_count": 5
  }
}
```

#### `/chat` - Chat with Personalization
```python
POST /chat?user_id=user_123
{
  "message": "I want a sci-fi movie"
}

Response:
{
  "response": "Here are some great sci-fi movies...",
  "recommendations": [...]
}
```

## User Journey

### New User (No Profile)
1. Visit website → user_id generated (e.g., `user_1704124800_abc123`)
2. Request recommendations → receives **popularity-based** recommendations
3. Click on movies → interactions tracked, profile created
4. After 1+ interactions → starts receiving **personalized** recommendations

### Returning User (Has Profile)
1. Visit website → same user_id loaded from localStorage
2. Request recommendations → receives **personalized** recommendations based on profile
3. Click on movies → profile continues to update with exponential moving average

## Testing

Run the test suite:
```bash
python test_user_id_system.py
```

Tests verify:
- ✅ New users get popularity recommendations
- ✅ Interactions create and update profiles
- ✅ Existing users get personalized recommendations
- ✅ Profiles persist across requests
- ✅ All endpoints accept and use user_id

## File Changes Summary

### Frontend
- ✅ `frontend/src/services/api.ts` - Added getUserId(), updated all API calls
- ✅ `frontend/src/app/page.tsx` - Auto-load user_id on mount, display in UI
- ✅ `frontend/src/app/chat/page.tsx` - Auto-load user_id on mount, display in UI
- ✅ `frontend/src/components/RecommendationCard.tsx` - Already passing user_id correctly

### Backend
- ✅ `backend/routes/recommend.py` - Added popularity fallback logic
- ✅ `backend/routes/chat.py` - Already accepts user_id (no changes needed)
- ✅ `backend/routes/interact.py` - Already accepts user_id (no changes needed)
- ✅ `src/recommender/popularity.py` - Created popularity recommender
- ✅ `src/profiles/profile_manager.py` - Already has profile management (no changes needed)

## Benefits

1. **Seamless Experience**: Users don't need to create accounts
2. **Persistent Preferences**: User preferences saved across sessions
3. **Progressive Personalization**: Recommendations improve as users interact
4. **Graceful Degradation**: New users still get quality recommendations via popularity
5. **Privacy-Friendly**: No personal data required, just anonymous IDs

## Next Steps (Optional Enhancements)

- 📊 Add analytics dashboard showing user profiles
- 🔄 Implement profile merging for users who want to claim their profile
- 🧹 Add profile cleanup for inactive users
- 📱 Add user_id to URL for sharing preferences
- 🎯 Implement A/B testing for different boost multipliers
