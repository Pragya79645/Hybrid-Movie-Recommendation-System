from fastapi import APIRouter
from src.inference.recommend import recommend
import numpy as np

router = APIRouter()

@router.get("/recommend")
def get_recommendations():
    user_vector = np.random.rand(50)
    recs = recommend(user_vector)
    return recs.to_dict(orient="records")
