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
from PIL import Image

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import noise_cancellation, silero, hedra
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents import AgentSession, inference


load_dotenv(".env.local", override=True)

# Backend API URL for fetching session data
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

print("DEBUG LIVEKIT_URL:", os.getenv("LIVEKIT_URL"))
print("DEBUG LIVEKIT_API_KEY:", os.getenv("LIVEKIT_API_KEY"))
print("DEBUG LIVEKIT_API_SECRET:", os.getenv("LIVEKIT_API_SECRET")[:6] + "..." if os.getenv("LIVEKIT_API_SECRET") else "Not set")
print("DEBUG HEDRA_API_KEY:", "Set" if os.getenv("HEDRA_API_KEY") else "Not set")
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
            role_context = f"\n\nInterview Context:\n- Position: {job_title}\n- Level: {seniority or 'mid'}-level\n- Total questions to ask: {num_questions}"
        
        instructions = f"""You are an expert AI Interview Coach conducting a professional mock interview.
{role_context}

IMPORTANT: You must ask EXACTLY {num_questions} questions during this interview, no more, no less.

Your role:
- Greet the candidate warmly and professionally
- Ask exactly {num_questions} relevant interview questions tailored to the {job_title or 'target'} role
- Listen actively to their answers
- Provide brief constructive feedback on their responses (keep feedback short and conversational)
- Maintain a supportive yet professional tone
- Ask follow-up questions when appropriate (but count this as part of your {num_questions} questions)
- Help candidates improve their interview skills
- After the {num_questions}th question is answered, thank them and wrap up the interview

Guidelines:
- Be encouraging and supportive
- Provide specific, actionable feedback
- Use natural conversation flow
- Acknowledge good responses
- Gently point out areas for improvement
- Keep the interview professional and focused
- Focus questions on skills relevant to {job_title or 'the role'} at the {seniority or 'mid'} level
- Keep track of how many questions you've asked
- When you reach {num_questions} questions, conclude with: "Thank you for completing this interview. We've covered all {num_questions} questions. You'll receive a detailed report shortly. Have a great day!"

Remember: Your goal is to help candidates succeed in their real interviews, and you must stick to exactly {num_questions} questions."""

        super().__init__(instructions=instructions)
        
        self.job_title = job_title
        self.seniority = seniority
        self.num_questions = num_questions
        self.questions_asked = 0
        self.conversation_transcript = []

server = AgentServer()

