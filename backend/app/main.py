"""
FastAPI application entry point for Interviewly backend.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.config import settings
from app.db import init_db
from app.schemas import HealthCheckResponse
from app.routes import interview, media, cv, cv_rewriter, livekit_routes, conversational_interview, career_agent, health, pricing, admin, auth, ats, support

# NOTE:
# This FastAPI app is intended to be an INTERNAL backend service.
# - The public entrypoint for users is the Next.js app (with Arcjet + Clerk).
# - FastAPI should NOT be directly exposed to the public internet in production.
# - In production, access should come only from trusted frontends / internal networks.

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered mock interview platform backend",
    version="1.0.0",
    debug=settings.debug
)

# Configure CORS
# Existing / current behavior (fallback) - matches current implementation
default_allow_origins = ["*"]  # Current behavior: allow all origins

# Optional strict CORS mode:
# - When STRICT_BACKEND_CORS=1, restrict to FRONTEND_ORIGIN only.
# - By default, STRICT_BACKEND_CORS is OFF to avoid breaking anything.
# - This is a future hardening option; current behavior remains unchanged.
strict_mode = os.getenv("STRICT_BACKEND_CORS", "0") == "1"
frontend_origin = os.getenv("FRONTEND_ORIGIN")

if strict_mode and frontend_origin:
    allow_origins = [frontend_origin]
else:
    allow_origins = default_allow_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)  # Health checks
app.include_router(pricing.router)  # Pricing plans (public)
app.include_router(admin.router)  # Admin analytics (protect in production!)
app.include_router(auth.router)  # Authentication & user roles
app.include_router(ats.router)  # ATS endpoints for recruiters
app.include_router(interview.router)
app.include_router(conversational_interview.router)  # Conversational AI interviews
app.include_router(media.router)
app.include_router(cv.router)
app.include_router(cv_rewriter.router)
app.include_router(career_agent.router)  # AI Career Agent
app.include_router(support.router)  # Linda Support Chat
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

