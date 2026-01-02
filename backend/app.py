from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from .routes.recommend import router
    from .routes.chat import router as chat_router
    from .routes.interact import router as interact_router
    from .routes.search import router as search_router
except ImportError:
    from routes.recommend import router
    from routes.chat import router as chat_router
    from routes.interact import router as interact_router
    from routes.search import router as search_router
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
app.include_router(interact_router)
app.include_router(search_router)

@app.get("/")
def root():
    return {"message": "Movie Recommendation API", "status": "running"}
