import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Movie {
  title: string;
  genres: string;
  explanation?: string;
}

export interface RecommendationResponse {
  user_id: number | null;
  recommendations: Movie[];
  profile_applied: boolean;
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

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  response: string;
  recommendations?: Movie[];
}

// Get recommendations for a specific user or anonymous
export const getRecommendations = async (
  userId?: number,
  topK: number = 5
): Promise<RecommendationResponse> => {
  try {
    const params: any = { top_k: topK };
    if (userId !== undefined) {
      params.user_id = userId;
    }
    
    const response = await axios.get(`${API_BASE_URL}/recommend`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching recommendations:', error);
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
  userId?: number
): Promise<ChatResponse> => {
  try {
    const params: any = {};
    if (userId !== undefined) {
      params.user_id = userId;
    }
    
    const response = await axios.post(
      `${API_BASE_URL}/chat`,
      { message },
      { params }
    );
    return response.data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};
