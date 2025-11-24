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
    livekit_url: Optional[str] = None
    livekit_api_key: Optional[str] = None
    livekit_api_secret: Optional[str] = None
    next_public_livekit_url: Optional[str] = None  # For frontend (can be same as livekit_url)

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
