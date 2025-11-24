# 🎥 LiveKit + Hedra Avatar Integration Plan

## Overview

Replace the current Web Speech API with **LiveKit Agents** for:
- ✅ Professional real-time voice conversation
- ✅ Better speech recognition (using Deepgram via LiveKit)
- ✅ Natural conversation flow
- ✅ Future: Hedra talking avatar integration
- ✅ Production-ready infrastructure

## Current vs. Future Architecture

### Current System
```
User speaks → Web Speech API → Text appears → User submits
                ↓
         Google Speech Recognition
         (Free, basic, no avatar)
```

### Future System (LiveKit + Hedra)
```
User speaks → LiveKit Room → Deepgram STT → LLM Processing → ElevenLabs TTS → Hedra Avatar
                ↓                                ↓                              ↓
         Professional Audio         AI Interviewer           Talking Face
         Real-time transcription    Natural conversation     Lip-synced video
```

## Your Existing Setup

✅ **LiveKit Cloud Account**
- URL: `wss://interviewsaas-m7lvjg0t.livekit.cloud`
- API Key: `APIiREwt2qyQJac`
- API Secret: `jrgxk72kPArbScntJDm67QGfPeuW54f4ahODxQSNHQnB`

✅ **Already Have**
- Deepgram API key (for STT via LiveKit)
- ElevenLabs API key (for TTS)
- OpenAI API key (for AI responses)

🎯 **Need to Add**
- Hedra API key (for talking avatar) - Later phase

## Implementation Phases

### Phase 1: LiveKit Voice Agent (Week 1)
**Goal:** Replace Web Speech API with LiveKit Agents

**What you get:**
- Professional voice conversation
- Better speech recognition (Deepgram via LiveKit)
- Real-time transcription display
- Natural turn-taking
- Voice activity detection

**Components:**
1. Backend: LiveKit token generation endpoint
2. Backend: Python LiveKit Agent worker
3. Frontend: LiveKit React components
4. Interview flow: Real-time voice conversation

### Phase 2: Hedra Avatar Integration (Week 2)
**Goal:** Add talking avatar video

**What you get:**
- AI interviewer with realistic face
- Lip-synced speech
- Natural facial expressions
- Eye contact and head movements

**Components:**
1. Hedra API integration
2. Video streaming via LiveKit
3. Avatar persona configuration
4. Real-time video rendering

### Phase 3: Polish & Production (Week 3)
**Goal:** Production-ready system

**What you get:**
- Error handling & reconnection
- Recording & playback
- Analytics & monitoring
- Mobile support

## Phase 1 Implementation Details

### Step 1: Install Dependencies

**Backend:**
```bash
cd backend
pip install livekit livekit-agents livekit-plugins-deepgram livekit-plugins-openai livekit-plugins-elevenlabs
```

**Frontend:**
```bash
cd frontend
npm install @livekit/components-react livekit-client @livekit/components-styles
```

### Step 2: Backend Token Generation

**New endpoint:** `backend/app/routes/livekit.py`

```python
from fastapi import APIRouter, HTTPException
from livekit import api
from app.config import settings

router = APIRouter(prefix="/livekit", tags=["livekit"])

@router.post("/token")
async def create_token(session_id: str, participant_name: str):
    """Generate LiveKit access token for interview session"""
    try:
        token = api.AccessToken(
            settings.livekit_api_key,
            settings.livekit_api_secret
        )
        
        token.with_identity(participant_name)
        token.with_name(participant_name)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=f"interview-{session_id}",
            can_publish=True,
            can_subscribe=True,
        ))
        
        return {
            "token": token.to_jwt(),
            "url": settings.livekit_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 3: Backend Agent Worker

**New file:** `backend/agent_worker.py`

```python
import asyncio
from livekit import agents
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, openai, elevenlabs

async def entrypoint(ctx: JobContext):
    """
    LiveKit Agent that:
    1. Listens to user speech (Deepgram STT)
    2. Processes with AI (OpenAI)
    3. Responds with voice (ElevenLabs TTS)
    """
    
    initial_message = "Hello! I'm your AI interviewer. Let's begin the interview. Please tell me about yourself."
    
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # Get interview context from room metadata
    room_name = ctx.room.name
    session_id = room_name.replace("interview-", "")
    
    # Initialize AI assistant
    assistant = agents.VoiceAssistant(
        vad=agents.silero.VAD.load(),
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=elevenlabs.TTS(),
        chat_ctx=openai.ChatContext().append(
            role="system",
            text=(
                "You are an AI interviewer conducting a job interview. "
                "Ask relevant questions based on the conversation. "
                "Be professional, friendly, and encouraging. "
                "Listen carefully and provide thoughtful follow-up questions."
            )
        )
    )
    
    assistant.start(ctx.room)
    
    await assistant.say(initial_message, allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        ),
    )
```

### Step 4: Frontend LiveKit Room Component

**New file:** `frontend/components/LiveKitInterviewRoom.tsx`

```typescript
"use client";

