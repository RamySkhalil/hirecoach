# 🔧 LiveKit Environment Setup - Quick Guide

## 📋 Required Environment Variables

### 1. Backend `.env` (in `C:\Personal\hirecoach\backend\.env`)

```bash
# Database (Neon Postgres)
DATABASE_URL=postgresql://neondb_owner:your_password@your-host.neon.tech/interviewly?sslmode=require

# OpenAI API
OPENAI_API_KEY=sk-proj-...

# LiveKit Credentials
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Other AI services
ANTHROPIC_API_KEY=sk-ant-...
DEEPGRAM_API_KEY=...
ELEVENLABS_API_KEY=...
```

### 2. Frontend `.env.local` (in `C:\Personal\hirecoach\frontend\.env.local`)

```bash
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Clerk webhook secret (for production)
CLERK_WEBHOOK_SECRET=whsec_...
```

### 3. Agent `.env.local` (in `C:\Personal\hirecoach\backend\livekit-voice-agent\.env.local`)

```bash
# OpenAI API (for Realtime voice)
OPENAI_API_KEY=sk-proj-...

# LiveKit Credentials (same as backend)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🔑 How to Get LiveKit Credentials

### Step 1: Create LiveKit Account
1. Go to https://cloud.livekit.io
2. Sign up or log in
3. Create a new project

### Step 2: Get Credentials
1. In your project dashboard, click "Settings"
2. Copy the following:
   - **LIVEKIT_URL** (e.g., `wss://your-project.livekit.cloud`)
   - **API Key** (starts with `API`)
   - **API Secret** (long alphanumeric string)

### Step 3: Set Up Dispatch Rule
1. In LiveKit dashboard, go to "Dispatch"
2. Click "Add Rule"
3. Configure:
   - **Rule Name:** Interview Rooms
   - **Room Pattern:** `interview-*`
   - **Agent URL:** (Your agent endpoint - for local dev, use ngrok/localtunnel)

---

## 🚀 Quick Start Commands

### Terminal 1: Backend
```bash
cd C:\Personal\hirecoach\backend
uvicorn app.main:app --reload
```

### Terminal 2: Agent (Optional for full video AI)
```bash
cd C:\Personal\hirecoach\backend\livekit-voice-agent
python interview_agent.py start
```

### Terminal 3: Frontend
```bash
cd C:\Personal\hirecoach\frontend
npm run dev
```

---

## ✅ Verification

### 1. Check Backend Health
```bash
curl http://localhost:8000/livekit/health
```

**Expected Response:**
```json
{
  "livekit_installed": true,
  "livekit_configured": true,
  "url": "wss://your-project.livekit.cloud"
}
```

### 2. Test Token Generation
```bash
curl -X POST http://localhost:8000/livekit/token \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"test123\",\"participant_name\":\"Test User\"}"
```

**Expected Response:**
```json
{
  "token": "eyJhbGc...",
  "url": "wss://your-project.livekit.cloud",
  "room_name": "interview-test123"
}
```

### 3. Check Agent Status
Agent terminal should show:
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
```

---

## 🐛 Common Issues

### Issue: "LiveKit not configured"

**Symptom:** Backend returns 500 error

**Fix:**
1. Check `.env` file exists in `backend/` directory
2. Verify all three LiveKit variables are set
3. Restart backend server

### Issue: "Failed to fetch token"

**Symptom:** Frontend shows "Video Unavailable"

**Fix:**
1. Ensure backend is running on port 8000
2. Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
3. Check browser console for CORS errors

### Issue: Agent not connecting

**Symptom:** Agent terminal shows no activity

**Fix:**
1. Verify `.env.local` exists in `livekit-voice-agent/` directory
2. Check all credentials match backend
3. Ensure dispatch rule is configured in LiveKit Cloud

---

## 📦 Dependencies Already Installed

### Backend Python Packages:
```txt
livekit==0.11.0
fastapi
uvicorn
sqlalchemy
pydantic
openai
```

### Frontend NPM Packages:
```json
{
  "@livekit/components-react": "^2.9.16",
  "@livekit/components-styles": "^1.2.0",
  "livekit-client": "^2.16.0"
}
```

### Agent Python Packages:
```txt
livekit-agents
livekit-plugins-openai
livekit-plugins-noise-cancellation
```

---

## 🔐 Security Notes

### Development:
- ✅ `.env` files are gitignored
- ✅ Tokens expire after 2 hours
- ✅ Room names are unique per session

### Production:
- 🔒 Use environment variables, not `.env` files
- 🔒 Restrict CORS to your domain
- 🔒 Enable rate limiting
- 🔒 Use HTTPS/WSS only
- 🔒 Rotate API keys regularly

---

## 📝 File Checklist

Before starting, ensure these files exist:

```
hirecoach/
├── backend/
│   ├── .env                          ← CREATE THIS
│   └── livekit-voice-agent/
│       └── .env.local                ← CREATE THIS
└── frontend/
    └── .env.local                    ← CREATE THIS
```

---

## ✨ What Works Without Agent

Even if you don't run the agent, interviews still work!

**With Agent:**
- ✅ Video chat with AI interviewer
- ✅ Voice conversation
- ✅ Real-time feedback
- ✅ Text Q&A

**Without Agent:**
- ✅ Candidate video only
- ✅ Text Q&A works normally
- ✅ Scores and feedback work
- ✅ Full interview flow

The agent is **optional** for the complete AI voice experience, but **not required** for core functionality.

---

## 🎯 Ready to Go!

Once your `.env` files are configured:

1. ✅ Start backend
2. ✅ Start frontend
3. ✅ (Optional) Start agent
4. ✅ Navigate to http://localhost:3000/interview/setup
5. ✅ Start your first visual AI interview!

**Questions?** Check the full guide in `LIVEKIT_INTEGRATION_COMPLETE.md`

