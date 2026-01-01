'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import Link from 'next/link';
import { searchSimilarMovies, getMovieAutocomplete, SimilarMovie, MovieSuggestion } from '../../services/api';

export default function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<MovieSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedMovie, setSelectedMovie] = useState<string | null>(null);
  const [similarMovies, setSimilarMovies] = useState<SimilarMovie[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [topK, setTopK] = useState(10);
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);

  // Debounced autocomplete function
  const fetchSuggestions = useCallback(async (query: string) => {
    if (query.length < 2) {
      setSuggestions([]);
      return;
    }

    try {
      const response = await getMovieAutocomplete(query, 10);
      setSuggestions(response.suggestions);
    } catch (err) {
      console.error('Error fetching suggestions:', err);
    }
  }, []);

  useEffect(() => {
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }
    
    debounceTimeout.current = setTimeout(() => {
      fetchSuggestions(searchQuery);
    }, 300);

    return () => {
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }
    };
  }, [searchQuery, fetchSuggestions]);

  const handleSearch = async (movieName: string) => {
    setLoading(true);
    setError(null);
    setSelectedMovie(movieName);
    setShowSuggestions(false);

    try {
      const response = await searchSimilarMovies(movieName, topK);
      setSimilarMovies(response.similar_movies);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to search for similar movies');
      setSimilarMovies([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: MovieSuggestion) => {
    setSearchQuery(suggestion.title);
    handleSearch(suggestion.title);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setShowSuggestions(true);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      handleSearch(searchQuery);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white">
      {/* Navigation Header */}
      <div className="bg-black/30 border-b border-purple-500/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold">Movie Similarity Search</h2>
            <div className="flex gap-3">
              <Link
                href="/"
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
              >
                🏠 Home
              </Link>
              <Link
                href="/chat"
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
              >
                💬 Chat
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <span className="text-6xl mr-3">✨</span>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Movie Similarity Search
            </h1>
          </div>
          <p className="text-gray-300 text-lg">
            Find movies similar to your favorites using AI-powered content analysis
          </p>
          <div className="mt-2 flex items-center justify-center gap-2 text-sm text-gray-400">
            <span>🎬</span>
            <span>Powered by FAISS Vector Search</span>
          </div>
        </div>

        {/* Search Bar */}
        <div className="max-w-3xl mx-auto mb-12">
          <div className="relative">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={handleInputChange}
                  onKeyPress={handleKeyPress}
                  onFocus={() => setShowSuggestions(true)}
                  placeholder="Enter a movie name (e.g., Avengers, Iron Man, The Matrix)..."
                  className="w-full px-6 py-4 bg-gray-800/50 border border-purple-500/30 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all"
                />
                <span className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400">🔍</span>
                
                {/* Autocomplete Suggestions */}
                {showSuggestions && suggestions.length > 0 && (
                  <div className="absolute z-10 w-full mt-2 bg-gray-800 border border-purple-500/30 rounded-xl shadow-2xl max-h-96 overflow-y-auto">
                    {suggestions.map((suggestion) => (
                      <button
                        key={suggestion.movie_id}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="w-full px-6 py-3 text-left hover:bg-purple-600/20 transition-colors border-b border-gray-700 last:border-b-0"
                      >
                        <div className="font-medium text-white">{suggestion.title}</div>
                        <div className="text-sm text-gray-400">{suggestion.genres}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              
              <button
                onClick={() => handleSearch(searchQuery)}
                disabled={!searchQuery.trim() || loading}
                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-purple-500/50"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>

            {/* Results Count Selector */}
            <div className="mt-4 flex items-center gap-3">
              <label className="text-sm text-gray-400">Results to show:</label>
              <select
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="px-3 py-2 bg-gray-800/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:border-purple-500"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={15}>15</option>
                <option value={20}>20</option>
              </select>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-3xl mx-auto mb-8 p-4 bg-red-900/30 border border-red-500/50 rounded-xl text-red-200">
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-500"></div>
          </div>
        )}

        {/* Results */}
        {!loading && selectedMovie && similarMovies.length > 0 && (
          <div className="max-w-7xl mx-auto">
            <div className="mb-8 p-6 bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-xl border border-purple-500/30">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl">📈</span>
                <h2 className="text-2xl font-bold">
                  Movies Similar to: <span className="text-purple-400">{selectedMovie}</span>
                </h2>
              </div>
              <p className="text-gray-300">
                Found {similarMovies.length} similar movies based on plot, genres, themes, and style
              </p>
            </div>

            {/* Similar Movies Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {similarMovies.map((movie, index) => (
                <div
                  key={movie.movie_id}
                  className="bg-gradient-to-br from-gray-800/80 to-purple-900/30 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6 hover:border-purple-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-purple-500/20 hover:-translate-y-1"
                >
                  {/* Rank Badge */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="bg-purple-600 text-white rounded-full w-10 h-10 flex items-center justify-center font-bold text-lg">
                      {index + 1}
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-400 mb-1">Similarity</div>
                      <div className="flex items-center gap-1">
                        <div className="w-20 bg-gray-700 rounded-full h-2 overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-purple-500 to-pink-500 h-full rounded-full transition-all"
                            style={{ width: `${movie.similarity_score * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-semibold text-purple-400">
                          {(movie.similarity_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Movie Info */}
                  <div className="mb-4">
                    <h3 className="text-xl font-bold text-white mb-2 line-clamp-2">
                      {movie.title}
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {movie.genres.split('|').map((genre, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-purple-600/30 text-purple-200 rounded-full text-xs font-medium"
                        >
                          {genre.trim()}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Movie ID */}
                  <div className="text-xs text-gray-500 mt-2">
                    ID: {movie.movie_id}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !selectedMovie && (
          <div className="text-center py-20">
            <div className="text-8xl mb-6">🎬</div>
            <h3 className="text-2xl font-semibold text-gray-400 mb-2">
              Search for Similar Movies
            </h3>
            <p className="text-gray-500">
              Enter a movie name above to discover similar films
            </p>
          </div>
        )}

        {/* How it Works */}
        <div className="max-w-4xl mx-auto mt-20 p-8 bg-gray-800/30 rounded-xl border border-gray-700">
          <h3 className="text-2xl font-bold mb-6 text-center">How It Works</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                1
              </div>
              <h4 className="font-semibold mb-2">Find Movie</h4>
              <p className="text-sm text-gray-400">Search for a movie by name</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                2
              </div>
              <h4 className="font-semibold mb-2">Get Embedding</h4>
              <p className="text-sm text-gray-400">Extract movie's vector representation</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                3
              </div>
              <h4 className="font-semibold mb-2">FAISS Search</h4>
              <p className="text-sm text-gray-400">Find nearest neighbors in vector space</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                4
              </div>
              <h4 className="font-semibold mb-2">Return Results</h4>
              <p className="text-sm text-gray-400">Show similar movies with scores</p>
            </div>
          </div>
          <div className="mt-8 p-4 bg-purple-900/20 rounded-lg border border-purple-500/20">
            <p className="text-sm text-gray-300 text-center">
              <strong>Content-Based Recommendation:</strong> Uses plot, genres, keywords, and themes. 
              No LLM required - pure vector similarity search powered by FAISS.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
