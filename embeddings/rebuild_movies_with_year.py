"""
Rebuild movies.pkl to include a year column extracted from the title.
This fixes the year filtering issue in recommendations.
"""
import joblib
import pandas as pd
import re

# Load the current movies dataframe
movies = joblib.load("embeddings/faiss_index/movies.pkl")

print(f"Original DataFrame shape: {movies.shape}")
print(f"Original columns: {movies.columns.tolist()}")

# Extract year from title using regex
# Titles are in format: "Movie Title (YYYY)"
def extract_year(title):
    """Extract year from title in format 'Movie Title (YYYY)'"""
    if pd.isna(title):
        return None
    
    match = re.search(r'\((\d{4})\)', str(title))
    if match:
        return int(match.group(1))
    return None

# Add year column
movies['year'] = movies['title'].apply(extract_year)

# Convert to int, handling NaN values
# Movies without years will be kept but won't match year filters
print(f"\nYear extraction results:")
print(f"  Total movies: {len(movies)}")
print(f"  Movies with year: {movies['year'].notna().sum()}")
print(f"  Movies without year: {movies['year'].isna().sum()}")

if movies['year'].notna().any():
    print(f"  Year range: {int(movies['year'].min())} to {int(movies['year'].max())}")
    print(f"\nSample movies with years:")
    print(movies[movies['year'].notna()][['title', 'year', 'genres']].head(10))

# Save the updated dataframe
joblib.dump(movies, "embeddings/faiss_index/movies.pkl")
print(f"\n✅ Successfully saved updated movies.pkl with year column")
print(f"New columns: {movies.columns.tolist()}")
