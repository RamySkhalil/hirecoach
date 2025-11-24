# 🚀 LiveKit Quick Start - Replace Web Speech API

## What We're Building

Replace the problematic Web Speech API with **LiveKit Agents** for professional voice interviews.

**Result:** Natural voice conversation without clicking buttons, with much better speech recognition.

## Step-by-Step Implementation

### Step 1: Install Backend Dependencies

```bash
cd backend
pip install livekit livekit-agents livekit-plugins-deepgram livekit-plugins-openai livekit-plugins-elevenlabs
```

### Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install @livekit/components-react livekit-client @livekit/components-styles
```

### Step 3: Update Backend Config

Add to `backend/app/config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # LiveKit Settings
    livekit_url: str = ""
    livekit_api_key: str = ""
    livekit_api_secret: str = ""
```

### Step 4: Create Token Endpoint

Create `backend/app/routes/livekit_routes.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from livekit import api
from app.config import settings

router = APIRouter(prefix="/livekit", tags=["livekit"])

class TokenRequest(BaseModel):
    session_id: str
    participant_name: str

@router.post("/token")
async def create_token(request: TokenRequest):
    """Generate LiveKit access token for interview session"""
    if not settings.livekit_api_key or not settings.livekit_api_secret:
        raise HTTPException(status_code=500, detail="LiveKit not configured")
    
    try:
        token = api.AccessToken(
            settings.livekit_api_key,
            settings.livekit_api_secret
        )
        
        token.with_identity(request.participant_name)
        token.with_name(request.participant_name)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=f"interview-{request.session_id}",
            can_publish=True,
            can_subscribe=True,
        ))
        
        return {
            "token": token.to_jwt(),
            "url": settings.livekit_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")
```

### Step 5: Register Route in Main

Update `backend/app/main.py`:

```python
from app.routes import interview, media, cv, cv_rewriter, livekit_routes

# Include routers
app.include_router(interview.router)
app.include_router(media.router)
app.include_router(cv.router)
app.include_router(cv_rewriter.router)
app.include_router(livekit_routes.router)  # ADD THIS
```

### Step 6: Create Simple Agent Worker

Create `backend/livekit_agent.py`:

```python
"""
LiveKit Voice Agent for Interview Platform
Handles real-time voice conversation with candidates
"""
import asyncio
import logging
from livekit import agents, rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, openai, elevenlabs
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("interview-agent")

async def entrypoint(ctx: JobContext):
    """
    Main entry point for the voice agent.
    Handles voice conversation with interview candidates.
    """
    logger.info(f"Agent starting for room: {ctx.room.name}")
    
    # Connect to the room
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # Initial greeting
    initial_message = (
        "Hello! I'm your AI interviewer. "
        "I'll be asking you some questions today. "
        "Please speak clearly and take your time with your answers. "
        "Let's begin!"
    )
    
    # Create voice assistant with plugins
    assistant = agents.VoiceAssistant(
        vad=agents.silero.VAD.load(),  # Voice activity detection
        stt=deepgram.STT(),  # Speech-to-text
        llm=openai.LLM(model="gpt-4o-mini"),  # Language model
        tts=elevenlabs.TTS(),  # Text-to-speech
        chat_ctx=openai.ChatContext().append(
            role="system",
            text=(
                "You are a professional AI interviewer conducting a job interview. "
                "Ask relevant follow-up questions based on the candidate's responses. "
                "Be encouraging, professional, and help the candidate showcase their skills. "
                "Keep questions concise and clear."
            )
        )
    )
    
    # Start the assistant
    assistant.start(ctx.room)
    
    # Say initial greeting
    await assistant.say(initial_message, allow_interruptions=True)
    
    logger.info("Agent started successfully")

if __name__ == "__main__":
    # Run the agent worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        ),
    )
```

### Step 7: Create Frontend Component

Create `frontend/components/LiveKitInterview.tsx`:

```typescript
"use client";

import { useEffect, useState } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useVoiceAssistant,
  BarVisualizer,
  AgentState,
} from "@livekit/components-react";
import "@livekit/components-styles";
import { Loader2, Mic, MicOff, Brain } from "lucide-react";
import { motion } from "framer-motion";

interface LiveKitInterviewProps {
  sessionId: string;
  onTranscript?: (text: string, isFinal: boolean) => void;
}

export default function LiveKitInterview({
  sessionId,
  onTranscript
}: LiveKitInterviewProps) {
  const [token, setToken] = useState<string>("");
  const [liveKitUrl, setLiveKitUrl] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Get LiveKit token from backend
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/livekit/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        participant_name: "Candidate",
      }),
    })
      .then(res => {
        if (!res.ok) throw new Error("Failed to get token");
        return res.json();
      })
      .then(data => {
        setToken(data.token);
        setLiveKitUrl(data.url);
        setLoading(false);
      })
      .catch(err => {
        console.error("Token error:", err);
        setError(err.message);
        setLoading(false);
      });
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <p className="ml-3 text-gray-600">Connecting to interview room...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800 font-semibold">Connection Error</p>
        <p className="text-red-600 text-sm mt-1">{error}</p>
      </div>
    );
  }

  return (
    <LiveKitRoom
      token={token}
      serverUrl={liveKitUrl}
      connect={true}
      audio={true}
      video={false}
      className="h-full"
    >
      <InterviewUI onTranscript={onTranscript} />
      <RoomAudioRenderer />
    </LiveKitRoom>
  );
}