async def save_interview_transcript(session_id: str, transcript: list, questions_asked: int) -> None:
    """
    Save the interview transcript to the backend.
    
    This allows the backend to generate a detailed report based on the conversation.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BACKEND_URL}/interview/voice-session/{session_id}/complete",
                json={
                    "transcript": transcript,
                    "questions_asked": questions_asked,
                }
            )
            if response.status_code == 200:
                print(f"✅ Saved transcript for session {session_id}")
            else:
                print(f"⚠️ Failed to save transcript: HTTP {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error saving transcript: {e}")


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

    # Track conversation for transcript
    transcript = []
    
    # Track if interview is complete
    interview_complete = False
    
    # Load avatar image
    avatar_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "avatar.png")
    avatar_image = None
    
    if os.path.exists(avatar_image_path):
        try:
            avatar_image = Image.open(avatar_image_path)
            print(f"✅ Loaded avatar image from: {avatar_image_path}")
        except Exception as e:
            print(f"⚠️ Failed to load avatar image: {e}")
    else:
        print(f"⚠️ Avatar image not found at: {avatar_image_path}")
    
    # Initialize Hedra avatar if image is available and API key is set
    avatar = None
    if avatar_image and os.getenv("HEDRA_API_KEY"):
        try:
            avatar = hedra.AvatarSession(
                avatar_image=avatar_image,
                avatar_participant_name="AI Interview Coach",
            )
            print("✅ Hedra avatar initialized")
        except Exception as e:
            print(f"⚠️ Failed to initialize Hedra avatar: {e}")
            avatar = None
    elif not os.getenv("HEDRA_API_KEY"):
        print("⚠️ HEDRA_API_KEY not set, avatar disabled")
    
    # Set up event handlers to capture conversation
    @session.on("user_speech_committed")
    def on_user_speech(speech):
        """Capture user's speech"""
        transcript.append({
            "role": "user",
            "content": speech.text,
            "timestamp": speech.timestamp if hasattr(speech, 'timestamp') else None
        })
        print(f"👤 User said: {speech.text[:100]}...")
    
    @session.on("agent_speech_committed")
    def on_agent_speech(speech):
        """Capture agent's speech"""
        nonlocal interview_complete
        
        transcript.append({
            "role": "assistant",
            "content": speech.text,
            "timestamp": speech.timestamp if hasattr(speech, 'timestamp') else None
        })
        print(f"🤖 Agent said: {speech.text[:100]}...")
        
        # Track questions asked (rough estimate based on agent turns)
        agent.questions_asked = len([t for t in transcript if t["role"] == "assistant"]) // 2
        
        # Check if interview is complete (agent said closing message)
        closing_keywords = ["thank you for completing", "you'll receive a detailed report", "have a great day", "we've covered all"]
        if any(keyword in speech.text.lower() for keyword in closing_keywords):
            interview_complete = True
            print(f"✅ Interview complete! Saving transcript and ending session...")
            
            # Create async task for saving transcript and disconnecting
            async def save_and_disconnect():
                await save_interview_transcript(session_id, transcript, agent.questions_asked)
                
                # Wait a moment for the message to be delivered
                import asyncio
                await asyncio.sleep(3)
                
                # Disconnect the room to end the interview
                await ctx.room.disconnect()
                print(f"🔚 Room disconnected. Interview session {session_id} ended.")
            
            # Schedule the async work
            import asyncio
            asyncio.create_task(save_and_disconnect())
    
    # Start the avatar if available
    if avatar:
        try:
            print("🎬 Starting Hedra avatar...")
            await avatar.start(session, room=ctx.room)
            print("✅ Hedra avatar started and joined the room")
        except Exception as e:
            print(f"⚠️ Failed to start avatar: {e}")
            avatar = None
    
    # Start the agent session
    # Note: The avatar publishes on behalf of the agent, but the agent participant still exists
    # The frontend filters out the agent participant to only show user + avatar
    # Transcriptions are enabled by default in AgentSession
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
    
    greeting = await session.generate_reply(instructions=greeting_instructions)
    transcript.append({
        "role": "assistant",
        "content": greeting if isinstance(greeting, str) else "Welcome to your interview!",
        "timestamp": None
    })
    
    print(f"✅ Agent greeted candidate in room: {room_name}")
    
    # Monitor room for disconnection and save transcript when interview ends
    @ctx.room.on("participant_disconnected")
    def on_participant_disconnected(participant):
        """Called when the candidate leaves the room"""
        if participant.identity == "agent" or participant.kind != "standard":
            return  # Don't trigger on agent disconnect
            
        print(f"📝 Participant {participant.identity} disconnected. Saving transcript...")
        
        # Create async task for saving transcript
        async def save_on_disconnect():
            await save_interview_transcript(session_id, transcript, agent.questions_asked)
            print(f"✅ Interview session {session_id} completed")
        
        # Schedule the async work
        import asyncio
        asyncio.create_task(save_on_disconnect())


if __name__ == "__main__":
    print("=" * 60)
    print("🎤 LiveKit AI Interview Agent with Hedra Avatar")
    print("=" * 60)
    print(f"LIVEKIT_URL: {os.getenv('LIVEKIT_URL', 'Not set')}")
    print(f"LIVEKIT_API_KEY: {'Set' if os.getenv('LIVEKIT_API_KEY') else 'Not set'}")
    print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print(f"HEDRA_API_KEY: {'Set' if os.getenv('HEDRA_API_KEY') else 'Not set'}")
    print(f"BACKEND_URL: {BACKEND_URL}")
    print("=" * 60)
    
    # Check if avatar.png exists
    avatar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "avatar.png")
    if os.path.exists(avatar_path):
        print(f"✅ Avatar image found: {avatar_path}")
    else:
        print(f"⚠️ Avatar image NOT found: {avatar_path}")
        print("   Avatar feature will be disabled")
    
    print("\nWaiting for interview sessions...")
    print("Listening for rooms: interview-*")
    print("Will fetch job_title/seniority from backend for each session")
    print("\nPress Ctrl+C to stop\n")
    
    agents.cli.run_app(server)

