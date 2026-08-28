from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.tickets import router as tickets_router
from app.api.ai import router as ai_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A customer support backend with AI assistance.",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(ai_router)

@app.get("/api/health", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint to verify the API is running.
    """
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME
    }
