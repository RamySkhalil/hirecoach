"""
FastAPI application entry point for Interviewly backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.config import settings
from app.db import init_db
from app.schemas import HealthCheckResponse
from app.routes import interview, media, cv, cv_rewriter, livekit_routes, conversational_interview, career_agent, health

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered mock interview platform backend",
    version="1.0.0",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)  # Health checks
app.include_router(interview.router)
app.include_router(conversational_interview.router)  # NEW: Conversational AI interviews
app.include_router(media.router)
app.include_router(cv.router)
app.include_router(cv_rewriter.router)
app.include_router(career_agent.router)  # NEW: AI Career Agent
app.include_router(livekit_routes.router)


@app.on_event("startup")
def startup_event():
    """Initialize database on application startup."""
    print("🚀 Starting Interviewly backend...")
    print(f"📊 Database: {settings.database_url}")
    
    # Check API keys
    print("\n🔑 API Keys Status:")
    print(f"  OpenAI: {'✅ Configured' if settings.openai_api_key else '❌ Not set'}")
    print(f"  ElevenLabs: {'✅ Configured' if settings.elevenlabs_api_key else '❌ Not set'}")
    if settings.elevenlabs_api_key:
        print(f"    Key preview: {settings.elevenlabs_api_key[:10]}...")
    print(f"  Deepgram: {'✅ Configured' if settings.deepgram_api_key else '❌ Not set'}")
    print(f"  LiveKit: {'✅ Configured' if settings.livekit_api_key else '❌ Not set'}")
    print(f"  LLM Provider: {settings.llm_provider}")
    print(f"  STT Provider: {settings.stt_provider}\n")
    
    init_db()
    print("✅ Database initialized")


@app.get("/", response_model=HealthCheckResponse)
def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        app_name=settings.app_name,
        timestamp=datetime.utcnow()
    )


@app.get("/health", response_model=HealthCheckResponse)
def health():
    """Alternative health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        app_name=settings.app_name,
        timestamp=datetime.utcnow()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

