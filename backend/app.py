from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.recommend import router
from backend.routes.chat import router as chat_router

app = FastAPI(title="Recommendation System")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {"message": "Movie Recommendation API", "status": "running"}
