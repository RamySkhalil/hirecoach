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
2. Set BACKEND_URL (default: http://localhost:8000)
3. Run: python interview_agent.py start
4. The agent will connect to LiveKit Cloud and wait for interview rooms
"""

from dotenv import load_dotenv
import os
import httpx

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents import AgentSession, inference


load_dotenv(".env.local", override=True)

# Backend API URL for fetching session data
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

print("DEBUG LIVEKIT_URL:", os.getenv("LIVEKIT_URL"))
print("DEBUG LIVEKIT_API_KEY:", os.getenv("LIVEKIT_API_KEY"))
print("DEBUG LIVEKIT_API_SECRET:", os.getenv("LIVEKIT_API_SECRET")[:6] + "...")
print("DEBUG BACKEND_URL:", BACKEND_URL)
os.environ.pop("SSL_CERT_FILE", None)


async def fetch_session_data(session_id: str) -> dict | None:
    """
    Fetch interview session details from the backend API.
    
    Returns dict with job_title, seniority, num_questions, etc.
    Returns None if fetch fails.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BACKEND_URL}/interview/session/{session_id}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Fetched session data: job_title={data.get('job_title')}, seniority={data.get('seniority')}")
                return data
            else:
                print(f"⚠️ Failed to fetch session data: HTTP {response.status_code}")
                return None
    except Exception as e:
        print(f"⚠️ Error fetching session data: {e}")
        return None


class InterviewCoachAgent(Agent):
    """
    AI Interview Coach Agent
    
    Conducts professional mock interviews with candidates, asking behavioral
    and technical questions, and providing constructive feedback.
    """
    
    def __init__(self, job_title: str = None, seniority: str = None, num_questions: int = 5) -> None:
        # Build context-aware instructions
        role_context = ""
        if job_title:
            role_context = f"\n\nInterview Context:\n- Position: {job_title}\n- Level: {seniority or 'mid'}-level\n- Questions to ask: {num_questions}"
        
        instructions = f"""You are an expert AI Interview Coach conducting a professional mock interview.
{role_context}

Your role:
- Greet the candidate warmly and professionally
- Ask relevant interview questions tailored to the {job_title or 'target'} role
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
- Focus questions on skills relevant to {job_title or 'the role'} at the {seniority or 'mid'} level

Remember: Your goal is to help candidates succeed in their real interviews."""

        super().__init__(instructions=instructions)
        
        self.job_title = job_title
        self.seniority = seniority
        self.num_questions = num_questions

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
    
    # Fetch interview session data from backend
    session_data = await fetch_session_data(session_id)
    
    job_title = session_data.get("job_title") if session_data else None
    seniority = session_data.get("seniority") if session_data else None
    num_questions = session_data.get("num_questions", 5) if session_data else 5
    
    print(f"   Job Title: {job_title or 'Not specified'}")
    print(f"   Seniority: {seniority or 'Not specified'}")
    print(f"   Questions: {num_questions}")

    session = AgentSession(
        stt="assemblyai/universal-streaming:en",  # same as working agent
        llm="openai/gpt-4o",                      # keep your model
        tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",  # same Cartesia voice as working agent
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    # Create agent with interview context
    agent = InterviewCoachAgent(
        job_title=job_title,
        seniority=seniority,
        num_questions=num_questions
    )

    # Start the agent session
    await session.start(
        room=ctx.room,
        agent=agent,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVC(),
            ),
        ),
    )

    # Generate context-aware initial greeting
    if job_title:
        greeting_instructions = f"""Greet the candidate professionally and acknowledge their target role.
        Say: 'Hello! Welcome to your mock interview session for the {job_title} position. 
        I'm your AI Interview Coach, and I'll be conducting a {seniority or 'mid'}-level interview with you today.
        I have {num_questions} questions prepared to help you practice.
        Are you ready to begin?'"""
    else:
        # Fallback if session data couldn't be fetched
        greeting_instructions = """Greet the candidate professionally. 
        Say: 'Hello! Welcome to your mock interview session. I'm your AI Interview Coach, 
        and I'm here to help you practice and improve your interview skills. 
        Before we begin, could you briefly tell me about the role you're preparing for?'"""
    
    await session.generate_reply(instructions=greeting_instructions)
    
    print(f"✅ Agent greeted candidate in room: {room_name}")


if __name__ == "__main__":
    print("=" * 60)
    print("🎤 LiveKit AI Interview Agent")
    print("=" * 60)
    print(f"LIVEKIT_URL: {os.getenv('LIVEKIT_URL', 'Not set')}")
    print(f"LIVEKIT_API_KEY: {'Set' if os.getenv('LIVEKIT_API_KEY') else 'Not set'}")
    print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print(f"BACKEND_URL: {BACKEND_URL}")
    print("=" * 60)
    print("\nWaiting for interview sessions...")
    print("Listening for rooms: interview-*")
    print("Will fetch job_title/seniority from backend for each session")
    print("\nPress Ctrl+C to stop\n")
    
    agents.cli.run_app(server)

