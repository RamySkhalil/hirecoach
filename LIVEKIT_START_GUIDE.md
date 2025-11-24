# 🚀 How to Start LiveKit Interview System

## The Problem

You're seeing the LiveKit interface but:
- ❌ No voice from AI
- ❌ Microphone doesn't work
- ❌ Nothing happens when you speak

## The Reason

**You need to start the LiveKit Agent Worker!**

The system has 3 parts:
1. ✅ Backend API (running)
2. ❌ **LiveKit Agent** (NOT running - this is the problem!)
3. ✅ Frontend (running)

Without the agent, there's no AI to talk to you!

## Quick Solution

### Option 1: Use the Startup Script (Easiest)

Double-click: **`START_LIVEKIT_INTERVIEW.bat`**

This will open 3 terminal windows automatically:
- Backend Server
- LiveKit Agent (the missing piece!)
- Frontend Server

### Option 2: Manual Start (3 Terminals)

**Terminal 1 - Backend:**
```powershell
cd C:\Personal\hirecoach\backend
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

**Terminal 2 - LiveKit Agent:** ⭐ **THIS IS THE IMPORTANT ONE!**
```powershell
cd C:\Personal\hirecoach\backend
.\.venv\Scripts\python livekit_agent.py start
```

**You should see:**
```
🚀 Starting LiveKit Interview Agent...
📡 LiveKit URL: wss://interviewsaas-m7lvjg0t.livekit.cloud
✅ All environment variables configured
🎧 Waiting for interview sessions...
INFO:interview-agent:Agent worker starting...
INFO:livekit:Connected to LiveKit server
```

**Terminal 3 - Frontend:**
```powershell
cd C:\Personal\hirecoach\frontend
npm run dev
```

## How It Works

```
You speak
    ↓
LiveKit Room (cloud)
    ↓
Agent Worker (YOUR COMPUTER) ← This needs to be running!
    ↓ Uses:
    - Deepgram (hears you)
    - OpenAI GPT (thinks)
    - ElevenLabs (speaks back)
    ↓
LiveKit Room (cloud)
    ↓
You hear AI response
```

## What You Should See

### In Agent Terminal:
```
🎧 Waiting for interview sessions...
🎤 Agent starting for room: interview-xxx
✅ Voice assistant started successfully
👋 Initial greeting delivered
```

### In Frontend:
- "AI Interviewer Speaking" (purple)
- You hear: "Hello! I'm your AI interviewer..."
- Then: "I'm Listening" (green)
- You speak
- "Processing..." (blue)
- AI responds

## Troubleshooting

### "Module not found" errors in agent terminal

Install dependencies:
```powershell
cd backend
.\.venv\Scripts\python -m pip install livekit-agents livekit-plugins-deepgram livekit-plugins-openai livekit-plugins-elevenlabs livekit-plugins-silero
```

### Agent starts but no audio

Check `.env` has all keys:
```env
DEEPGRAM_API_KEY=...
OPENAI_API_KEY=...
ELEVENLABS_API_KEY=...
LIVEKIT_URL=wss://interviewsaas-m7lvjg0t.livekit.cloud
LIVEKIT_API_KEY=APIiREwt2qyQJac
LIVEKIT_API_SECRET=jrgxk72kPArbScntJDm67QGfPeuW54f4ahODxQSNHQnB
```

### "Agent not responding"

Restart the agent:
1. Press Ctrl+C in agent terminal
2. Run: `python livekit_agent.py start`
3. Refresh browser

### Frontend shows "Connecting..."

1. Make sure agent terminal shows "Connected to LiveKit server"
2. Check backend terminal has no errors
3. Refresh browser page

## Quick Test Checklist

- [ ] Backend running (Terminal 1)
- [ ] **Agent running** (Terminal 2) ⭐ **Most important!**
- [ ] Frontend running (Terminal 3)
- [ ] Agent shows "Waiting for interview sessions..."
- [ ] Open http://localhost:3000
- [ ] Start interview
- [ ] See "Connecting to AI Interviewer..."
- [ ] Agent terminal shows "Agent starting for room..."
- [ ] Hear AI greeting
- [ ] See "I'm Listening" (green)
- [ ] Speak
- [ ] AI responds

## Summary

**The fix:** Start the LiveKit Agent Worker!

**Easiest way:** Run `START_LIVEKIT_INTERVIEW.bat`

**Or manually run in Terminal 2:**
```powershell
cd backend
.\.venv\Scripts\python livekit_agent.py start
```

Once the agent is running, voice conversation will work! 🎤✅

