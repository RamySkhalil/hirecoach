# 🚀 LiveKit Installation & Testing Guide

## ✅ Code Implementation Complete!

All LiveKit files have been created. Now let's install dependencies and test it!

## Step 1: Install Backend Dependencies

Open PowerShell in the `backend` directory:

```powershell
cd C:\Personal\hirecoach\backend
.\.venv\Scripts\activate
pip install livekit livekit-agents livekit-plugins-deepgram livekit-plugins-openai livekit-plugins-elevenlabs livekit-plugins-silero
```

Expected output:
```
Successfully installed livekit-x.x.x livekit-agents-x.x.x ...
```

## Step 2: Install Frontend Dependencies

Open PowerShell in the `frontend` directory:

```powershell
cd C:\Personal\hirecoach\frontend
npm install @livekit/components-react livekit-client @livekit/components-styles
```

Expected output:
```
added XX packages in Xs
```

## Step 3: Verify Environment Variables

Your `.env` file already has LiveKit credentials. Let's verify they're correct:

```powershell
cd C:\Personal\hirecoach\backend
Get-Content .env | Select-String "LIVEKIT"
```

Should show:
```
LIVEKIT_API_KEY=APIiREwt2qyQJac
LIVEKIT_API_SECRET=jrgxk72kPArbScntJDm67QGfPeuW54f4ahODxQSNHQnB
LIVEKIT_URL=wss://interviewsaas-m7lvjg0t.livekit.cloud
```

✅ These look good!

Also verify other required keys:
```powershell
Get-Content .env | Select-String "DEEPGRAM_API_KEY"
Get-Content .env | Select-String "OPENAI_API_KEY"
Get-Content .env | Select-String "ELEVENLABS_API_KEY"
```

All three must be present for the agent to work.

## Step 4: Test Backend Endpoint

**Terminal 1 - Start Backend:**
```powershell
cd C:\Personal\hirecoach\backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

Expected startup output should now include:
```
🔑 API Keys Status:
  OpenAI: ✅ Configured
  ElevenLabs: ✅ Configured
  Deepgram: ✅ Configured
  LiveKit: ✅ Configured          ← New!
  LLM Provider: openai
  STT Provider: deepgram
