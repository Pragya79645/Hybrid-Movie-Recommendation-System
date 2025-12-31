import React, { useState } from 'react';

interface PreferenceFormProps {
  onSubmit: (preferences: { genres: Record<string, number> }) => void;
  onSkip: () => void;
}

const AVAILABLE_GENRES = [
  'Action',
  'Adventure',
  'Animation',
  'Comedy',
  'Crime',
  'Documentary',
  'Drama',
  'Family',
  'Fantasy',
  'Horror',
  'Mystery',
  'Romance',
  'Sci-Fi',
  'Thriller',
  'Western'
];

export default function PreferenceForm({ onSubmit, onSkip }: PreferenceFormProps) {
  const [selectedGenres, setSelectedGenres] = useState<Record<string, number>>({});

  const handleGenreClick = (genre: string) => {
    setSelectedGenres(prev => {
      const current = prev[genre] || 0;
      if (current === 0) {
        return { ...prev, [genre]: 1.0 };
      } else if (current === 1.0) {
        return { ...prev, [genre]: 0.5 };
      } else {
        const { [genre]: _, ...rest } = prev;
        return rest;
      }
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (Object.keys(selectedGenres).length > 0) {
      onSubmit({ genres: selectedGenres });
    }
  };

  const getGenreButtonClass = (genre: string) => {
    const weight = selectedGenres[genre];
    if (weight === 1.0) {
      return 'bg-blue-600 text-white border-blue-600';
    } else if (weight === 0.5) {
      return 'bg-blue-300 text-white border-blue-300';
    }
    return 'bg-white text-gray-700 border-gray-300 hover:border-blue-400';
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">
        What genres do you like?
      </h2>
      <p className="text-gray-600 mb-6">
        Click once for strong preference, twice for moderate, three times to deselect.
      </p>
      
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mb-6">
          {AVAILABLE_GENRES.map(genre => (
            <button
              key={genre}
              type="button"
              onClick={() => handleGenreClick(genre)}
              className={`px-4 py-3 rounded-lg border-2 font-medium transition-all duration-200 ${getGenreButtonClass(genre)}`}
            >
              {genre}
              {selectedGenres[genre] === 1.0 && ' ❤️'}
              {selectedGenres[genre] === 0.5 && ' 👍'}
            </button>
          ))}
        </div>

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={Object.keys(selectedGenres).length === 0}
            className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Get Recommendations ({Object.keys(selectedGenres).length} genres selected)
          </button>
          <button
            type="button"
            onClick={onSkip}
            className="px-6 py-3 rounded-lg border-2 border-gray-300 text-gray-700 font-semibold hover:bg-gray-50 transition-colors"
          >
            Skip
          </button>
        </div>
      </form>

      {Object.keys(selectedGenres).length > 0 && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-2">Your Preferences:</h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(selectedGenres).map(([genre, weight]) => (
              <span
                key={genre}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {genre} {weight === 1.0 ? '(Strong)' : '(Moderate)'}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
