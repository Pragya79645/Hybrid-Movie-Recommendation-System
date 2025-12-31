import React from 'react';
import { Movie } from '@/services/api';

interface RecommendationCardProps {
  movie: Movie;
  rank?: number;
}

export default function RecommendationCard({ movie, rank }: RecommendationCardProps) {
  const genres = movie.genres ? movie.genres.split('|').filter(g => g.trim()) : [];

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 p-6 border border-gray-200">
      {rank && (
        <div className="flex items-center justify-between mb-3">
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white font-bold text-sm">
            #{rank}
          </span>
        </div>
      )}
      
      <h3 className="text-xl font-bold text-gray-800 mb-3 line-clamp-2">
        {movie.title}
      </h3>

      <div className="mb-4">
        <div className="flex flex-wrap gap-2">
          {genres.map((genre, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 rounded-full text-sm font-medium"
            >
              {genre.trim()}
            </span>
          ))}
        </div>
      </div>

      {movie.explanation && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
            <svg 
              className="w-4 h-4 mr-2" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
              />
            </svg>
            Why this recommendation?
          </h4>
          <p className="text-sm text-gray-600 leading-relaxed">
            {movie.explanation}
          </p>
        </div>
      )}
    </div>
  );
}
