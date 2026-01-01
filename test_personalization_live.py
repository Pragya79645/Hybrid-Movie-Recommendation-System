"""
Diagnostic tool to test personalization
Shows real-time profile updates
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def show_profile(user_id):
    """Display user profile"""
    try:
        with open("profiles/user_profiles.json", "r") as f:
            profiles = json.load(f)
            if user_id in profiles:
                print(f"\n📊 Profile for '{user_id}':")
                print(f"   Interactions: {profiles[user_id]['interaction_count']}")
                print(f"   Genre Weights:")
                for genre, weight in profiles[user_id]['genre_weights'].items():
                    bar = "█" * int(weight * 50)
                    print(f"      {genre:15} {weight:.2%} {bar}")
            else:
                print(f"\n⚠️  No profile found for '{user_id}'")
    except FileNotFoundError:
        print("\n⚠️  No profiles file found")

def simulate_clicks(user_id, clicks):
    """Simulate user clicking on movies"""
    print(f"\n🎬 Simulating {len(clicks)} clicks for user '{user_id}'...")
    
    for i, (movie_id, genres) in enumerate(clicks, 1):
        print(f"\n   Click {i}: Movie {movie_id} - {genres}")
        response = requests.post(
            f"{BASE_URL}/interact",
            json={
                "user_id": user_id,
                "movie_id": movie_id,
                "genres": genres
            }
        )
        
        if response.status_code == 200:
            print(f"   ✅ Tracked successfully")
            show_profile(user_id)
        else:
            print(f"   ❌ Failed: {response.status_code}")
        
        time.sleep(0.5)

def main():
    print("=" * 70)
    print("🎯 PERSONALIZATION DIAGNOSTIC TOOL")
    print("=" * 70)
    
    user_id = input("\nEnter User ID to test (e.g., 'testuser'): ").strip()
    
    print("\n📋 Choose test scenario:")
    print("1. Sci-Fi fan (clicks on Sci-Fi movies)")
    print("2. Horror fan (clicks on Horror movies)")
    print("3. Mixed preferences (clicks on various genres)")
    print("4. Custom scenario")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    scenarios = {
        "1": [
            (1, ["Sci-Fi", "Adventure"]),
            (2, ["Sci-Fi", "Action"]),
            (3, ["Sci-Fi", "Thriller"]),
            (4, ["Sci-Fi", "Drama"]),
        ],
        "2": [
            (10, ["Horror", "Thriller"]),
            (11, ["Horror", "Mystery"]),
            (12, ["Horror", "Thriller"]),
        ],
        "3": [
            (20, ["Comedy", "Romance"]),
            (21, ["Action", "Adventure"]),
            (22, ["Drama", "Thriller"]),
            (23, ["Sci-Fi", "Action"]),
        ]
    }
    
    if choice in scenarios:
        print(f"\n🎬 Initial profile:")
        show_profile(user_id)
        
        simulate_clicks(user_id, scenarios[choice])
        
        print("\n" + "=" * 70)
        print("✅ Test Complete!")
        print("=" * 70)
        print(f"\n💡 Notice how the genre weights evolved as '{user_id}' clicked movies")
        print(f"   The system learned their preferences automatically!")
    
    elif choice == "4":
        print("\n📝 Enter clicks manually:")
        clicks = []
        while True:
            movie_id = input("Movie ID (or Enter to finish): ").strip()
            if not movie_id:
                break
            genres_str = input("Genres (comma-separated): ").strip()
            genres = [g.strip() for g in genres_str.split(",")]
            clicks.append((int(movie_id), genres))
        
        if clicks:
            show_profile(user_id)
            simulate_clicks(user_id, clicks)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