import { useEffect, useState } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  StartAudio,
  useVoiceAssistant,
  BarVisualizer,
  AgentState,
} from "@livekit/components-react";
import "@livekit/components-styles";

interface LiveKitInterviewRoomProps {
  sessionId: string;
  participantName: string;
  onTranscript: (text: string, isFinal: boolean) => void;
  onAgentResponse: (text: string) => void;
}

export default function LiveKitInterviewRoom({
  sessionId,
  participantName,
  onTranscript,
  onAgentResponse
}: LiveKitInterviewRoomProps) {
  const [token, setToken] = useState<string>("");
  const [liveKitUrl, setLiveKitUrl] = useState<string>("");

  useEffect(() => {
    // Get LiveKit token from backend
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/livekit/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        participant_name: participantName,
      }),
    })
      .then(res => res.json())
      .then(data => {
        setToken(data.token);
        setLiveKitUrl(data.url);
      })
      .catch(err => console.error("Failed to get token:", err));
  }, [sessionId, participantName]);

  if (!token || !liveKitUrl) {
    return <div>Connecting to interview room...</div>;
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
      <InterviewUI 
        onTranscript={onTranscript}
        onAgentResponse={onAgentResponse}
      />
      <RoomAudioRenderer />
      <StartAudio label="Click to enable audio" />
    </LiveKitRoom>
  );
}

function InterviewUI({ onTranscript, onAgentResponse }: any) {
  const { state, audioTrack } = useVoiceAssistant();

  useEffect(() => {
    // Listen to transcription events
    const handleTranscript = (event: any) => {
      onTranscript(event.text, event.isFinal);
    };

    // Listen to agent responses
    const handleAgentMessage = (event: any) => {
      onAgentResponse(event.text);
    };

    // Attach event listeners
    // (Implementation depends on LiveKit SDK version)

    return () => {
      // Cleanup
    };
  }, [onTranscript, onAgentResponse]);

  return (
    <div className="flex flex-col items-center justify-center h-full space-y-6">
      {/* Agent State */}
      <div className="text-center">
        {state === AgentState.LISTENING && (
          <p className="text-green-600 font-medium">🎤 Listening...</p>
        )}
        {state === AgentState.THINKING && (
          <p className="text-blue-600 font-medium">🤔 Thinking...</p>
        )}
        {state === AgentState.SPEAKING && (
          <p className="text-indigo-600 font-medium">🗣️ Speaking...</p>
        )}
      </div>

      {/* Voice Visualizer */}
      {audioTrack && (
        <div className="w-full max-w-md">
          <BarVisualizer
            state={state}
            barCount={5}
            trackRef={audioTrack}
            className="h-32"
          />
        </div>
      )}

      {/* Status */}
      <p className="text-sm text-gray-500">
        Speak naturally - the AI interviewer is listening
      </p>
    </div>
  );
}
```

### Step 5: Update Interview Session Page

Replace `ContinuousVoiceInput` with `LiveKitInterviewRoom`:

```typescript
// In frontend/app/interview/session/[sessionId]/page.tsx

import LiveKitInterviewRoom from "@/components/LiveKitInterviewRoom";

// Replace the voice input section with:
<LiveKitInterviewRoom
  sessionId={sessionId}
  participantName="Candidate"
  onTranscript={(text, isFinal) => {
    if (isFinal) {
      setAnswer(prev => prev + " " + text);
    }
  }}
  onAgentResponse={(text) => {
    // Add agent message to chat
    setMessages(prev => [...prev, {
      role: "agent",
      content: text,
      timestamp: new Date()
    }]);
  }}
/>
```

### Step 6: Start Agent Worker

```bash
cd backend
python agent_worker.py start
```

## Phase 2: Hedra Avatar Integration

### What is Hedra?

**Hedra** creates realistic talking avatars from:
- Audio input (your AI's voice)
- Base image (professional interviewer photo)
- Returns: Lip-synced video with natural expressions

### How It Works

```
Interview Question (text)
  ↓
ElevenLabs TTS (audio)
  ↓
Hedra API (audio + base image)
  ↓
Talking Avatar Video
  ↓
Stream via LiveKit
  ↓
User sees AI interviewer speaking
```

### Implementation

**Backend:** `backend/app/services/hedra_service.py`

```python
import httpx
from app.config import settings

