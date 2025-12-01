# ⚡ Quick Dispatch Rule Setup

You found the right place! Now here's **exactly** what to enter:

## Location
✅ **Telephony** → **Agent Dispatch** (you found it!)

## Click "Create Dispatch Rule" or "Add Rule"

## Fill in the Form

### Required Fields:

**1. Rule Name:**
```
Interview Agent Dispatch
```

**2. Room Name Pattern:**
```
interview-*
```
⚠️ **CRITICAL:** Must include the asterisk `*` at the end!

**3. Agent Name:**
```
[Leave this field BLANK/EMPTY]
```
Or if it requires something, enter:
```
*
```

**4. Priority:**
```
1
```
(or leave default)

**5. Metadata:**
```
[Leave empty]
```

## After You Save

You should see your new rule listed like:
```
Interview Agent Dispatch
  Pattern: interview-*
  Agent: (any)
  Status: ✅ Active
```

## Test It!

1. **Make sure your agent is still running** in the terminal
   - If not, run: `cd backend && RUN_AGENT.bat`
   - You should see: `registered worker`

2. **Start an interview from frontend:**
   - Open: http://localhost:3000/interview/setup
   - Create a new interview
   - Go to the interview session page

3. **Watch your agent terminal:**
   - You should see: `received job request {"room": "interview-..."}`
   - Then: `✅ AI Interview Agent joining room: interview-...`

4. **In your browser:**
   - You should hear the agent say: "Hello! Welcome to your mock interview session..."

## If It Still Doesn't Work

Try restarting the agent after creating the rule:
```bash
# Press Ctrl+C in the agent terminal to stop it
# Then run again:
cd backend
RUN_AGENT.bat
```

## Alternative: Local Server (No Dispatch Rule Needed!)

If you're having issues with cloud config, you can skip all of this by running a local LiveKit server:

```bash
docker run --rm -p 7880:7880 -p 7881:7881 livekit/livekit-server --dev
```

Then update your `.env` files to `ws://localhost:7880` - it auto-dispatches! ✨

See: `SWITCH_TO_LOCAL_LIVEKIT.md`

