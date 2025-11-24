"""
LiveKit API endpoints for real-time voice interview sessions.
"""
from datetime import timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import settings

# Try to import LiveKit
try:
    from livekit import api
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False
    print("WARNING: LiveKit not installed. Run: pip install livekit")


router = APIRouter(prefix="/livekit", tags=["livekit"])


class TokenRequest(BaseModel):
    session_id: str
    participant_name: str = "Candidate"


@router.post("/token")
async def create_token(request: TokenRequest):
    """
    Generate LiveKit access token for interview session.
    
    This token allows the frontend to join a LiveKit room and
    communicate with the AI interviewer agent.
    """
    if not LIVEKIT_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="LiveKit not installed. Install with: pip install livekit"
        )
    
    if not settings.livekit_api_key or not settings.livekit_api_secret:
        raise HTTPException(
            status_code=500,
            detail="LiveKit not configured. Add LIVEKIT_API_KEY and LIVEKIT_API_SECRET to .env"
        )
    
    if not settings.livekit_url:
        raise HTTPException(
            status_code=500,
            detail="LiveKit URL not configured. Add LIVEKIT_URL to .env"
        )
    
    try:
        # Create access token
        token = api.AccessToken(
            settings.livekit_api_key,
            settings.livekit_api_secret
        )
        
        # Set participant identity and name
        token.with_identity(f"{request.participant_name}-{request.session_id}")
        token.with_name(request.participant_name)
        
        # Grant permissions
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=f"interview-{request.session_id}",
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
        ))
        
        # Set token expiration (2 hours - enough for long interviews)
        token.with_ttl(timedelta(seconds=7200))
        
        jwt_token = token.to_jwt()
        
        print(f"✅ Generated LiveKit token for session: {request.session_id}")
        
        return {
            "token": jwt_token,
            "url": settings.livekit_url,
            "room_name": f"interview-{request.session_id}"
        }
        
    except Exception as e:
        print(f"❌ LiveKit token generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Token generation failed: {str(e)}"
        )


@router.get("/health")
async def livekit_health():
    """Check if LiveKit is properly configured."""
    return {
        "livekit_installed": LIVEKIT_AVAILABLE,
        "livekit_configured": bool(
            settings.livekit_api_key and 
            settings.livekit_api_secret and 
            settings.livekit_url
        ),
        "url": settings.livekit_url if settings.livekit_url else "Not configured",
    }