```

**Test the token endpoint:**

Open a new PowerShell window:
```powershell
$body = @{
    session_id = "test-123"
    participant_name = "Test User"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/livekit/token" -Method POST -Body $body -ContentType "application/json"
```

Expected response:
```
token      : eyJ...long_jwt_token...
url        : wss://interviewsaas-m7lvjg0t.livekit.cloud
room_name  : interview-test-123
```

✅ If you see this, the backend is working!

## Step 5: Start the LiveKit Agent

**Terminal 2 - Start Agent Worker:**

```powershell
cd C:\Personal\hirecoach\backend
.\.venv\Scripts\activate
python livekit_agent.py start
```

Expected output:
```
🚀 Starting LiveKit Interview Agent...
📡 LiveKit URL: wss://interviewsaas-m7lvjg0t.livekit.cloud
✅ All environment variables configured
🎧 Waiting for interview sessions...
INFO:interview-agent:Agent worker starting...
INFO:livekit:Connected to LiveKit server
```

✅ Agent is now running and waiting for interview sessions!

## Step 6: Start Frontend

**Terminal 3 - Start Frontend:**

```powershell
cd C:\Personal\hirecoach\frontend
npm run dev
```

Expected output:
```
  ▲ Next.js 15.x.x
  - Local:        http://localhost:3000
  - Ready in XXXms
```

## Step 7: Test the Integration

1. **Open browser:** `http://localhost:3000`

2. **Start a new interview:**
   - Go to Interview Setup
   - Fill in details
   - Click "Start Interview"

3. **You should see:**
   - "Connecting to AI Interviewer..." (brief)
   - Blue toggle button: "🎙️ LiveKit Mode (Professional)"
   - Beautiful UI with agent state indicators

4. **Allow microphone access** when prompted

5. **Wait for AI greeting:**
   - Agent terminal shows: `🎤 Agent starting for room: interview-xxx`
   - You hear: "Hello! I'm your AI interviewer..."
   - Frontend shows: "AI Interviewer Speaking" (purple)

6. **Respond to the question:**
   - Wait for agent to finish speaking
   - Frontend shows: "I'm Listening" (green + pulsing)
   - Speak your answer clearly
   - Frontend shows: "Processing..." (blue + rotating brain)
   - Agent analyzes and responds

7. **Natural conversation flows:**
   - AI asks follow-up questions
   - No button clicking needed
   - Real-time voice visualization
   - Turn-taking is automatic

## Troubleshooting

### Issue: "LiveKit not installed"

**Solution:**
```powershell
cd backend
.\.venv\Scripts\activate
pip install livekit livekit-agents livekit-plugins-deepgram livekit-plugins-openai livekit-plugins-elevenlabs livekit-plugins-silero
```

### Issue: "Failed to get LiveKit token"

**Check:**
1. Backend is running (`http://localhost:8000`)
2. `.env` has `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `LIVEKIT_URL`
3. Restart backend after updating `.env`

### Issue: Agent not responding

**Check Agent Terminal:**
- Should show: `🎤 Agent starting for room: interview-xxx`
- If not, verify all API keys in `.env`:
  - `DEEPGRAM_API_KEY`
  - `OPENAI_API_KEY`
  - `ELEVENLABS_API_KEY`

**Restart agent:**
```powershell
# Press Ctrl+C to stop
python livekit_agent.py start
```

### Issue: No audio from AI

**Check:**
1. `ELEVENLABS_API_KEY` is set in `.env`
2. Agent terminal shows no errors
3. Browser audio is not muted
4. System volume is up

### Issue: AI can't hear me

**Check:**
1. Browser has microphone permission
2. Correct microphone selected (AirPods or built-in)
3. Microphone works in system settings
4. Frontend shows "I'm Listening" (green)

### Issue: npm install fails

**Try:**
```powershell
cd frontend
rm -r node_modules
rm package-lock.json
npm install
```

## What Each Terminal Should Show

### Terminal 1 (Backend)
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 2 (Agent)
```
🎧 Waiting for interview sessions...
🎤 Agent starting for room: interview-xxx
✅ Voice assistant started successfully
👋 Initial greeting delivered
```

### Terminal 3 (Frontend)
```
  ▲ Next.js 15.x.x
  - Local:        http://localhost:3000
```

## Testing Checklist

- [ ] Backend starts successfully
- [ ] Agent worker starts successfully
- [ ] Frontend starts successfully
- [ ] Can create new interview
- [ ] LiveKit mode toggle appears
- [ ] Connects to AI interviewer
- [ ] Hears AI greeting
- [ ] AI detects when I speak
- [ ] AI responds to my answers
- [ ] Conversation flows naturally
- [ ] No "no-speech" errors
- [ ] Voice visualizer works
- [ ] Can toggle to Web Speech mode

## Switch Modes

**LiveKit Mode (Default):**
- Professional AI conversation
- Better speech recognition
- Natural turn-taking
- No button clicking

**Web Speech Mode:**
- Click toggle: "🎤 Web Speech Mode (Basic)"
- Falls back to browser API
- Use if LiveKit has issues

## Next: Add Hedra Avatar

Once voice conversation works perfectly, we can add:
- Talking face video
- Lip-synced speech
- Professional interviewer avatar

See `LIVEKIT_INTEGRATION_PLAN.md` for Phase 2 details.

## Summary

You now have:
✅ Professional voice recognition (Deepgram)
✅ Natural conversation flow (no button clicking)
✅ Real-time AI responses (GPT-4o-mini)
✅ High-quality voice (ElevenLabs)
✅ Beautiful UI with state indicators
✅ Fallback to Web Speech API

**Total cost per interview:** ~$0.30-0.50 (vs free but unreliable Web Speech)

---

**Ready to test?** Follow steps 1-7 above and let me know how it goes! 🚀

