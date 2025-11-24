"""
Diagnostic script to check configuration loading.
Run this to verify your .env file is being loaded correctly.
"""
import os
from pathlib import Path

print("=" * 60)
print("Configuration Diagnostic Tool")
print("=" * 60)

# Check .env file location
env_file = Path(__file__).parent / ".env"
print(f"\n1. Checking .env file location:")
print(f"   Expected: {env_file}")
print(f"   Exists: {'✅ Yes' if env_file.exists() else '❌ No'}")

if env_file.exists():
    print(f"\n2. Reading .env file contents:")
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Look for API keys
    keys_found = {
        'OPENAI_API_KEY': False,
        'DEEPGRAM_API_KEY': False,
        'ELEVENLABS_API_KEY': False
    }
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            for key in keys_found.keys():
                if line.startswith(key):
                    # Extract value
                    value = line.split('=', 1)[1].strip()
                    # Remove quotes if present
                    value = value.strip('"').strip("'")
                    
                    if value:
                        keys_found[key] = True
                        print(f"   {key}: ✅ Found (preview: {value[:15]}...)")
                    else:
                        print(f"   {key}: ⚠️ Found but empty")

    for key, found in keys_found.items():
        if not found:
            print(f"   {key}: ❌ Not found")

print(f"\n3. Loading configuration with pydantic-settings:")
try:
    from app.config import settings
    
    print(f"   OPENAI_API_KEY: {'✅ Loaded' if settings.openai_api_key else '❌ Not loaded'}")
    if settings.openai_api_key:
        print(f"      Preview: {settings.openai_api_key[:15]}...")
    
    print(f"   DEEPGRAM_API_KEY: {'✅ Loaded' if settings.deepgram_api_key else '❌ Not loaded'}")
    if settings.deepgram_api_key:
        print(f"      Preview: {settings.deepgram_api_key[:15]}...")
    
    print(f"   ELEVENLABS_API_KEY: {'✅ Loaded' if settings.elevenlabs_api_key else '❌ Not loaded'}")
    if settings.elevenlabs_api_key:
        print(f"      Preview: {settings.elevenlabs_api_key[:15]}...")
    
    print(f"\n   STT Provider: {settings.stt_provider}")
    print(f"   LLM Provider: {settings.llm_provider}")
    
except Exception as e:
    print(f"   ❌ Error loading config: {e}")

print(f"\n4. Testing STT Service:")
try:
    from app.services.stt_service import STTService, DEEPGRAM_AVAILABLE
    
    print(f"   Deepgram library available: {'✅ Yes' if DEEPGRAM_AVAILABLE else '❌ No (install: pip install deepgram-sdk)'}")
    
    if DEEPGRAM_AVAILABLE:
        from app.config import settings
        if settings.deepgram_api_key:
            print(f"   ✅ Deepgram is ready to use!")
        else:
            print(f"   ⚠️ Deepgram library installed but API key not loaded")
    
except Exception as e:
    print(f"   ❌ Error checking STT service: {e}")

print("\n" + "=" * 60)
print("Diagnosis Complete!")
print("=" * 60)

print("\n📋 Summary:")
print("   If Deepgram shows ❌ Not loaded above:")
print("   1. Make sure .env file is in backend/ folder")
print("   2. Check the format: DEEPGRAM_API_KEY=your_key_here")
print("   3. No spaces around = sign")
print("   4. No quotes unless key has spaces")
print("   5. Restart backend after changes")
print("\n   Get Deepgram key from: https://console.deepgram.com/")

