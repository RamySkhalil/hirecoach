"""
LiveKit Voice Agent for AI Interview Platform

This agent handles real-time voice conversations with interview candidates using:
- Deepgram for speech-to-text (STT)
- OpenAI GPT for intelligent responses
- ElevenLabs for text-to-speech (TTS)
- Silero VAD for voice activity detection

Usage:
    python livekit_agent.py start
"""
import asyncio
import logging
import ssl
import certifi
from typing import Annotated
from livekit import agents, rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, tokenize, tts
from livekit.plugins import deepgram, openai, elevenlabs, silero
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Fix SSL certificate issues on Windows
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("interview-agent")


async def entrypoint(ctx: JobContext):
    """
    Main entry point for the LiveKit voice agent.
    
    This function is called whenever a participant joins an interview room.
    It sets up the voice assistant and manages the conversation flow.
    """
    logger.info(f"🎤 Agent starting for room: {ctx.room.name}")
    
    try:
        # Connect to the room (audio only, no video)
        # Use explicit connection options to avoid region detection issues
        rtc_config = rtc.RoomOptions(
            auto_subscribe=AutoSubscribe.AUDIO_ONLY,
            dynacast=True,
        )
        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        
        # Get room metadata (contains interview context)
        room_name = ctx.room.name
        session_id = room_name.replace("interview-", "")
        
        logger.info(f"📝 Session ID: {session_id}")
        
        # Initial greeting message
        initial_message = (
            "Hello! I'm your AI interviewer. "
            "I'll be conducting your interview today. "
            "Please speak clearly, and feel free to take your time with your answers. "
            "Are you ready to begin?"
        )
        
        # Create voice assistant with AI capabilities
        assistant = agents.VoiceAssistant(
            # Voice Activity Detection - detects when user starts/stops speaking
            vad=silero.VAD.load(),
            
            # Speech-to-Text - converts user speech to text
            stt=deepgram.STT(
                model="nova-2",
                language="en-US",
            ),
            
            # Language Model - generates intelligent responses
            llm=openai.LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
            # Text-to-Speech - converts AI responses to natural voice
            tts=elevenlabs.TTS(
                model_id="eleven_turbo_v2",
                voice="Rachel",  # Professional female voice
            ),
            
            # Conversation context and system prompt
            chat_ctx=openai.ChatContext().append(
                role="system",
                text=(
                    "You are a professional AI interviewer conducting a job interview. "
                    "Your role is to:\n"
                    "1. Ask relevant interview questions based on the candidate's responses\n"
                    "2. Listen actively and ask thoughtful follow-up questions\n"
                    "3. Be encouraging and help the candidate showcase their skills\n"
                    "4. Keep questions clear and concise (2-3 sentences max)\n"
                    "5. Maintain a professional yet friendly tone\n"
                    "6. Wait for complete answers before asking follow-ups\n\n"
                    "Remember: Your goal is to help the candidate succeed while gathering "
                    "meaningful information about their qualifications and experience."
                )
            )
        )
        
        # Start the assistant
        assistant.start(ctx.room)
        
        logger.info("✅ Voice assistant started successfully")
        
        # Greet the candidate
        await assistant.say(initial_message, allow_interruptions=True)
        
        logger.info("👋 Initial greeting delivered")
        
    except Exception as e:
        logger.error(f"❌ Agent error: {e}", exc_info=True)
        raise


def main():
    """Main function to run the LiveKit agent worker."""
    
    # Check required environment variables
    required_vars = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "DEEPGRAM_API_KEY",
        "OPENAI_API_KEY",
        "ELEVENLABS_API_KEY",
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        logger.error("Please add them to backend/.env file")
        return
    
    logger.info("🚀 Starting LiveKit Interview Agent...")
    logger.info(f"📡 LiveKit URL: {os.getenv('LIVEKIT_URL')}")
    logger.info("✅ All environment variables configured")
    logger.info("🎧 Waiting for interview sessions...")
    
    # Run the agent worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            # Worker will process jobs from the queue
            # Each job = one interview session
        )
    )


if __name__ == "__main__":
    main()

