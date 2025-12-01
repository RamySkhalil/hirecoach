# 🎯 LiveKit Agent Dispatch Setup - CRITICAL STEP

## ✅ Current Status
Your agent is successfully registered and waiting for jobs:
```
✅ Worker registered: AW_SREg5NKEkim8
✅ URL: wss://interviewsaas-m7lvjg0t.livekit.cloud
✅ Region: Israel
✅ Listening for: interview-* rooms
```

## ❌ Problem
The agent never joins rooms because **LiveKit Cloud doesn't know to send jobs to it**.

## 🔧 Solution: Configure Agent Dispatch Rule

### Step 1: Open LiveKit Cloud Dashboard

1. Go to: **https://cloud.livekit.io/projects/p_1hl6dsarlbc/agents**
   - Or navigate: Dashboard → Your Project → **Agents** (left sidebar)

2. Look for **"Agent Dispatch"** or **"Dispatch Rules"** section

### Step 2: Create New Dispatch Rule

Click **"Create Dispatch Rule"** or **"Add Rule"** button.

Fill in the form with these **EXACT VALUES**:

```
┌────────────────────────────────────────────────────────┐
│  Create Agent Dispatch Rule                           │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Rule Name:                                           │
│  ┌──────────────────────────────────────────────┐    │
│  │ Interview Agent Dispatch                     │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Room Name Pattern: ⚠️ CRITICAL - Must match exactly  │
│  ┌──────────────────────────────────────────────┐    │
│  │ interview-*                                   │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Agent Name: (leave empty or use *)                   │
│  ┌──────────────────────────────────────────────┐    │
│  │ *                                             │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Priority: (optional, use default)                    │
│  ┌──────────────────────────────────────────────┐    │
│  │ 1                                             │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Metadata: (leave empty)                              │
│  ┌──────────────────────────────────────────────┐    │
│  │                                               │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  [Cancel]                    [Create Dispatch Rule]   │
└────────────────────────────────────────────────────────┘
```

### Key Configuration Points:

**Room Name Pattern:** `interview-*`
- ⚠️ **MUST** match exactly (with asterisk)
- This matches rooms: `interview-abc123`, `interview-xyz789`, etc.
- The `*` is a wildcard for anything after "interview-"

**Agent Name:** `*` or leave empty
- Your agent registers without a specific name
- Using `*` or blank means "dispatch to any available agent"

### Step 3: Save and Verify

1. Click **"Create Dispatch Rule"** or **"Save"**

2. You should see the rule in your dashboard:
   ```
   ┌────────────────────────────────────────────────────┐
   │ Interview Agent Dispatch        [Active] [Edit]    │
   │ Pattern: interview-*                               │
   │ Agent: * (any)                                     │
   └────────────────────────────────────────────────────┘
   ```

3. Make sure the status shows **"Active"** or **"Enabled"**

### Step 4: Test the Connection

Keep your agent running (you should see in terminal):
```
INFO   livekit.agents   registered worker
                        {"agent_name": "", "id": "AW_SREg5NKEkim8"}
```

Now test from frontend:

1. **Start your backend** (if not running):
   ```powershell
   cd C:\Personal\hirecoach\backend
   .venv\Scripts\Activate.ps1
   uvicorn app.main:app --reload
   ```

2. **Start your frontend** (if not running):
   ```powershell
   cd C:\Personal\hirecoach\frontend
   npm run dev
   ```

3. **Open browser** to: http://localhost:3000/interview/setup

4. **Choose "Voice Interview"** (not Conversational)
   - This will navigate to `/interview/session/[sessionId]`
   - This is the one that uses LiveKit voice with the agent

5. **Watch your agent terminal** - You should see:
   ```
   ✅ AI Interview Agent joining room: interview-abc123
      Session ID: abc123
   ✅ Agent greeted candidate in room: interview-abc123
   ```

---

## 🔍 Troubleshooting

### Can't Find "Agents" or "Dispatch Rules"?

