"""
Media-related API endpoints (STT, TTS).
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response

from app.schemas import STTResponse, TTSRequest
from app.services.stt_service import STTService
from app.services.tts_service import TTSService

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/stt", response_model=STTResponse)
async def speech_to_text(audio: UploadFile = File(...)):
    """
    Convert speech audio to text (Speech-to-Text).

    Now standardized on OpenAI Whisper.

    Expects multipart/form-data with field name "audio" containing
    browser-recorded audio (e.g. webm/opus from MediaRecorder).
    """
    try:
        # Read audio file
        audio_data = await audio.read()
        audio_length = len(audio_data)

        print(
            f"[STT] Incoming audio: "
            f"content_type={audio.content_type}, bytes={audio_length}"
        )

        if audio_length == 0:
            raise HTTPException(status_code=400, detail="Empty audio stream received")

        # Call STT service (OpenAI Whisper)
        transcript = await STTService.transcribe_audio(audio_data)

        return STTResponse(text=transcript)

    except HTTPException:
        raise
    except Exception as e:
        print(f"[STT] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"STT processing error: {str(e)}")


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech audio (Text-to-Speech) using OpenAI TTS.
    Returns audio file directly (MP3 format).

    TTSRequest is expected to contain at least a 'text' field.
    Any extra fields (e.g. voice selection) can be wired later.
    """
    try:
        if not request.text or len(request.text) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        # Call TTS service (OpenAI)
        # If TTSRequest has a voice field, you can pass it here:
        # result = await TTSService.synthesize_speech(request.text, voice=request.voice or "alloy")
        result = await TTSService.synthesize_speech(request.text)

        # If we have audio bytes, return them directly
        if result.get("audio_bytes"):
            return Response(
                content=result["audio_bytes"],
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": "attachment; filename=speech.mp3"
                },
            )

        # Otherwise return JSON with metadata (fallback/dummy mode)
        return {
            "audio_url": result.get("audio_url"),
            "audio_bytes_length": result.get("audio_bytes_length", 0),
            "message": "Audio generation not available (no API key configured)",
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[TTS] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS processing error: {str(e)}")


@router.get("/tts/voices")
async def get_available_voices():
    """
    Get list of available TTS voices.

    Previously this used ElevenLabs; now it returns a static list
    of OpenAI-compatible voices from TTSService.
    """
    try:
        voices = await TTSService.get_available_voices()
        return {"voices": voices}
    except Exception as e:
        print(f"[TTS] Voices error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching voices: {str(e)}")