function InterviewUI({ onTranscript }: { onTranscript?: (text: string, isFinal: boolean) => void }) {
  const { state, audioTrack } = useVoiceAssistant();

  return (
    <div className="flex flex-col items-center justify-center h-full space-y-8 p-6">
      {/* Agent State Indicator */}
      <motion.div
        animate={{
          scale: state === AgentState.SPEAKING ? [1, 1.1, 1] : 1,
        }}
        transition={{
          duration: 1,
          repeat: state === AgentState.SPEAKING ? Infinity : 0,
        }}
        className="text-center"
      >
        {state === AgentState.LISTENING && (
          <div className="flex items-center gap-3">
            <div className="p-4 rounded-full bg-gradient-to-r from-green-500 to-emerald-600 animate-pulse">
              <Mic className="h-8 w-8 text-white" />
            </div>
            <div>
              <p className="text-xl font-semibold text-green-600">Listening</p>
              <p className="text-sm text-gray-500">Speak your answer...</p>
            </div>
          </div>
        )}
        
        {state === AgentState.THINKING && (
          <div className="flex items-center gap-3">
            <div className="p-4 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600">
              <Brain className="h-8 w-8 text-white animate-pulse" />
            </div>
            <div>
              <p className="text-xl font-semibold text-blue-600">Thinking</p>
              <p className="text-sm text-gray-500">Processing your response...</p>
            </div>
          </div>
        )}
        
        {state === AgentState.SPEAKING && (
          <div className="flex items-center gap-3">
            <div className="p-4 rounded-full bg-gradient-to-r from-purple-500 to-pink-600">
              <Mic className="h-8 w-8 text-white" />
            </div>
            <div>
              <p className="text-xl font-semibold text-purple-600">AI Interviewer Speaking</p>
              <p className="text-sm text-gray-500">Listen to the question...</p>
            </div>
          </div>
        )}

        {state === AgentState.IDLE && (
          <div className="flex items-center gap-3">
            <div className="p-4 rounded-full bg-gray-300">
              <MicOff className="h-8 w-8 text-gray-600" />
            </div>
            <div>
              <p className="text-xl font-semibold text-gray-600">Ready</p>
              <p className="text-sm text-gray-500">Waiting to start...</p>
            </div>
          </div>
        )}
      </motion.div>

      {/* Voice Visualizer */}
      {audioTrack && (
        <div className="w-full max-w-md">
          <BarVisualizer
            state={state}
            barCount={7}
            trackRef={audioTrack}
            className="h-32"
          />
        </div>
      )}

      {/* Tips */}
      <div className="text-center max-w-md space-y-2">
        <p className="text-sm text-gray-600">
          💡 <strong>Tip:</strong> Speak naturally and clearly
        </p>
        <p className="text-xs text-gray-400">
          The AI will wait for you to finish speaking before asking the next question
        </p>
      </div>
    </div>
  );
}
```

### Step 8: Update Interview Page

Modify `frontend/app/interview/session/[sessionId]/page.tsx`:

Add import at top:
```typescript
import LiveKitInterview from "@/components/LiveKitInterview";
```

Replace the `ContinuousVoiceInput` section with:
```typescript
{/* Replace the entire input area section with: */}
<div className="border-t border-gray-200 p-4 bg-gray-50">
  <LiveKitInterview
    sessionId={sessionId}
    onTranscript={(text, isFinal) => {
      if (isFinal) {
        // Add to messages when complete
        setMessages(prev => [...prev, {
          role: "user",
          content: text,
          timestamp: new Date()
        }]);
      }
    }}
  />
</div>
```

### Step 9: Start the Agent Worker

Open a NEW terminal:

```bash
cd backend
python livekit_agent.py start
```

You should see:
```
INFO:interview-agent:Agent worker starting...
INFO:interview-agent:Connected to LiveKit server
INFO:interview-agent:Waiting for jobs...
```

### Step 10: Start Backend & Frontend

**Terminal 1 - Backend:**
```bash
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Agent Worker:**
```bash
cd backend
.\.venv\Scripts\activate
python livekit_agent.py start
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 11: Test It!

1. Go to `http://localhost:3000`
2. Start a new interview
3. You should see "Connecting to interview room..."
4. Then the AI will greet you with voice
5. Speak your answer - it will transcribe in real-time
6. AI responds with next question automatically

## What You Get

✅ **No more "no-speech" errors** - Deepgram is much better  
✅ **Natural conversation** - No button clicking  
✅ **Better recognition** - Professional-grade STT  
✅ **Real-time feedback** - See agent state (listening/thinking/speaking)  
✅ **Voice visualizer** - Cool audio bars  
✅ **Auto turn-taking** - AI waits for you to finish  

## Troubleshooting

### "Failed to get token"
- Check `.env` has `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
- Restart backend after updating `.env`

### Agent not responding
- Make sure `livekit_agent.py` is running
- Check agent terminal for errors
- Verify Deepgram/ElevenLabs keys in `.env`

### No audio
- Click "Start Audio" button in browser
- Check browser microphone permissions
- Verify AirPods/mic is selected as input

## Next: Add Hedra Avatar

Once this works, we can add Hedra to show a talking face! 🎭

**Want me to implement this now?** I can create all the files and guide you through testing! 🚀

