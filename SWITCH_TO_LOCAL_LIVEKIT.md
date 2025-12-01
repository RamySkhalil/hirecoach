# 🔧 Switch to Local LiveKit Server - Step by Step

Your agent cannot connect to LiveKit Cloud. Let's use a **local server** instead - it's faster and eliminates all network issues.

---

## 📦 Step 1: Install Docker Desktop (Easiest Method)

**Download and Install:**
```
https://www.docker.com/products/docker-desktop
```

**After installation:**
- Restart your computer
- Open Docker Desktop and let it start

---

## 🚀 Step 2: Run Local LiveKit Server

**Open PowerShell and run:**
```powershell
docker run --rm -p 7880:7880 -p 7881:7881 -e LIVEKIT_DEV_MODE=1 livekit/livekit-server --dev
```

**Expected Output:**
```
INFO starting LiveKit server... {"version": "..."}
INFO using generated API Key/secret  
INFO API Key: devkey, Secret Key: secret
INFO HTTP server listening {"addr": ":7880"}
INFO WebRTC server listening {"addr": ":7881"}
```

**Keep this terminal running!**

---

## 📝 Step 3: Update Backend .env

**Edit `C:\Personal\hirecoach\backend\.env`**

Find these lines and **change** them:

```bash
# OLD (Cloud - not working):
# LIVEKIT_URL=wss://interviewsaas-m7lvjg0t.livekit.cloud
# LIVEKIT_API_KEY=...
# LIVEKIT_API_SECRET=...

# NEW (Local - will work):
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

**Save the file!**

---

## 📝 Step 4: Update Agent .env.local

**Edit `C:\Personal\hirecoach\backend\livekit-voice-agent\.env.local`**

```bash
# OpenAI (keep your existing key)
OPENAI_API_KEY=sk-proj-your-key-here

# LiveKit (change to local)
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

**Save the file!**

---

## 🔄 Step 5: Restart Everything

**Terminal 1: Local LiveKit Server (Already running from Step 2)**
```powershell
docker run --rm -p 7880:7880 -p 7881:7881 -e LIVEKIT_DEV_MODE=1 livekit/livekit-server --dev
```

**Terminal 2: Agent (NEW TERMINAL)**
```powershell
cd C:\Personal\hirecoach\backend\livekit-voice-agent
python interview_agent.py dev
```

**Expected Output (NO ERRORS!):**
```
============================================================
🎤 LiveKit AI Interview Agent
============================================================
LIVEKIT_URL: ws://localhost:7880
LIVEKIT_API_KEY: Set
OPENAI_API_KEY: Set
============================================================

Waiting for interview sessions...
```

**Terminal 3: Backend (NEW TERMINAL)**
```powershell
cd C:\Personal\hirecoach\backend
uvicorn app.main:app --reload
```

**Terminal 4: Frontend (NEW TERMINAL)**
```powershell
cd C:\Personal\hirecoach\frontend
npm run dev
```

---

## 🧪 Step 6: Test Interview

1. **Open browser:** http://localhost:3000/interview/setup
2. **Start interview**
3. **Agent Terminal should show:**
   ```
   ✅ AI Interview Agent joining room: interview-abc123
   ✅ Agent greeted candidate in room: interview-abc123
   ```
4. **You should HEAR:** "Hello! Welcome to your mock interview..."

---

## ✅ Success Checklist

After these changes, you should have:

- [ ] Docker Desktop installed and running
- [ ] Local LiveKit server running (Terminal 1)
- [ ] Backend `.env` using `ws://localhost:7880`
- [ ] Agent `.env.local` using `ws://localhost:7880`
- [ ] Agent connects WITHOUT errors
- [ ] Frontend loads interview session
- [ ] You HEAR agent voice! 🎤

---

## 🔍 Troubleshooting

### Issue: Docker command fails

**Solution 1: Install Docker Desktop**
- Download from https://www.docker.com/products/docker-desktop
- Install and restart computer
- Try again

**Solution 2: Download LiveKit Binary**
- Go to https://github.com/livekit/livekit/releases
- Download `livekit-server-*.zip` for Windows
- Extract and run: `livekit-server.exe --dev`

---

### Issue: Agent still shows cloud URL

**Check your .env files:**
```powershell
# Check backend .env
cd C:\Personal\hirecoach\backend
type .env | findstr LIVEKIT_URL

# Check agent .env.local
cd livekit-voice-agent
type .env.local | findstr LIVEKIT_URL
```

**Both should show:** `ws://localhost:7880`

If not, edit the files and save again!

---

### Issue: Port 7880 already in use

**Find and kill the process:**
```powershell
netstat -ano | findstr :7880
# Note the PID number
taskkill /F /PID <PID>
```

Then restart LiveKit server.

---

## 📊 Before vs After

### Before (Cloud - Not Working):
```
LIVEKIT_URL=wss://interviewsaas-m7lvjg0t.livekit.cloud
↓
❌ Network Error
❌ Connection Failed
❌ No Audio
```

### After (Local - Working):
```
LIVEKIT_URL=ws://localhost:7880
↓
✅ Instant Connection
✅ No Network Issues
✅ Agent Speaks! 🎤
```

---

## 🎉 Why Local is Better

**Benefits:**
- ✅ No network/firewall issues
- ✅ Faster connection
- ✅ Free (no cloud costs)
- ✅ Works offline
- ✅ Easier debugging
- ✅ No region problems

**When to use Cloud:**
- Production deployment
- Need global access
- Multiple developers
- After local testing works

---

## 🚀 Quick Commands Reference

```powershell
# Terminal 1: Start local LiveKit
docker run --rm -p 7880:7880 -p 7881:7881 livekit/livekit-server --dev

# Terminal 2: Start agent
cd C:\Personal\hirecoach\backend\livekit-voice-agent
python interview_agent.py dev

# Terminal 3: Start backend
cd C:\Personal\hirecoach\backend
uvicorn app.main:app --reload

# Terminal 4: Start frontend
cd C:\Personal\hirecoach\frontend
npm run dev
```

**Then test:** http://localhost:3000/interview/setup

---

## 📞 Need Help?

If still having issues after switching to local:

1. **Check Docker is running:** Open Docker Desktop
2. **Check port 7880 is free:** `netstat -ano | findstr :7880`
3. **Check .env files:** Both should have `ws://localhost:7880`
4. **Check agent connects:** Should show NO connection errors

**The local server approach will fix your connection issues!** 🎊

