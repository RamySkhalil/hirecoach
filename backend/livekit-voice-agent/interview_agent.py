"""
LiveKit AI Interview Agent

This agent joins interview rooms (interview-{session_id}) and conducts
AI-powered mock interviews with candidates.

Room Naming Convention:
- Frontend creates room: interview-{session_id}
- Backend generates token for: interview-{session_id}
- LiveKit Cloud dispatch rule: interview-* → this agent
- Agent joins and conducts the interview

Setup:
1. Ensure .env.local has OPENAI_API_KEY, LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
2. Run: python interview_agent.py start
3. The agent will connect to LiveKit Cloud and wait for interview rooms
"""

from dotenv import load_dotenv
import os

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents import AgentSession, inference


load_dotenv(".env.local", override=True)

print("DEBUG LIVEKIT_URL:", os.getenv("LIVEKIT_URL"))
print("DEBUG LIVEKIT_API_KEY:", os.getenv("LIVEKIT_API_KEY"))
print("DEBUG LIVEKIT_API_SECRET:", os.getenv("LIVEKIT_API_SECRET")[:6] + "...")
os.environ.pop("SSL_CERT_FILE", None)

class InterviewCoachAgent(Agent):
    """
    AI Interview Coach Agent
    
    Conducts professional mock interviews with candidates, asking behavioral
    and technical questions, and providing constructive feedback.
    """
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are an expert AI Interview Coach conducting a professional mock interview.

Your role:
- Greet the candidate warmly and professionally
- Ask relevant interview questions based on their role
- Listen actively to their answers
- Provide constructive feedback on their responses
- Maintain a supportive yet professional tone
- Ask follow-up questions when appropriate
- Help candidates improve their interview skills

Guidelines:
- Be encouraging and supportive
- Provide specific, actionable feedback
- Use natural conversation flow
- Acknowledge good responses
- Gently point out areas for improvement
- Keep the interview professional and focused

Remember: Your goal is to help candidates succeed in their real interviews."""
        )

server = AgentServer()

@server.rtc_session()
async def interview_agent_handler(ctx: agents.JobContext):
    """
    Main handler for interview sessions.
    
    This function is called when a candidate joins an interview room.
    The room name format is: interview-{session_id}
    """
    
    # Extract session ID from room name (format: interview-{session_id})
    room_name = ctx.room.name
    session_id = room_name.replace("interview-", "") if room_name.startswith("interview-") else "unknown"
    
    print(f"✅ AI Interview Agent joining room: {room_name}")
    print(f"   Session ID: {session_id}")
    
    # Create agent session with separate components (like working example)
    # session = AgentSession(
    #     stt="deepgram",  # Deepgram STT (you have the API key)
    #     llm="openai/gpt-4o",  # GPT-4o for interview intelligence
    #     tts="openai/tts-1:alloy",  # OpenAI TTS with alloy voice
    #     vad=silero.VAD.load(),  # Voice activity detection
    #     turn_detection=MultilingualModel(),  # Turn detection
    # )

    session = AgentSession(
        stt="assemblyai/universal-streaming:en",  # same as working agent
        llm="openai/gpt-4o",                      # keep your model
        tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",  # same Cartesia voice as working agent
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    # Start the agent session
    await session.start(
        room=ctx.room,
        agent=InterviewCoachAgent(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVC(),
            ),
        ),
    )

    # Generate initial greeting
    await session.generate_reply(
        instructions="""Greet the candidate professionally. 
        Say: 'Hello! Welcome to your mock interview session. I'm your AI Interview Coach, 
        and I'm here to help you practice and improve your interview skills. 
        Before we begin, could you briefly tell me about the role you're preparing for?'"""
    )
    
    print(f"✅ Agent greeted candidate in room: {room_name}")


if __name__ == "__main__":
    print("=" * 60)
    print("🎤 LiveKit AI Interview Agent")
    print("=" * 60)
    print(f"LIVEKIT_URL: {os.getenv('LIVEKIT_URL', 'Not set')}")
    print(f"LIVEKIT_API_KEY: {'Set' if os.getenv('LIVEKIT_API_KEY') else 'Not set'}")
    print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print("=" * 60)
    print("\nWaiting for interview sessions...")
    print("Listening for rooms: interview-*")
    print("\nPress Ctrl+C to stop\n")
    
    agents.cli.run_app(server)

