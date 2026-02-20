from fastapi import FastAPI
from app.api.routes import router as v1_router
from app.core.config import settings

app = FastAPI(
    title="Multimodal Conversation Intelligence API",
    version="1.0.0",
    description="API-first backend for multimodal (audio/text) conversation intelligence using Gemini.",
)

app.include_router(v1_router, prefix="/v1")


@app.get("/", tags=["meta"])
def root():
    return {
        "service": "conversation-intelligence-api",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/v1/health",
        "analyze": "/v1/analyze",
        "auth_enabled": settings.api_key_required,
    }