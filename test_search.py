"""
Test script for movie similarity search feature
Run this after starting the backend to verify the search endpoint works correctly
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_autocomplete():
    """Test the autocomplete endpoint"""
    print("\n" + "="*60)
    print("Testing Autocomplete")
    print("="*60)
    
    query = "Aven"
    response = requests.get(f"{BASE_URL}/search/autocomplete", params={"query": query, "limit": 5})
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Autocomplete working!")
        print(f"Query: '{data['query']}'")
        print(f"Found {data['count']} suggestions:\n")
        for suggestion in data['suggestions']:
            print(f"  - {suggestion['title']} ({suggestion['genres']})")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_similarity_search(movie_name="Avengers", top_k=5):
    """Test the similarity search endpoint"""
    print("\n" + "="*60)
    print(f"Testing Similarity Search for '{movie_name}'")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/search/similar",
        params={"movie_name": movie_name, "top_k": top_k}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Search working!")
        print(f"Query Movie: {data['query_movie']}")
        print(f"Found {data['total_results']} similar movies:\n")
        
        for i, movie in enumerate(data['similar_movies'], 1):
            similarity_pct = movie['similarity_score'] * 100
            print(f"{i}. {movie['title']}")
            print(f"   Genres: {movie['genres']}")
            print(f"   Similarity: {similarity_pct:.1f}%")
            print()
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_nonexistent_movie():
    """Test error handling for nonexistent movie"""
    print("\n" + "="*60)
    print("Testing Error Handling (Nonexistent Movie)")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/search/similar",
        params={"movie_name": "zzzNonexistentMovie123", "top_k": 5}
    )
    
    if response.status_code == 404:
        print("✅ Error handling works correctly!")
        print(f"Error message: {response.json()['detail']}")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")

def main():
    print("\n" + "="*60)
    print("MOVIE SIMILARITY SEARCH - BACKEND TEST")
    print("="*60)
    print(f"Testing backend at: {BASE_URL}")
    print("Make sure the backend is running (uvicorn backend.app:app --reload)")
    
    try:
        # Test if backend is running
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Backend is running!")
        else:
            print("❌ Backend responded with unexpected status")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running!")
        return
    
    # Run tests
    test_autocomplete()
    test_similarity_search("Avengers", 5)
    test_similarity_search("Matrix", 3)
    test_nonexistent_movie()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start frontend: cd frontend && pnpm dev")
    print("2. Visit: http://localhost:3000/search")
    print("3. Try searching for movies!")

if __name__ == "__main__":
    main()
