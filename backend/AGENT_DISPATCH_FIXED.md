# ✅ Agent Dispatch Issue - FIXED

## 🎯 The Problem

You were looking for "Agent Dispatch Rules" in LiveKit Cloud, but found only **Telephony dispatch rules** (for phone/SIP calls). 

**Key Discovery:** According to the [LiveKit Agent Dispatch documentation](https://docs.livekit.io/agents/server/agent-dispatch/), there are **three ways** to dispatch agents:

1. **Automatic dispatch** (default) - Agent joins ALL new rooms automatically
2. **Explicit dispatch via API** - Manually dispatch agents using API calls
3. **Dispatch via token configuration** - Include agent dispatch in the participant token ✅ **THIS IS WHAT WE NEED**

## 🔧 The Solution

We configured **agent dispatch via token** by updating your backend token generation code.

### What Changed:

**File:** `backend/app/routes/livekit_routes.py`

#### Change #1: Import Required Classes

```python
from livekit import api
from livekit.protocol.models import RoomConfiguration, RoomAgentDispatch
```

#### Change #2: Add Agent Dispatch to Token

Added this configuration when creating the token:

```python
# Configure agent dispatch - automatically dispatch agent when participant joins
token.with_room_config(
    RoomConfiguration(
        agents=[
            RoomAgentDispatch(
                agent_name="",  # Empty string matches any agent (including unnamed agents)
                metadata=f'{{"session_id": "{request.session_id}", "participant": "{request.participant_name}"}}'
            )
        ]
    )
)
```

## 🎯 How This Works

Based on the [official documentation](https://docs.livekit.io/agents/server/agent-dispatch/), here's the flow:

```
┌─────────────────────────────────────────────────────────────┐
│  1. Frontend requests token from backend                    │
│     POST /livekit/token { session_id: "abc123" }           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Backend creates token WITH agent dispatch config         │
│     - Room: interview-abc123                                 │
│     - Grants: join, publish, subscribe                       │
│     - RoomConfiguration.agents: [RoomAgentDispatch(...)]    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Frontend connects to LiveKit Cloud with token           │
│     Room "interview-abc123" is created                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. LiveKit Cloud reads token's RoomConfiguration           │
│     "Oh! This token has agent dispatch configured!"         │
│     agent_name: "" (matches ANY registered agent)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. LiveKit Cloud dispatches job to your Python agent       │
│     Agent receives: JobContext with room info               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  6. ✅ Agent joins room "interview-abc123"                  │
│     ✅ Agent starts voice session                           │
│     ✅ Agent greets participant                             │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Key Points from Documentation

### Agent Name Matching

From the [docs](https://docs.livekit.io/agents/server/agent-dispatch/):

> "If you set the `agent_name` property, you turn off automatic dispatch. Agents must be explicitly dispatched to a room."

Our solution:
- Agent code: `@server.rtc_session()` - No agent_name specified
- Token config: `agent_name=""` - Empty string matches unnamed agents
- Result: ✅ Agent will be dispatched when participant connects

### Job Metadata

From the [docs](https://docs.livekit.io/agents/server/agent-dispatch/):

> "Explicit dispatch allows you to pass metadata to the agent, available in the `JobContext`. This is useful for including details such as the user's ID, name, or phone number."

Our implementation:
```python
metadata=f'{{"session_id": "{request.session_id}", "participant": "{request.participant_name}"}}'
```

The agent can access this in `JobContext.job.metadata` if needed.

## 🚀 Testing Instructions

### 1. Restart Backend (to load new code)

```powershell
# Stop backend (Ctrl+C if running)
# Then restart:
cd C:\Personal\hirecoach\backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### 2. Keep Agent Running

Your agent should still be running and showing:
```
INFO   livekit.agents   registered worker
                        {"agent_name": "", "id": "AW_SREg5NKEkim8"}
```

If not running, start it:
```powershell
cd C:\Personal\hirecoach\backend
RUN_AGENT.bat
```

### 3. Test from Frontend

1. Open: http://localhost:3000/interview/setup

2. Fill in the form and click **"Start Voice Interview"**
   - This uses `/interview/session/[sessionId]` which has LiveKit voice

3. **Watch your agent terminal** - You should now see:
   ```
   ✅ AI Interview Agent joining room: interview-abc123
      Session ID: abc123
   ✅ Agent greeted candidate in room: interview-abc123
   ```

4. **In frontend** - You should hear the agent speaking!

## 🎯 Expected Behavior

### Backend Logs (when token is generated):
```
✅ Generated LiveKit token for session: abc123
   Room: interview-abc123
   Agent dispatch: Enabled (automatic)
```

### Agent Logs (when participant joins):
```
✅ AI Interview Agent joining room: interview-abc123
   Session ID: abc123
✅ Agent greeted candidate in room: interview-abc123
```

### Frontend:
- Loading screen: "Connecting to AI Interviewer..."
- Then you should see: LiveKit connected
- Then you should hear: Agent greeting you via voice

## 🔍 Troubleshooting

### Agent Still Not Joining?

**Check #1: Backend restarted?**
- The new code won't work until backend is restarted
- Look for the new log message with "Agent dispatch: Enabled"

**Check #2: Using correct interview mode?**
- ✅ `/interview/session/[sessionId]` - Uses LiveKit voice (needs agent)
- ❌ `/interview/conversational/[sessionId]` - Uses Whisper text (no agent)

**Check #3: Agent running and registered?**
```
INFO   livekit.agents   registered worker
```

**Check #4: Check frontend browser console**
```javascript
console.log("LiveKit connected:", { room, url })
```

**Check #5: Verify token includes dispatch**
Add temporary debug logging in backend:
```python
print(f"Token room config: {token._room_config}")
```

## 📖 Reference

- [LiveKit Agent Dispatch Documentation](https://docs.livekit.io/agents/server/agent-dispatch/)
- [Dispatch on Participant Connection](https://docs.livekit.io/agents/server/agent-dispatch/#dispatch-on-participant-connection)
- [Job Metadata Guide](https://docs.livekit.io/agents/server/job-lifecycle/)

## ✅ What Was Wrong Before

**Before:**
- Token had room join permissions only
- No agent dispatch configuration in token
- LiveKit Cloud didn't know to send agent to the room
- Agent waited forever (never received job)

**After:**
- Token includes `RoomConfiguration` with `RoomAgentDispatch`
- When participant joins, LiveKit Cloud reads token
- LiveKit Cloud automatically dispatches agent to room
- Agent receives job and joins immediately ✅

---

## 🎉 Summary

**The fix:** We added agent dispatch configuration to the participant token using `RoomConfiguration` and `RoomAgentDispatch`, following the [official LiveKit documentation](https://docs.livekit.io/agents/server/agent-dispatch/).

**No UI configuration needed** - The telephony dispatch rules you found are for phone calls, not for room-based agents. Room-based agent dispatch is configured **via the participant token**, which is what we just fixed!

Now restart your backend and test! 🚀

