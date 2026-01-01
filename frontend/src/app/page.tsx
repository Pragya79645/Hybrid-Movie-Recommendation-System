'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import PreferenceForm from '@/components/PreferenceForm';
import RecommendationCard from '@/components/RecommendationCard';
import { getRecommendations, getCustomRecommendations, Movie, getUserId } from '@/services/api';

export default function Home() {
  const [showPreferences, setShowPreferences] = useState(true);
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<Movie[]>([]);
  const [userId, setUserId] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  // Initialize user ID on component mount
  useEffect(() => {
    const id = getUserId();
    setUserId(id);
  }, []);

  const fetchRecommendations = async (preferences?: { genres: Record<string, number> }) => {
    setLoading(true);
    setError(null);
    
    try {
      let response;
      
      if (preferences && preferences.genres) {
        // Get custom recommendations based on preferences
        response = await getCustomRecommendations(preferences, 20);
        setRecommendations(response.recommendations);
      } else {
        // Get recommendations for user (getUserId is called automatically in the API)
        response = await getRecommendations(userId, 20);
        setRecommendations(response.recommendations);
      }
      
      setShowPreferences(false);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError('Failed to fetch recommendations. Please make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handlePreferenceSubmit = (preferences: { genres: Record<string, number> }) => {
    fetchRecommendations(preferences);
  };

  const handleSkip = () => {
    fetchRecommendations();
  };

  const handleReset = () => {
    setShowPreferences(true);
    setRecommendations([]);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🎬 Movie Recommendations
              </h1>
              <p className="text-gray-600 mt-1">
                Discover your next favorite movie
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 rounded-lg border border-gray-200">
                <span className="text-sm font-medium text-gray-700">
                  User ID:
                </span>
                <span className="text-sm text-gray-900 font-mono">
                  {userId || 'Loading...'}
                </span>
              </div>
              <Link
                href="/search"
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                🔍 Search Movies
              </Link>
              <Link
                href="/chat"
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
              >
                💬 Chat Assistant
              </Link>
              {!showPreferences && (
                <button
                  onClick={handleReset}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
                >
                  Reset
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <svg
                className="w-5 h-5 text-red-600 mr-3"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {showPreferences ? (
          <PreferenceForm onSubmit={handlePreferenceSubmit} onSkip={handleSkip} />
        ) : loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600 text-lg">Finding perfect movies for you...</p>
            </div>
          </div>
        ) : (
          <div>
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Your Personalized Recommendations
              </h2>
              <p className="text-gray-600">
                {recommendations.length} movies tailored just for you
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recommendations.map((movie, index) => (
                <RecommendationCard
                  key={`${movie.title}-${index}`}
                  movie={movie}
                  rank={index + 1}
                  userId={userId}
                  movieId={movie.movie_id}
                />
              ))}
            </div>

            {recommendations.length === 0 && !loading && (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">
                  No recommendations found. Try adjusting your preferences.
                </p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-600">
            Powered by collaborative filtering and RAG technology
          </p>
        </div>
      </footer>
    </div>
  );
}
