"""
Quick profile viewer
"""
import json

def view_profiles():
    try:
        with open("profiles/user_profiles.json", "r") as f:
            profiles = json.load(f)
            
        print("\n" + "=" * 70)
        print("👥 USER PROFILES")
        print("=" * 70)
        
        for user_id, profile in profiles.items():
            print(f"\n🎭 {user_id}")
            print(f"   Clicks: {profile['interaction_count']}")
            print(f"   Top Genres:")
            
            # Sort by weight
            sorted_genres = sorted(
                profile['genre_weights'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            for genre, weight in sorted_genres[:5]:
                bar = "█" * int(weight * 40)
                print(f"      {genre:15} {weight:6.1%} {bar}")
        
        print("\n" + "=" * 70)
        
    except FileNotFoundError:
        print("No profiles found yet!")

if __name__ == "__main__":
    view_profiles()
