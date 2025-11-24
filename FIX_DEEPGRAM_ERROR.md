# 🔧 Fix Deepgram "Not Configured" Error

## Issue
Getting "Deepgram not configured. Please add DEEPGRAM_API_KEY to .env" even though the key is in `.env`

## Root Cause
The backend needs to be **restarted** after adding the API key to `.env` file.

---

## ✅ Quick Fix

### Step 1: Verify `.env` File

**Check `backend/.env` has the key:**
```env
DEEPGRAM_API_KEY=your_actual_key_here
```

**Important:**
- No spaces around `=`
- No quotes needed (unless key has spaces)
- Key should start with a string of letters/numbers

### Step 2: Restart Backend

**Stop the backend** (press Ctrl+C in the terminal where it's running)

**Then restart:**
```powershell
cd C:\Personal\hirecoach\backend
uvicorn app.main:app --reload
```

### Step 3: Verify Configuration

**Look for this in the startup logs:**
```
🚀 Starting Interviewly backend...
📊 Database: sqlite:///./interviewly.db

🔑 API Keys Status:
  OpenAI: ✅ Configured
  ElevenLabs: ✅ Configured
    Key preview: sk_a4ae52...
  Deepgram: ✅ Configured    ← Should show ✅
  LLM Provider: openai
  STT Provider: deepgram
```

**If you see:**
```
  Deepgram: ❌ Not set
```

Then the key is not being loaded correctly.

---

## 🔍 Troubleshooting

### If Deepgram still shows "Not set":

#### 1. Check `.env` file location
The file should be at:
```
C:\Personal\hirecoach\backend\.env
```

NOT:
```
C:\Personal\hirecoach\.env  ← Wrong location
```

#### 2. Check `.env` file format

**Good:**
```env
DEEPGRAM_API_KEY=abc123def456
```

**Bad:**
```env
DEEPGRAM_API_KEY = abc123def456  ← Spaces around =
DEEPGRAM_API_KEY="abc123def456"  ← Unnecessary quotes
#DEEPGRAM_API_KEY=abc123def456   ← Commented out
```

#### 3. Check key value

Your Deepgram key should look like:
```
[random letters and numbers, usually starts with letters]
```

Get it from: https://console.deepgram.com/

#### 4. Test manually

**Add a debug print in config.py:**

Edit `backend/app/config.py` and add after the `Settings` class:
```python
settings = Settings()
print(f"DEBUG: Deepgram key loaded: {settings.deepgram_api_key[:10] if settings.deepgram_api_key else 'None'}...")
```

Restart backend and check if it prints the key preview.

---

## 🎯 Alternative Solutions

### Option 1: Use Whisper Instead

If Deepgram continues to have issues, switch to OpenAI Whisper:

**In `backend/.env`:**
```env
STT_PROVIDER=whisper
OPENAI_API_KEY=sk-...
```

**Restart backend**

### Option 2: Disable Voice Temporarily

Use text input instead of voice recording until Deepgram is configured.

---

## ✅ Verification Steps

After restart, test voice recording:

1. **Go to interview session**
   ```
   http://localhost:3000/interview/session/[id]
   ```

2. **Click microphone button**

3. **Record a test message**
   "This is a test"

4. **Check transcription**
   - Should show your text
   - Not "Deepgram not configured"

---

## 📊 Expected Behavior

### With Deepgram Configured:
```
[User records: "Hello, my name is John"]
→ Transcription: "Hello, my name is John"
→ Appears in text box
→ Can submit as answer
```

### Without Deepgram:
```
[User records audio]
→ Transcription: "Deepgram not configured..."
→ Error message shown
```

---

## 🔑 Getting Deepgram API Key

1. Go to https://console.deepgram.com/
2. Sign up / Sign in
3. Go to "API Keys"
4. Create new key or copy existing
5. Add to `backend/.env`:
   ```env
   DEEPGRAM_API_KEY=paste_key_here
   ```
6. Restart backend

---

## 🚀 Final Checklist

- [ ] `.env` file in `backend/` folder (not root)
- [ ] `DEEPGRAM_API_KEY=...` line in `.env`
- [ ] No extra spaces or quotes
- [ ] Backend restarted
- [ ] Startup logs show "✅ Configured"
- [ ] Voice recording works

---

## 💡 Quick Test

**Without restarting, just check the config:**

```powershell
cd backend
python -c "from app.config import settings; print(settings.deepgram_api_key)"
```

Should print your key (or `None` if not loaded).

---

**Once you restart the backend with the correct key, voice recording will work!** 🎤✅