**Option A: Try these locations:**
1. Dashboard → **Agents** (left sidebar)
2. Dashboard → **Telephony** → **Agent Dispatch**
3. Dashboard → **Settings** → **Agent Dispatch**

**Option B: Check your plan:**
- Agent dispatch is available on paid plans
- Free/starter plans may not support agents
- Upgrade if needed: https://cloud.livekit.io/settings/plans

### Dispatch Rule Created But Agent Still Doesn't Join?

**Check #1: Verify Room Name**
- Frontend creates room: `interview-{sessionId}` ✅
- Dispatch pattern: `interview-*` ✅
- These MUST match!

**Check #2: Agent Still Running?**
```powershell
# In agent terminal, you should see:
INFO   livekit.agents   registered worker
```

If you don't see this, restart the agent:
```powershell
cd C:\Personal\hirecoach\backend
RUN_AGENT.bat
```

**Check #3: Using Correct Interview Mode?**
- ✅ `/interview/session/[sessionId]` - Uses LiveKit voice (needs agent)
- ❌ `/interview/conversational/[sessionId]` - Uses Whisper text (no agent needed)

Make sure you're testing with the **Voice Interview** mode!

**Check #4: Check LiveKit Cloud Logs**
1. Go to: https://cloud.livekit.io/projects/p_1hl6dsarlbc/monitor
2. Look for room creation events
3. Check if dispatch rule is being triggered

### Agent Joins But Doesn't Speak?

**Check #1: OpenAI API Key**
```powershell
# In backend\livekit-voice-agent\.env.local
OPENAI_API_KEY=sk-proj-your-key-here
```

**Check #2: OpenAI Credits**
- Go to: https://platform.openai.com/account/billing
- Make sure you have credits available
- Realtime API uses credits faster than regular API

---

## 📊 How This Works (Architecture)

```
┌─────────────┐                    ┌──────────────┐
│  Frontend   │                    │   Backend    │
│             │                    │              │
│ User joins  │ ───(1) Request──► │ Generate     │
│ interview   │    LiveKit token   │ token for    │
│             │                    │ room name:   │
│             │ ◄──(2) Token+URL─  │ interview-X  │
└─────────────┘                    └──────────────┘
       │
       │ (3) Connect to room
       ▼
┌─────────────────────────────────────────────────┐
│          LiveKit Cloud                          │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ Room Created: interview-X                │  │
│  └──────────────────────────────────────────┘  │
│                 │                               │
│                 │ (4) Match dispatch rule:      │
│                 │     "interview-*"             │
│                 ▼                               │
│  ┌──────────────────────────────────────────┐  │
│  │ Send job to registered agent             │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                  │
                  │ (5) Job dispatched
                  ▼
        ┌──────────────────┐
        │  Python Agent    │
        │  (Your Machine)  │
        │                  │
        │  ✅ Receives job │
        │  ✅ Joins room   │
        │  ✅ Starts voice │
        │  ✅ Greets user  │
        └──────────────────┘
```

**Without Dispatch Rule:**
- Step 4 fails ❌
- Agent never receives jobs
- User waits forever

**With Dispatch Rule:**
- All steps succeed ✅
- Agent joins automatically
- Interview starts!

---

## ✅ Next Steps

1. **Configure dispatch rule** (steps above)
2. **Keep agent running** in terminal
3. **Test from frontend** using Voice Interview mode
4. **Watch agent logs** for connection messages

Once the dispatch rule is configured, your agent will automatically join rooms matching `interview-*` pattern! 🎉

---

## 🆘 Still Not Working?

If you've followed all steps and it's still not working:

1. **Share agent logs** - Copy the terminal output
2. **Share LiveKit Cloud logs** - From monitor/logs section
3. **Verify dispatch rule** - Screenshot the rule configuration

Or consider using a **local LiveKit server** for development:
```powershell
# Much simpler - auto-dispatches to all agents
docker run --rm -p 7880:7880 -p 7881:7881 -e LIVEKIT_DEV_MODE=1 livekit/livekit-server --dev
```

Local server doesn't require dispatch rules - agents auto-join! Perfect for development.

