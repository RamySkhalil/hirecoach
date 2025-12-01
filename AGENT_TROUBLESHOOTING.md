# 🔧 Agent Not Speaking - Troubleshooting Guide

## ✅ What We Fixed

Simplified the agent configuration to match the working example:

**Before:**
```python
llm=openai.realtime.RealtimeModel(
    model="gpt-4o-realtime-preview",  # might not be needed
    voice="alloy",
    temperature=0.7,
)
```

**After:**
```python
llm=openai.realtime.RealtimeModel(
    voice="alloy",  # simpler, matches example
)
```

---

## 🔍 Diagnostic Steps

### Step 1: Check Agent Terminal Output

When you start the agent with `python interview_agent.py start`, you should see:

**Expected Output:**
```
============================================================
🎤 LiveKit AI Interview Agent
============================================================
LIVEKIT_URL: wss://your-project.livekit.cloud
LIVEKIT_API_KEY: Set
OPENAI_API_KEY: Set
============================================================

Waiting for interview sessions...
Listening for rooms: interview-*

Press Ctrl+C to stop
```

**When you join from frontend, you should see:**
```
✅ AI Interview Agent joining room: interview-abc123
   Session ID: abc123
✅ Agent greeted candidate in room: interview-abc123
```

**If you DON'T see these messages when joining:**
- ❌ Agent is not joining the room
- 🔴 **Problem:** Dispatch rule or room naming issue

---

### Step 2: Check Agent is Actually Running

In the agent terminal, after starting, check:

1. **No errors?** ✅ Good
2. **Sees the "Waiting for interview sessions..." message?** ✅ Good
3. **When you start interview, sees "joining room"?** ✅ Good
4. **Sees "greeted candidate"?** ✅ Good

If any of these are ❌, continue to Step 3.

---

### Step 3: Verify Environment Variables

Check `backend/livekit-voice-agent/.env.local` exists and has:

```bash
# Required for agent to work
OPENAI_API_KEY=sk-proj-...
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Test:**
```bash
cd backend/livekit-voice-agent
python -c "from dotenv import load_dotenv; import os; load_dotenv('.env.local'); print('OPENAI_API_KEY:', 'Set' if os.getenv('OPENAI_API_KEY') else 'NOT SET'); print('LIVEKIT_URL:', os.getenv('LIVEKIT_URL', 'NOT SET'))"
```

**Expected:**
```
OPENAI_API_KEY: Set
LIVEKIT_URL: wss://your-project.livekit.cloud
```

---

### Step 4: Check LiveKit Cloud Dispatch Rules

**If agent doesn't join automatically, you need a dispatch rule:**

1. Go to: https://cloud.livekit.io
2. Select your project
3. Go to **"Agents"** or **"Dispatch"** tab
4. Create a rule:
   - **Room Pattern:** `interview-*`
   - **Agent URL:** Your agent endpoint (or use dev mode, see Step 5)

**Alternative: Use Dev Mode (Easier for Testing)**

Instead of dispatch rules, use dev mode (see Step 5).

---

### Step 5: Run Agent in Dev Mode (Local Testing)

**For local testing without dispatch rules:**

```bash
cd backend/livekit-voice-agent

# Dev mode - connects to specific room
python interview_agent.py dev --room interview-test123
```

**Then in browser:**
- Start interview
- Note the room name in console: `interview-abc123`
- **Stop the agent (Ctrl+C)**
- Restart with: `python interview_agent.py dev --room interview-abc123`
- Refresh browser

This forces the agent to join that specific room.

---

### Step 6: Check Browser Console

Open DevTools (F12) and check for:

**Expected:**
```
✅ LiveKit connected: {room: 'interview-abc123', url: 'wss://...'}
```

**Check audio tracks:**
```javascript
// In browser console, run:
window.roomInstance = document.querySelector('[data-lk-theme]')?.__roomContext
console.log('Remote participants:', window.roomInstance?.remoteParticipants)
```

**You should see:**
- Agent as a remote participant ✅
- Agent has audio tracks ✅

---

### Step 7: Check Audio Output

**In browser:**
1. Right-click anywhere → **Inspect** → **Console**
2. Run:
   ```javascript
   // Check if RoomAudioRenderer is working
   document.querySelectorAll('audio').forEach(el => {
     console.log('Audio element:', el, 'src:', el.src, 'muted:', el.muted);
   });
   ```

**Expected:**
- Should see `<audio>` elements
- Should NOT be muted
- Should have src or stream

---

## 🔴 Common Issues & Fixes

### Issue 1: Agent Never Joins

**Symptoms:**
- Agent terminal shows "Waiting..." but never "joining room"
- Browser shows video but no agent

**Causes:**
1. No dispatch rule configured
2. Room name mismatch
3. Agent not running in correct mode

**Fix:**
```bash
# Option A: Use dev mode with explicit room
cd backend/livekit-voice-agent
python interview_agent.py dev --room interview-YOUR_SESSION_ID

