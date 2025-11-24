"""
Text-to-Speech (TTS) Service using OpenAI TTS.
"""

from typing import Optional, List, Dict

import dotenv
from openai import OpenAI

from app.config import settings

dotenv.load_dotenv()


class TTSService:
    """
    Service for converting text to speech audio using OpenAI TTS.
    """

    @staticmethod
    def _get_client() -> Optional[OpenAI]:
        """Get OpenAI client if API key is configured."""
        if not settings.openai_api_key:
            print("OPENAI_API_KEY not configured")
            return None

        try:
            client = OpenAI(api_key=settings.openai_api_key)
            return client
        except Exception as e:
            print(f"Failed to initialize OpenAI client: {e}")
            return None

    @staticmethod
    async def synthesize_speech(text: str, voice: str = "alloy") -> dict:
        """
        Convert text to speech audio using OpenAI.

        Args:
            text: Text to convert to speech.
            voice: OpenAI voice name (e.g., "alloy").

        Returns:
            Dictionary with audio data:
            {
                "audio_bytes": bytes | None,
                "audio_url": None,
                "audio_bytes_length": int
            }
        """
        client = TTSService._get_client()
        if not client:
            return {
                "audio_bytes": None,
                "audio_url": None,
                "audio_bytes_length": 0,
            }

        try:
            print(f"[TTS] 🔈 Generating audio for text (len={len(text)})")

            # OpenAI audio TTS call
            audio_response = client.audio.speech.create(
                model="gpt-4o-mini-tts",  # you can change to another TTS-capable model
                voice=voice,
                input=text,
            )

            # In the latest OpenAI Python SDK, audio.speech.create returns raw bytes
            audio_bytes = audio_response

            return {
                "audio_bytes": audio_bytes,
                "audio_url": None,  # future: upload to storage and return URL
                "audio_bytes_length": len(audio_bytes),
            }

        except Exception as e:
            print(f"[TTS] ❌ OpenAI TTS Error: {e}")
            return {
                "audio_bytes": None,
                "audio_url": None,
                "audio_bytes_length": 0,
            }

    @staticmethod
    async def get_available_voices() -> List[Dict]:
        """
        Get list of available TTS voices (OpenAI).

        OpenAI doesn't have a 'voices API' like ElevenLabs, so we return
        a static list of known voices that work with the selected model.
        """
        # Extend this list if you experiment with more voices/models.
        return [
            {
                "voice_id": "alloy",
                "name": "Alloy",
                "description": "Default OpenAI TTS voice",
                "category": "general",
            }
        ]
