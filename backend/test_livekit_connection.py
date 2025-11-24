"""Test LiveKit connection from Python"""
import asyncio
import httpx
from app.config import settings

async def test_connection():
    print(f"[TEST] Testing connection to: {settings.livekit_url}")
    print(f"[KEY] API Key: {settings.livekit_api_key[:10]}..." if settings.livekit_api_key else "[ERROR] No API Key")
    
    # Test 1: Basic HTTP request
    print("\n[TEST 1] HTTP GET to /settings/regions")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"https://interviewsaas-m7lvjg0t.livekit.cloud/settings/regions",
                headers={"Authorization": f"Bearer {settings.livekit_api_key}"} if settings.livekit_api_key else {}
            )
            print(f"   [OK] Status: {response.status_code}")
            print(f"   Response: {response.text[:100]}")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
    
    # Test 2: WebSocket connection (what LiveKit actually uses)
    print("\n[TEST 2] WebSocket connection")
    try:
        import websockets
        url = settings.livekit_url.replace("wss://", "ws://") if "wss://" in settings.livekit_url else settings.livekit_url
        print(f"   Attempting: {url}")
        async with websockets.connect(url, timeout=10) as ws:
            print(f"   [OK] WebSocket connected!")
    except ImportError:
        print("   [WARNING] websockets library not installed (this is OK)")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
    
    # Test 3: Check firewall/proxy settings
    print("\n[TEST 3] Environment proxy settings")
    import os
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    print(f"   HTTP_PROXY: {http_proxy or 'Not set'}")
    print(f"   HTTPS_PROXY: {https_proxy or 'Not set'}")
    
    print("\n" + "="*60)
    print("[INFO] If Test 1 works but LiveKit fails, it's likely:")
    print("   1. Windows Firewall blocking Python.exe")
    print("   2. Antivirus blocking WebSocket connections")
    print("   3. LiveKit SDK issue with SSL certificates")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_connection())

