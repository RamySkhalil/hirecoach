"""
Application configuration using pydantic-settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Tell pydantic-settings to load from .env (in project root)
    model_config = SettingsConfigDict(
        env_file=".env",               # adjust if your .env is elsewhere
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    # For Neon Postgres: postgresql://user:password@host/dbname?sslmode=require
    # For local SQLite fallback: sqlite:///./interviewly.db
    database_url: str = "sqlite:///./interviewly.db"

    # AI Service API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    deepgram_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None

    # LLM Settings
    llm_provider: str = "openai"  # "openai" or "anthropic"
    llm_model: str = "gpt-4o"  # gpt-4o (latest), gpt-4o-mini, or claude-3-5-sonnet-20241022
    llm_temperature: float = 0.7

    # TTS Settings (legacy ElevenLabs – now unused, but kept to avoid breaking anything)
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_model: str = "eleven_multilingual_v2"

    # STT Settings
    # Default to OpenAI Whisper as the primary STT provider
    stt_provider: str = "whisper"  # "deepgram" or "whisper"

    # LiveKit Settings
    # Backend uses these to generate tokens and connect agent
    livekit_url: Optional[str] = None  # wss://your-project.livekit.cloud
    livekit_api_key: Optional[str] = None
    livekit_api_secret: Optional[str] = None

    # Clerk Authentication
    clerk_secret_key: Optional[str] = None
    
    # Cloudflare R2 Storage
    r2_bucket_name: Optional[str] = None
    r2_account_id: Optional[str] = None
    r2_access_key_id: Optional[str] = None
    r2_secret_access_key: Optional[str] = None
    r2_endpoint_url: Optional[str] = None  # e.g., https://<account-id>.r2.cloudflarestorage.com (without bucket name)
    r2_public_url: Optional[str] = None  # Custom domain/CDN URL (deprecated, not used for private storage)
    
    # App settings
    app_name: str = "Interviewly"
    debug: bool = True


settings = Settings()

# Optional: small debug print (will not show the key itself)
if settings.debug:
    print(
        f"[Config] Loaded settings. "
        f"OPENAI_API_KEY set: {bool(settings.openai_api_key)}, "
        f"DB: {settings.database_url}"
    )