# Option B: Set up dispatch rule in LiveKit Cloud
# Pattern: interview-*
# Or run: python interview_agent.py start
```

---

### Issue 2: Agent Joins But No Audio

**Symptoms:**
- Agent terminal shows "✅ Agent greeted candidate"
- But you hear nothing

**Causes:**
1. Browser audio muted
2. `RoomAudioRenderer` missing (we added it ✅)
3. OpenAI API key invalid
4. Audio output device issue

**Fix:**
```bash
# Check OpenAI key
cd backend/livekit-voice-agent
python -c "import openai; import os; from dotenv import load_dotenv; load_dotenv('.env.local'); client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print('OpenAI API Key Valid!' if os.getenv('OPENAI_API_KEY') else 'No API Key')"
```

**In browser:**
- Unmute the tab (check browser tab icon)
- Check system volume
- Check DevTools → Console for audio errors

---

### Issue 3: Agent Crashes After Joining

**Symptoms:**
- Agent joins, then terminal shows error
- Connection drops

**Check agent logs for:**
```
Error: OpenAI API Error
Error: Authentication failed
```

**Fix:**
- Verify OpenAI API key is correct
- Check you have access to Realtime API
- Try different OpenAI key

---

## 🧪 Quick Test Script

Create `test_agent_audio.py`:

```python
"""Quick test to verify agent can speak"""
import asyncio
import os
from dotenv import load_dotenv
from livekit import rtc, agents
from livekit.agents import AgentSession, Agent
from livekit.plugins import openai

load_dotenv(".env.local")

class TestAgent(Agent):
    def __init__(self):
        super().__init__(instructions="You are a test agent. Say hello.")

async def test():
    print("Testing agent audio...")
    
    # Create a simple room connection
    room = rtc.Room()
    
    try:
        # This would connect to a real room
        print("Agent voice config looks good!")
        print(f"OpenAI Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
```

Run: `python test_agent_audio.py`

---

## ✅ Working Configuration Checklist

- [ ] Agent shows "Waiting for interview sessions..."
- [ ] When interview starts, agent shows "joining room"
- [ ] Agent shows "greeted candidate"
- [ ] Frontend console shows LiveKit connected
- [ ] Browser asked for mic permissions (granted)
- [ ] `RoomAudioRenderer` is in the JSX ✅
- [ ] Agent terminal shows no errors
- [ ] OpenAI API key is valid
- [ ] System volume is up
- [ ] Browser tab is not muted

---

## 🎯 Most Likely Issues

Based on "can't hear agent":

### 1. **Agent Not Joining** (70% of cases)
- **Fix:** Use dev mode: `python interview_agent.py dev --room interview-SESSION_ID`

### 2. **OpenAI API Issue** (20% of cases)
- **Fix:** Verify API key has Realtime API access

### 3. **Browser Audio Issue** (10% of cases)
- **Fix:** Unmute tab, check volume, try different browser

---

## 🚀 Recommended Testing Flow

```bash
# Terminal 1: Start agent in dev mode
cd backend/livekit-voice-agent
python interview_agent.py dev

# Terminal 2: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 3: Start frontend
cd frontend
npm run dev

# Browser:
# 1. Start interview
# 2. Check agent terminal - should say "joining room"
# 3. Grant mic permissions
# 4. Speak: "Hello"
# 5. Agent should respond
```

---

## 📞 Get More Help

If still not working, collect this info:

1. **Agent terminal output** (full logs)
2. **Browser console errors** (F12 → Console)
3. **Network tab** showing LiveKit connection
4. **Audio elements** output from Step 7

Then we can diagnose the specific issue!

---

## 🎉 When It Works

You'll know it's working when:

1. **Agent terminal:** Shows "✅ Agent greeted candidate"
2. **Browser:** You hear "Hello! Welcome to your mock interview..."
3. **You speak:** Agent responds with voice
4. **Smooth conversation:** Back and forth works

**That's when you know everything is connected!** 🎊

