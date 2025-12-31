from fastapi import FastAPI
from routes.recommend import router

app = FastAPI(title="Recommendation System")
app.include_router(router)