class HedraService:
    @staticmethod
    async def generate_talking_avatar(audio_url: str, base_image_url: str):
        """
        Generate talking avatar video using Hedra API
        
        Args:
            audio_url: URL to ElevenLabs audio
            base_image_url: URL to interviewer base image
            
        Returns:
            Video URL of talking avatar
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.hedra.com/v1/characters",
                headers={
                    "Authorization": f"Bearer {settings.hedra_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "audio_source": audio_url,
                    "avatar_image": base_image_url,
                    "aspect_ratio": "16:9"
                }
            )
            
            data = response.json()
            job_id = data["id"]
            
            # Poll for completion
            while True:
                status = await client.get(
                    f"https://api.hedra.com/v1/characters/{job_id}",
                    headers={"Authorization": f"Bearer {settings.hedra_api_key}"}
                )
                
                status_data = status.json()
                if status_data["status"] == "completed":
                    return status_data["video_url"]
                
                await asyncio.sleep(1)
```

**LiveKit Agent with Hedra:**

```python
# Modify agent_worker.py

async def entrypoint(ctx: JobContext):
    # ... existing setup ...
    
    # When agent speaks:
    async def on_agent_speech(text: str, audio_data: bytes):
        # 1. Generate avatar video with Hedra
        audio_url = upload_audio_to_storage(audio_data)
        video_url = await HedraService.generate_talking_avatar(
            audio_url=audio_url,
            base_image_url=settings.interviewer_avatar_image
        )
        
        # 2. Stream video to LiveKit room
        video_track = VideoTrack()
        await video_track.publish_from_url(video_url)
        await ctx.room.local_participant.publish_track(video_track)
    
    # Attach to assistant
    assistant.on("speech", on_agent_speech)
```

### Frontend Video Display

```typescript
// Add video rendering to LiveKitInterviewRoom.tsx

import { useTrack } from "@livekit/components-react";
import { Track } from "livekit-client";

function InterviewUI() {
  const videoTrack = useTrack(Track.Source.Camera);
  
  return (
    <div>
      {videoTrack && (
        <video
          ref={videoTrack.ref}
          className="rounded-lg w-full max-w-2xl"
          autoPlay
        />
      )}
      
      {/* If no video, show static avatar */}
      {!videoTrack && (
        <img 
          src="/interviewer-avatar.jpg"
          className="rounded-lg w-full max-w-2xl"
        />
      )}
    </div>
  );
}
```

## Benefits of LiveKit + Hedra

| Feature | Web Speech API | LiveKit + Hedra |
|---------|----------------|-----------------|
| Speech Recognition | Basic (Google) | Professional (Deepgram) |
| Voice Quality | N/A | High-quality TTS |
| Visual Avatar | None | Realistic talking face |
| Conversation Flow | Manual submit | Natural turn-taking |
| Production Ready | Limited | Enterprise-grade |
| Latency | Variable | Optimized |
| Scalability | Browser-dependent | Cloud infrastructure |
| Recording | Manual | Built-in |
| Cost | Free (limited) | Paid (professional) |

## Cost Estimation

### LiveKit Cloud
- **Free tier:** 50GB egress/month
- **Starter:** $99/month for 500GB
- **Your usage:** ~1GB per interview hour
- **Estimate:** $0.20-0.50 per interview

### Hedra API
- **Cost:** ~$0.05 per 10 seconds of video
- **Interview:** 20 questions × 10 sec each = $1.00
- **Estimate:** $1.00 per interview

### Total Cost Per Interview
- Web Speech API: $0 (current)
- LiveKit Voice: $0.20-0.50
- LiveKit + Hedra: $1.20-1.50

**Worth it?** Yes, for professional interviews!

## Migration Strategy

### Option 1: Gradual Migration (Recommended)
1. Keep Web Speech API as default
2. Add "Professional Mode" toggle
3. Professional Mode uses LiveKit + Hedra
4. Collect user feedback
5. Make LiveKit default once stable

### Option 2: Complete Replacement
1. Replace all voice input with LiveKit
2. Higher quality but immediate commitment
3. Requires thorough testing

### Option 3: Hybrid Approach
1. Use LiveKit for voice (better recognition)
2. Add Hedra avatar later (Phase 2)
3. Best of both worlds

## Next Steps

### Immediate (This Week)
1. ✅ You already have LiveKit credentials
2. Install LiveKit dependencies
3. Create token generation endpoint
4. Build basic LiveKit agent
5. Test voice conversation

### Short Term (Next Week)
1. Replace ContinuousVoiceInput with LiveKitRoom
2. Implement interview flow with agent
3. Add transcription display
4. Test with real interviews

### Future (Month 2)
1. Get Hedra API access
2. Integrate avatar generation
3. Stream video via LiveKit
4. Polish UX and add animations

## Sample Timeline

**Week 1: LiveKit Voice**
- Day 1-2: Backend setup (token, agent worker)
- Day 3-4: Frontend integration
- Day 5: Testing & bug fixes

**Week 2: Interview Flow**
- Day 1-2: Agent conversation logic
- Day 3-4: Question sequencing
- Day 5: Evaluation integration

**Week 3: Hedra Avatar**
- Day 1-2: Hedra API integration
- Day 3-4: Video streaming
- Day 5: Polish & animations

**Week 4: Production**
- Day 1-2: Error handling
- Day 3-4: Performance optimization
- Day 5: Launch!

## Do You Want to Proceed?

I can help you implement:

1. **Phase 1 only:** LiveKit voice (better than Web Speech API)
2. **Phase 1 + 2:** LiveKit + Hedra (full talking avatar)
3. **Gradual migration:** Both systems side-by-side

**Which approach do you prefer?** Let me know and I'll start building! 🚀

