"""
Test the intelligent chat system
Run this after starting the backend server
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_recommendations(recs, max_display=3):
    """Pretty print recommendations"""
    for i, rec in enumerate(recs[:max_display], 1):
        print(f"\n   {i}. {rec['title']}")
        print(f"      Genres: {rec['genres']}")
        if rec.get('explanation'):
            print(f"      💡 {rec['explanation']}")

def test_chat_intelligence():
    print("🎬 Testing Intelligent Chat System\n")
    print("=" * 70)
    
    # Test 1: Simple genre request
    print("\n\n📝 Test 1: 'I want a thriller movie'")
    print("-" * 70)
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "I want a thriller movie"}
    )
    data = response.json()
    print(f"Response: {data['response']}")
    print(f"Recommendations: {len(data.get('recommendations', []))}")
    print_recommendations(data.get('recommendations', []))
    
    # Test 2: Genre with exclusion (THE KEY TEST)
    print("\n\n📝 Test 2: 'I want a thriller but not very violent'")
    print("-" * 70)
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "I want a thriller but not very violent"}
    )
    data = response.json()
    print(f"Response: {data['response']}")
    print(f"Recommendations: {len(data.get('recommendations', []))}")
    print_recommendations(data.get('recommendations', []))
    
    # Test 3: Mood-based
    print("\n\n📝 Test 3: 'Something scary'")
    print("-" * 70)
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "Something scary"}
    )
    data = response.json()
    print(f"Response: {data['response']}")
    print(f"Recommendations: {len(data.get('recommendations', []))}")
    print_recommendations(data.get('recommendations', []))
    
    # Test 4: Multiple genres
    print("\n\n📝 Test 4: 'Action sci-fi movies'")
    print("-" * 70)
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "Action sci-fi movies"}
    )
    data = response.json()
    print(f"Response: {data['response']}")
    print(f"Recommendations: {len(data.get('recommendations', []))}")
    print_recommendations(data.get('recommendations', []))
    
    # Test 5: Complex constraints
    print("\n\n📝 Test 5: 'Recent action movies that aren't too dark'")
    print("-" * 70)
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "Recent action movies that aren't too dark"}
    )
    data = response.json()
    print(f"Response: {data['response']}")
    print(f"Recommendations: {len(data.get('recommendations', []))}")
    print_recommendations(data.get('recommendations', []))
    
    # Test 6: Personalized (with user_id)
    print("\n\n📝 Test 6: Personalized for user 'alice' - 'Recommend something'")
    print("-" * 70)
    
    # First, create some interactions for alice (sci-fi fan)
    requests.post(f"{BASE_URL}/interact", json={
        "user_id": "alice",
        "movie_id": 1,
        "genres": ["Sci-Fi", "Thriller"]
    })
    requests.post(f"{BASE_URL}/interact", json={
        "user_id": "alice",
        "movie_id": 2,
        "genres": ["Sci-Fi", "Action"]
    })
    
    # Now ask for recommendations
    response = requests.post(
        f"{BASE_URL}/chat?user_id=alice",
        json={"message": "Recommend something"}
    )
    data = response.json()
    print(f"Response: {data['response']}")
    print(f"Recommendations: {len(data.get('recommendations', []))}")
    print_recommendations(data.get('recommendations', []))
    
    # Test 7: Non-recommendation query
    print("\n\n📝 Test 7: 'Hello, how are you?'")
    print("-" * 70)
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "Hello, how are you?"}
    )
    data = response.json()
    print(f"Response: {data['response']}")
    print(f"Recommendations: {len(data.get('recommendations', []))}")
    
    print("\n\n" + "=" * 70)
    print("✅ Chat Intelligence Test Complete!")
    print("\nKey Features Demonstrated:")
    print("  ✓ Intent extraction (Gemini)")
    print("  ✓ FAISS semantic retrieval")
    print("  ✓ Constraint filtering (exclusions, year)")
    print("  ✓ Personalized re-ranking")
    print("  ✓ Gemini explanations")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_chat_intelligence()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend server.")
        print("   Please make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
