import pandas as pd

def load_and_preprocess(interactions_path, items_path):
    ratings = pd.read_csv(interactions_path)
    items = pd.read_csv(items_path)

    # Basic preprocessing
    ratings['user_id'] = ratings['user_id'].astype(int)
    ratings['movie_id'] = ratings['movie_id'].astype(int)

    # Merge for metadata if needed
    return ratings, items

if __name__ == "__main__":
    ratings, items = load_and_preprocess(
        "data/raw/interactions.csv",
        "data/raw/items.csv"
    )
    ratings.to_csv("data/processed/train.csv", index=False)
    items.to_csv("data/processed/items.csv", index=False)
