import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// User ID Management
const USER_ID_KEY = 'movie_app_user_id';

/**
 * Generate a unique user ID
 */
const generateUserId = (): string => {
  return `user_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
};

/**
 * Get or create user ID from localStorage
 * This ensures the user ID persists across page refreshes
 */
export const getUserId = (): string => {
  if (typeof window === 'undefined') {
    // Server-side rendering fallback
    return generateUserId();
  }
  
  let userId = localStorage.getItem(USER_ID_KEY);
  
  if (!userId) {
    userId = generateUserId();
    localStorage.setItem(USER_ID_KEY, userId);
    console.log('✨ Generated new user ID:', userId);
  } else {
    console.log('👤 Using existing user ID:', userId);
  }
  
  return userId;
};

/**
 * Clear user ID (for testing/logout)
 */
export const clearUserId = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(USER_ID_KEY);
  }
};

export interface Movie {
  movie_id: number;
  title: string;
  genres: string;
  explanation?: string;
}

export interface RecommendationResponse {
  user_id: string | null;
  recommendations: Movie[];
  personalized: boolean;
  profile?: Record<string, number>;
}

export interface CustomPreferences {
  liked_movies?: number[];
  genres?: Record<string, number>;
}

export interface CustomRecommendationResponse {
  recommendations: Movie[];
  custom_profile?: Record<string, number>;
}

export interface InteractionRequest {
  user_id: string;
  movie_id: number;
  genres: string[];
}

export interface InteractionResponse {
  success: boolean;
  user_id: string;
  updated_profile: {
    genre_weights: Record<string, number>;
    interaction_count: number;
  };
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  response: string;
  recommendations?: Movie[];
}

export interface SimilarMovie {
  movie_id: number;
  title: string;
  genres: string;
  similarity_score: number;
}

export interface SearchResponse {
  query_movie: string;
  similar_movies: SimilarMovie[];
  total_results: number;
}

export interface MovieSuggestion {
  movie_id: number;
  title: string;
  genres: string;
}

export interface AutocompleteResponse {
  query: string;
  suggestions: MovieSuggestion[];
  count: number;
}

// Get recommendations for a specific user or anonymous
export const getRecommendations = async (
  userId?: string,
  topK: number = 5
): Promise<RecommendationResponse> => {
  try {
    // Always use a user ID (either provided or from localStorage)
    const effectiveUserId = userId || getUserId();
    
    const response = await axios.get(`${API_BASE_URL}/recommend`, {
      params: {
        top_k: topK,
        user_id: effectiveUserId
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    throw error;
  }
};

// Track user interaction with a movie
export const trackInteraction = async (
  userId: string | undefined,
  movieId: number,
  genres: string[]
): Promise<InteractionResponse> => {
  try {
    // Always use a user ID (either provided or from localStorage)
    const effectiveUserId = userId || getUserId();
    
    const response = await axios.post(`${API_BASE_URL}/interact`, {
      user_id: effectiveUserId,
      movie_id: movieId,
      genres: genres
    });
    return response.data;
  } catch (error) {
    console.error('Error tracking interaction:', error);
    throw error;
  }
};

// Get recommendations based on custom preferences
export const getCustomRecommendations = async (
  preferences: CustomPreferences,
  topK: number = 5
): Promise<CustomRecommendationResponse> => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/recommend/custom`,
      preferences,
      { params: { top_k: topK } }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching custom recommendations:', error);
    throw error;
  }
};

// Send chat message and get response
export const sendChatMessage = async (
  message: string,
  userId?: string
): Promise<ChatResponse> => {
  try {
    // Always use a user ID (either provided or from localStorage)
    const effectiveUserId = userId || getUserId();
    
    const response = await axios.post(
      `${API_BASE_URL}/chat`,
      { message },
      { params: { user_id: effectiveUserId } }
    );
    return response.data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

// Search for similar movies using FAISS
export const searchSimilarMovies = async (
  movieName: string,
  topK: number = 10
): Promise<SearchResponse> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/search/similar`, {
      params: { movie_name: movieName, top_k: topK }
    });
    return response.data;
  } catch (error) {
    console.error('Error searching for similar movies:', error);
    throw error;
  }
};

// Get autocomplete suggestions for movie titles
export const getMovieAutocomplete = async (
  query: string,
  limit: number = 10
): Promise<AutocompleteResponse> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/search/autocomplete`, {
      params: { query, limit }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching autocomplete suggestions:', error);
    throw error;
  }
};
