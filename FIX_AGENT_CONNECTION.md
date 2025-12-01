# 🔴 CRITICAL: Agent Connection Error - FIXES

## ❌ The Error

```
livekit.rtc.room.ConnectError: engine: signal failure: failed to retrieve region info: 
error sending request for url (https://interviewsaas-m7lvjg0t.livekit.cloud/settings/regions)
```

**What This Means:**
The agent is trying to connect to LiveKit Cloud but **cannot reach the server**. This is NOT a code issue - it's a network/configuration issue.

---

## ✅ SOLUTION 1: Use Local LiveKit Server (Recommended for Testing)

Instead of LiveKit Cloud, run LiveKit locally. This bypasses all network issues.

### Install LiveKit Server Locally

**Windows (via Scoop):**
```powershell
# Install Scoop if you don't have it
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Install LiveKit server
scoop bucket add livekit https://github.com/livekit/scoop-bucket.git
scoop install livekit-server
```

**Or download directly:**
https://github.com/livekit/livekit/releases

### Run Local Server

```powershell
# Create a simple config file: livekit.yaml
# (or use default config)
livekit-server --dev
```

**Expected Output:**
```
INFO starting LiveKit server... {"version": "..."}
INFO using generated API Key/secret
INFO HTTP server listening {"addr": ":7880"}
INFO WebRTC server listening {"addr": ":7881"}
```

### Update Your .env Files

**backend/.env:**
```bash
# Change from Cloud to Local
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

**backend/livekit-voice-agent/.env.local:**
```bash
OPENAI_API_KEY=sk-your-key
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

**Restart everything and test!**

---

## ✅ SOLUTION 2: Fix LiveKit Cloud Connection

If you want to use LiveKit Cloud, the issue is network connectivity.

### Check #1: Verify LiveKit Cloud Credentials

Go to https://cloud.livekit.io → Your Project → Settings

**Verify these match your .env:**
- API Key
- API Secret  
- WebSocket URL (should be `wss://...livekit.cloud` not `https://`)

### Check #2: Update LiveKit URL Format

**In `backend/.env` and `backend/livekit-voice-agent/.env.local`:**

```bash
# Make sure it's wss:// (WebSocket Secure) NOT https://
LIVEKIT_URL=wss://interviewsaas-m7lvjg0t.livekit.cloud

# NOT: https://interviewsaas-m7lvjg0t.livekit.cloud ❌
```

### Check #3: Network/Firewall Issues

**Test connectivity:**
```powershell
# Test if you can reach LiveKit Cloud
curl https://interviewsaas-m7lvjg0t.livekit.cloud/settings/regions
```

**If this fails:**
- Check firewall settings
- Check proxy settings
- Try different network (mobile hotspot?)
- LiveKit Cloud might be down (check status page)

### Check #4: Try Different Region

In LiveKit Cloud dashboard:
- Check if your region is Israel
- Try creating a project in a different region (US, EU)
- Update the URL in your .env files

---

## ✅ SOLUTION 3: Use LiveKit Cloud with Dispatch (No Local Agent)

If local agent keeps failing, use LiveKit Cloud's built-in agent hosting:

### Steps:

1. **Go to LiveKit Cloud Dashboard**
2. **Navigate to "Agents" tab**
3. **Create a new Agent:**
   - Upload your `interview_agent.py`
   - Set environment variables (OPENAI_API_KEY)
   - Deploy

4. **Create Dispatch Rule:**
   - Room Pattern: `interview-*`
   - Agent: Your deployed agent

5. **Update your .env to remove local agent:**
   - Keep frontend/backend running
   - LiveKit Cloud will run the agent automatically

---

## 🚀 RECOMMENDED: Quick Test with Local Server

**This is the FASTEST way to get it working:**

```powershell
# Terminal 1: Local LiveKit Server
livekit-server --dev

# Terminal 2: Agent (with local server)
cd backend/livekit-voice-agent
# Edit .env.local to use ws://localhost:7880
python interview_agent.py dev

# Terminal 3: Backend
cd backend
# Edit .env to use ws://localhost:7880
uvicorn app.main:app --reload

# Terminal 4: Frontend  
cd frontend
npm run dev
```

**Test:** Start interview and you should hear the agent!

---

## 🔍 Detailed Diagnosis

### The Error Breakdown

```
WARNI… livekit - failed to connect: Signal(RegionError("error sending request for url 
(https://interviewsaas-m7lvjg0t.livekit.cloud/settings/regions)")), retrying... (1/3)
```

**What's happening:**
1. Agent receives job request ✅
2. Agent tries to join the LiveKit room
3. Agent queries LiveKit Cloud for region info
4. **Network request fails** ❌
5. Agent retries 3 times
6. Agent gives up and crashes

**Possible Causes:**
- Network firewall blocking LiveKit Cloud
- Incorrect URL format (https vs wss)
- LiveKit Cloud regional issue
- Proxy intercepting requests
- Internet connectivity problem

---

## ✅ Immediate Fix: Edit .env Files

### File: `backend/.env`

```bash
# === DATABASE ===
DATABASE_URL=postgresql://...

# === AI SERVICES ===
OPENAI_API_KEY=sk-proj-...

# === LIVEKIT (USE LOCAL FOR NOW) ===
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

### File: `backend/livekit-voice-agent/.env.local`

```bash
# === AI ===
OPENAI_API_KEY=sk-proj-...

# === LIVEKIT (MUST MATCH BACKEND) ===
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

### Install and Run Local LiveKit Server

```powershell
# Download from https://github.com/livekit/livekit/releases
# Or use Docker:
docker run --rm -p 7880:7880 -p 7881:7881 livekit/livekit-server --dev
```

---

## 📋 Checklist

After making changes:

- [ ] Local LiveKit server running (`livekit-server --dev`)
- [ ] Backend .env has `ws://localhost:7880`
- [ ] Agent .env.local has `ws://localhost:7880`
- [ ] API keys match in both files
- [ ] Restart agent with updated .env
- [ ] Restart backend
- [ ] Test interview

---

## 🎯 Why Local Server is Better for Dev

**LiveKit Cloud Issues:**
- ❌ Network/firewall problems
- ❌ Region latency
- ❌ Connection errors
- ❌ Harder to debug

**Local Server Benefits:**
- ✅ No network issues
- ✅ Instant connection
- ✅ Easier debugging
- ✅ No cost
- ✅ Works offline

---

## 🆘 Quick Test

Run this to verify connectivity:

```powershell
# Test if you can reach your LiveKit Cloud
curl https://interviewsaas-m7lvjg0t.livekit.cloud

# Test if local server is running
curl http://localhost:7880
```

**If Cloud curl fails:** Use local server  
**If local curl works:** You're good to go!

---

## 🎉 After Fix

Once using local server, you should see:

**Agent Terminal:**
```
✅ AI Interview Agent joining room: interview-abc123
   Session ID: abc123
✅ Agent greeted candidate in room: interview-abc123
```

**No errors!** And you'll hear the agent speak!

---

## 📞 Still Issues?

If local server STILL doesn't work:

1. **Check ports:** Make sure 7880 and 7881 are not blocked
2. **Check logs:** Look for errors in livekit-server output
3. **Try Docker:** `docker run -p 7880:7880 -p 7881:7881 livekit/livekit-server --dev`

The local server approach should eliminate all network issues!

