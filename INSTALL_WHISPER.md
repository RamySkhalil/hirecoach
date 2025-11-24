# Quick Installation Guide: OpenAI Whisper STT

## 🚀 Quick Start (5 minutes)

### Step 1: Install OpenAI SDK

```bash
cd frontend
npm install openai
```

### Step 2: Configure Environment

Create `frontend/.env.local` with:

```env
# OpenAI API Key (REQUIRED - get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Backend URL (already configured)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Enable question voice (optional)
NEXT_PUBLIC_ENABLE_QUESTION_TTS=true
```

**⚠️ IMPORTANT:** 
- Do NOT add `NEXT_PUBLIC_` prefix to `OPENAI_API_KEY`
- Never commit `.env.local` to git (it's already in `.gitignore`)

### Step 3: Start the App

```bash
# Terminal 1: Backend (optional, only needed for TTS)
cd backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Step 4: Test It!

1. Go to http://localhost:3000
2. Start an interview session
3. Click the microphone button 🎤
4. Speak your answer
5. Wait for "Transcribing..." to finish
6. Your text appears in the input box!

---

## ✅ What Changed

### Added Files
- ✅ `frontend/app/api/transcribe/route.ts` - Whisper API endpoint
- ✅ `frontend/components/WhisperVoiceInput.tsx` - Recording component
- ✅ `WHISPER_SETUP.md` - Detailed documentation

### Modified Files
- ✅ `frontend/app/interview/session/[sessionId]/page.tsx` - Now uses WhisperVoiceInput

### Deprecated Files (renamed to `.deprecated`)
- ❌ `ContinuousVoiceInput.tsx.deprecated` - Old Web Speech API
- ❌ `LiveKitInterview.tsx.deprecated` - Old LiveKit integration

### Unchanged (Everything Else Works!)
- ✅ Hedra avatar rendering (InterviewAvatar)
- ✅ ElevenLabs TTS for questions
- ✅ Interview logic and scoring
- ✅ Chat interface and UI
- ✅ All other features

---

## 📦 Package Requirements

```json
{
  "dependencies": {
    "openai": "^4.x.x"  // ← NEW: OpenAI SDK for Whisper
    // ... all existing packages remain unchanged
  }
}
```

---

## 🎯 How It Works

```
┌─────────────┐
│   User      │
│  Speaks 🗣️  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ MediaRecorder   │ (Browser records audio)
│ (WebM/Opus)     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Audio Blob      │ (Sends to backend)
│ (~100KB/30sec)  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ /api/transcribe │ (Next.js API route)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ OpenAI Whisper  │ (Transcription)
│ API             │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Text Response   │ (Returns to frontend)
│ "Hello world"   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Interview Form  │ (User can edit/submit)
└─────────────────┘
```

---

## 🔧 Troubleshooting

### Error: "OPENAI_API_KEY not configured"
**Solution:** Add `OPENAI_API_KEY=sk-proj-...` to `frontend/.env.local` (without `NEXT_PUBLIC_` prefix)

### Error: "Module not found: 'openai'"
**Solution:** Run `npm install openai` in the `frontend` directory

### Error: "Microphone access denied"
**Solution:** Click the lock icon in your browser's address bar → Allow microphone

### Error: "No audio recorded"
**Solution:** 
- Check your microphone is plugged in and not muted
- Close other apps using the microphone (Discord, Teams, etc.)
- Try a different browser (Chrome or Edge work best)

### Silence detection doesn't work
**Solution:** 
- Speak louder or closer to the microphone
- Check system microphone volume is not too low
- Reduce background noise

### Frontend won't start after installing openai
**Solution:** 
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 💰 Cost Analysis

**OpenAI Whisper Pricing:** $0.006 per minute

**Example Scenarios:**
- 1 interview (5 questions × 1 min each): $0.03
- 10 interviews: $0.30
- 100 interviews/month: $3.00
- 1,000 interviews/month: $30.00

**Comparison:**
- Web Speech API: Free but unreliable ❌
- Deepgram Streaming: ~$0.0125/min ($12.50/1000 min) 💰
- OpenAI Whisper: $0.006/min ($6/1000 min) ✅ Best value!

---

## 🎨 UI Features

### Visual Feedback
- 🎤 **Microphone Button** - Red when recording, blue when transcribing
- 📊 **Volume Indicator** - Real-time audio level bar
- ⏱️ **Silence Detection** - Auto-stops after 2s of silence
- ⚠️ **Error Messages** - Clear, actionable error messages
- 🔄 **Loading State** - "Transcribing..." with spinner

### User Experience
- **Click to start** recording
- **Click again to stop** (or wait for auto-stop)
- **Visual feedback** during recording and transcription
- **Edit before submit** - transcribed text goes to input field first
- **No continuous connection** - only sends audio when recording stops

---

## 🧪 Testing Checklist

After installation, test these scenarios:

- [ ] Click mic button → record 5 seconds → click again → see transcription
- [ ] Record and stay silent for 2+ seconds → auto-stops
- [ ] Try with background noise → still transcribes correctly
- [ ] Try very quiet speech → shows "No speech detected" error
- [ ] Try with no microphone → shows "No microphone found" error
- [ ] Try in Chrome, Edge, and Safari → works in all
- [ ] Submit answer after transcription → goes to next question
- [ ] Check browser console → no errors

---

## 📚 Additional Resources

- **OpenAI Whisper Docs:** https://platform.openai.com/docs/guides/speech-to-text
- **MediaRecorder API:** https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder
- **Full Setup Guide:** See `WHISPER_SETUP.md` for detailed technical documentation

---

## 🆘 Need Help?

1. Check browser console (F12) for detailed error logs
2. Verify `.env.local` file exists and has correct format
3. Test OpenAI API key directly: https://platform.openai.com/playground/audio
4. Ensure microphone works in system settings
5. Try a different browser (Chrome/Edge recommended)

---

## ✨ Success Indicators

You'll know everything is working when:

1. ✅ Frontend starts without errors (`npm run dev`)
2. ✅ Mic button appears in interview session
3. ✅ Clicking mic button shows "Recording..." status
4. ✅ Volume bar moves when you speak
5. ✅ After stopping, shows "Transcribing..." with spinner
6. ✅ Transcribed text appears in the input box
7. ✅ Can edit and submit the answer normally

**Congratulations! 🎉 OpenAI Whisper STT is now fully integrated!**

