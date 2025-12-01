# 🚨 LiveKit Cloud Dispatch Rule Configuration

## Problem
Your agent is registered and waiting, but it doesn't join rooms because **LiveKit Cloud doesn't have a dispatch rule** configured.

## What's a Dispatch Rule?
A dispatch rule tells LiveKit Cloud: "When a room matching pattern X is created, send a job to agent worker Y."

Without it:
- ✅ Frontend creates room: `interview-abc123`
- ✅ Agent worker is registered and waiting
- ❌ **LiveKit Cloud doesn't connect them**

## Solution: Configure Dispatch Rule in LiveKit Cloud

### Step 1: Log into LiveKit Cloud
1. Go to https://cloud.livekit.io
2. Sign in to your account
3. Select your project: **interviewsaas-m7lvjg0t**

### Step 2: Navigate to Dispatch Rules
1. Click **"Telephony"** in the left sidebar
2. Look for **"Agent Dispatch"** or **"Dispatch Rules"** section
3. Click **"Create Dispatch Rule"** or **"Add Rule"**

### Step 3: Create Dispatch Rule
You should see a form. Fill it in **exactly** like this:

```
┌─────────────────────────────────────────────────────────┐
│ Create Agent Dispatch Rule                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Rule Name:           Interview Agent Dispatch          │
│                                                         │
│ Room Name Pattern:   interview-*                       │
│                      ↑ IMPORTANT: Must match exactly!  │
│                                                         │
│ Agent Name:          [leave blank or enter: *]         │
│                      ↑ Empty = any agent               │
│                                                         │
│ Priority:            [leave default or enter: 1]       │
│                                                         │
│ Metadata:            [leave empty]                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Key points:**
- **Room Name Pattern:** Must be `interview-*` (with asterisk)
  - This matches: `interview-abc123`, `interview-xyz789`, etc.
  - The `*` is a wildcard matching anything after "interview-"
  
- **Agent Name:** Leave blank or use `*`
  - Your agent registers with `agent_name=""` (empty)
  - Blank/empty means "dispatch to any available agent"
  
- **Everything else:** Use defaults or leave empty

### Step 4: Save and Test
1. **Double-check your configuration:**
   ```
   Rule Name: Interview Agent Dispatch
   Room Name Pattern: interview-*
   Agent Name: (leave blank or enter *)
   ```

2. Click **"Save"** or **"Create Rule"** or **"Add Dispatch Rule"**

3. You should see the rule listed in your dashboard with:
   - Pattern: `interview-*`
   - Status: Active/Enabled

4. **Keep your agent running** (it should already be running in terminal)

5. Try starting an interview from frontend: http://localhost:3000/interview/setup

### Expected Behavior After Configuration

#### Before (what you see now):
```
Frontend: Creates room "interview-abc123"
Agent: Registered and waiting... [no job received]
```

#### After (what should happen):
```
Frontend: Creates room "interview-abc123"
LiveKit Cloud: "Found room matching 'interview-*', dispatching to agent..."
Agent: ✅ Received job request {"room": "interview-abc123"}
Agent: ✅ Joining room...
Agent: ✅ Starting voice session...
Agent: 👋 "Hello! Welcome to your mock interview..."
```

## Alternative: Use Agent Name
If you want more control, you can:

1. **Update agent to use a specific name:**
   ```python
   # In interview_agent.py, line ~114
   agents.cli.run_app(server, agent_name="interview-agent")
   ```

2. **Configure dispatch rule with that name:**
   - Room Pattern: `interview-*`
   - Agent Name: `interview-agent`

## Troubleshooting

### Can't find Dispatch Rules?
- Look under **"Telephony"** → **"Agent Dispatch"** (most common location)
- Or look under **"Agents"** → **"Dispatch Rules"** (some UIs)
- Make sure you're on a plan that supports agents (not Free tier)
- Check if your project has agents enabled

### Dispatch rule created but agent still doesn't join?
1. Check agent logs for errors
2. Verify agent is still running and registered
3. Check room name matches pattern (must start with `interview-`)
4. Restart the agent after creating the rule

### Still not working?
Try a **local LiveKit server** instead:
1. Run: `docker run --rm -p 7880:7880 -p 7881:7881 livekit/livekit-server --dev`
2. Update `.env` to use `ws://localhost:7880`
3. Local server auto-dispatches to any registered agent

## Current Status
- ✅ Agent code is correct
- ✅ Frontend code is correct
- ✅ Backend code is correct
- ✅ Agent is registered with LiveKit Cloud
- ❌ **Missing: Dispatch rule in LiveKit Cloud**

Once you add the dispatch rule, everything should work! 🎉

