"""Simple LiveKit connection test"""
import asyncio
import os
from dotenv import load_dotenv
from livekit import rtc

load_dotenv()

async def test_simple_connection():
    print("[TEST] Simple LiveKit Room Connection Test")
    print(f"[URL] {os.getenv('LIVEKIT_URL')}")
    
    # Create a room
    room = rtc.Room()
    
    # Connection callback
    @room.on("connected")
    def on_connected():
        print("[SUCCESS] Connected to room!")
    
    @room.on("disconnected")
    def on_disconnected():
        print("[INFO] Disconnected from room")
    
    @room.on("connection_state_changed")
    def on_state_changed(state: rtc.ConnectionState):
        print(f"[STATE] Connection state: {state}")
    
    # Try to connect with a test token
    try:
        # Generate a quick test token
        from livekit.api import AccessToken, VideoGrants
        
        token = AccessToken(
            os.getenv('LIVEKIT_API_KEY'),
            os.getenv('LIVEKIT_API_SECRET')
        )
        grants = VideoGrants(room_join=True, room="test-connection-room")
        token.with_grants(grants).with_identity("test-user")
        
        test_token = token.to_jwt()
        print("[TOKEN] Generated test token")
        
        # Attempt connection
        print("[CONNECT] Attempting to connect...")
        await room.connect(os.getenv('LIVEKIT_URL'), test_token)
        
        print("[SUCCESS] Connection successful!")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Disconnect
        await room.disconnect()
        print("[DONE] Test completed successfully")
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_connection())

