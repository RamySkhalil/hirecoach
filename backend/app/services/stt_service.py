"""
Speech-to-Text (STT) Service using OpenAI Whisper, with ffmpeg conversion.

We accept browser audio (webm/opus etc.), convert it to WAV via ffmpeg,
and then send the WAV file to OpenAI Whisper to avoid "invalid file format"
issues.
"""

import io
import os
import tempfile
import subprocess
import dotenv
from openai import OpenAI

from app.config import settings

dotenv.load_dotenv()


class STTService:
    """
    Service for converting speech audio to text.
    Standardized on OpenAI Whisper.
    """

    @staticmethod
    async def transcribe_audio(audio_data: bytes) -> str:
        """
        Main entry point for STT – uses OpenAI Whisper.

        Args:
            audio_data: Raw audio bytes from browser (webm/opus, etc.)

        Returns:
            Transcribed text as a string.
        """
        return await STTService._transcribe_whisper(audio_data)

    @staticmethod
    async def _transcribe_whisper(audio_data: bytes) -> str:
        """
        Transcribe using OpenAI Whisper API.

        Steps:
        1. Save incoming browser audio (webm/opus etc.) to a temp file.
        2. Use ffmpeg to convert it to mono 16kHz WAV.
        3. Send the WAV file to OpenAI Whisper.
        """
        if not settings.openai_api_key:
            msg = "OpenAI not configured. Please add OPENAI_API_KEY to .env"
            print("[Whisper] ❌", msg)
            return msg

        try:
            print(f"[Whisper] 🔊 Received {len(audio_data)} bytes for transcription")

            client = OpenAI(api_key=settings.openai_api_key)

            # Save debug copy of the original audio (for manual testing)
            try:
                debug_path = os.path.join(os.getcwd(), "debug_audio.webm")
                with open(debug_path, "wb") as dbg:
                    dbg.write(audio_data)
                print(f"[Whisper] 🐞 Saved debug audio to {debug_path}")
            except Exception as debug_err:
                print(f"[Whisper] ⚠️ Could not write debug audio file: {debug_err}")

            # 1) Save input bytes to a temp source file (webm/ogg etc.)
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as src_tmp:
                src_tmp.write(audio_data)
                src_tmp.flush()
                src_path = src_tmp.name

            # 2) Prepare temp output WAV path
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out_tmp:
                out_path = out_tmp.name

            print(f"[Whisper] 📁 Temp source file: {src_path}")
            print(f"[Whisper] 📁 Temp WAV file:   {out_path}")

            # 3) Run ffmpeg to convert to mono 16kHz WAV
            #    ffmpeg -y -i input.webm -ar 16000 -ac 1 output.wav
            try:
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    src_path,
                    "-ar",
                    "16000",
                    "-ac",
                    "1",
                    out_path,
                ]
                print(f"[Whisper] 🛠️ Running ffmpeg: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )

                if result.returncode != 0:
                    stderr_text = result.stderr.decode("utf-8", errors="ignore")
                    print(f"[Whisper] ❌ ffmpeg failed: {stderr_text}")
                    return (
                        "Transcription error: ffmpeg failed to convert audio. "
                        "Ensure ffmpeg is installed and on PATH."
                    )
            except FileNotFoundError:
                print("[Whisper] ❌ ffmpeg not found on PATH")
                return (
                    "Transcription error: ffmpeg is not installed or not on PATH. "
                    "Please install ffmpeg."
                )

            # 4) Send converted WAV to OpenAI Whisper
            try:
                with open(out_path, "rb") as f:
                    # You can also use the newer model:
                    # model="gpt-4o-mini-transcribe"
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        response_format="text",  # returns a plain string
                    )
            finally:
                # Clean up the temp files
                for path in (src_path, out_path):
                    try:
                        os.remove(path)
                        print(f"[Whisper] 🧹 Temp file removed: {path}")
                    except Exception as rm_err:
                        print(f"[Whisper] ⚠️ Could not remove temp file {path}: {rm_err}")

            print(f"[Whisper] ✅ Transcript: {transcript}")
            return transcript

        except Exception as e:
            print(f"[Whisper] ❌ STT Error: {e}")
            return f"Transcription error: {str(e)}"
