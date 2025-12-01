"""
Test script to verify LiveKit token generation works.
Run: python test_livekit_token.py
"""
import os
from dotenv import load_dotenv
from livekit import api
from datetime import timedelta

load_dotenv()

def test_token_generation():
    print("=" * 60)
    print("🧪 Testing LiveKit Token Generation")
    print("=" * 60)
    
    # Check environment variables
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    print(f"\nLIVEKIT_URL: {livekit_url}")
    print(f"LIVEKIT_API_KEY: {'Set ✅' if livekit_api_key else 'Missing ❌'}")
    print(f"LIVEKIT_API_SECRET: {'Set ✅' if livekit_api_secret else 'Missing ❌'}")
    
    if not all([livekit_url, livekit_api_key, livekit_api_secret]):
        print("\n❌ Missing required environment variables!")
        return False
    
    try:
        # Test token generation
        session_id = "test-session-123"
        participant_name = "Test User"
        
        token = api.AccessToken(livekit_api_key, livekit_api_secret)
        token.with_identity(f"{participant_name}-{session_id}")
        token.with_name(participant_name)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=f"interview-{session_id}",
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
        ))
        token.with_ttl(timedelta(seconds=7200))
        
        jwt_token = token.to_jwt()
        
        print("\n✅ Token generated successfully!")
        print(f"\nRoom Name: interview-{session_id}")
        print(f"Token (first 50 chars): {jwt_token[:50]}...")
        print(f"Token length: {len(jwt_token)} characters")
        
        print("\n" + "=" * 60)
        print("✅ Backend token generation is working!")
        print("=" * 60)
        
        print("\nNext steps:")
        print("1. Make sure agent is running: cd backend && RUN_AGENT.bat")
        print("2. Configure LiveKit Cloud dispatch rule (see CONFIGURE_LIVEKIT_DISPATCH.md)")
        print("3. Test from frontend: http://localhost:3000/interview/setup")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error generating token: {e}")
        return False

if __name__ == "__main__":
    test_token_generation()

