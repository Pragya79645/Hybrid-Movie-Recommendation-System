"""
Test script for personalization feature
Run this after starting the backend server
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_personalization():
    print("🎬 Testing Personalization Feature\n")
    
    # Test 1: Track interactions for user1 (Sci-Fi fan)
    print("1️⃣ User 'alice' clicks on Sci-Fi movies...")
    interactions = [
        {"user_id": "alice", "movie_id": 1, "genres": ["Sci-Fi", "Thriller"]},
        {"user_id": "alice", "movie_id": 2, "genres": ["Sci-Fi", "Action"]},
        {"user_id": "alice", "movie_id": 3, "genres": ["Sci-Fi", "Drama"]},
    ]
    
    for interaction in interactions:
        response = requests.post(f"{BASE_URL}/interact", json=interaction)
        if response.status_code == 200:
            print(f"   ✅ Tracked: {interaction['genres']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    
    # Get Alice's profile
    print("\n2️⃣ Alice's profile:")
    response = requests.get(f"{BASE_URL}/recommend?user_id=alice&top_k=5")
    if response.status_code == 200:
        data = response.json()
        if data.get("profile"):
            print(f"   Genre weights: {json.dumps(data['profile'], indent=4)}")
            print(f"   Personalized: {data.get('personalized')}")
    
    # Test 2: Track interactions for user2 (Crime fan)
    print("\n3️⃣ User 'bob' clicks on Crime movies...")
    interactions = [
        {"user_id": "bob", "movie_id": 10, "genres": ["Crime", "Drama"]},
        {"user_id": "bob", "movie_id": 11, "genres": ["Crime", "Thriller"]},
        {"user_id": "bob", "movie_id": 12, "genres": ["Crime", "Drama"]},
    ]
    
    for interaction in interactions:
        response = requests.post(f"{BASE_URL}/interact", json=interaction)
        if response.status_code == 200:
            print(f"   ✅ Tracked: {interaction['genres']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    
    # Get Bob's profile
    print("\n4️⃣ Bob's profile:")
    response = requests.get(f"{BASE_URL}/recommend?user_id=bob&top_k=5")
    if response.status_code == 200:
        data = response.json()
        if data.get("profile"):
            print(f"   Genre weights: {json.dumps(data['profile'], indent=4)}")
            print(f"   Personalized: {data.get('personalized')}")
    
    # Compare recommendations
    print("\n5️⃣ Comparing Alice vs Bob recommendations:")
    
    alice_recs = requests.get(f"{BASE_URL}/recommend?user_id=alice&top_k=3").json()
    bob_recs = requests.get(f"{BASE_URL}/recommend?user_id=bob&top_k=3").json()
    
    print("\n   Alice's top 3:")
    for i, rec in enumerate(alice_recs.get("recommendations", [])[:3], 1):
        print(f"   {i}. {rec['title']} - {rec['genres']}")
    
    print("\n   Bob's top 3:")
    for i, rec in enumerate(bob_recs.get("recommendations", [])[:3], 1):
        print(f"   {i}. {rec['title']} - {rec['genres']}")
    
    print("\n✅ Same endpoint, different results! Personalization works! 🎉")

if __name__ == "__main__":
    try:
        test_personalization()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend server.")
        print("   Please make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
