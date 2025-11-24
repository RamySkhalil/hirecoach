# Quick Fix Checklist - Recording & AI Voice

## ✅ Recording Issue - SOLVED!

Recording is working! I've added:
1. **Volume logging** - See volume levels in console
2. **Manual stop button** - Click "Stop & Transcribe" if silence detection doesn't trigger
3. **Better silence threshold** - More sensitive to quiet pauses

### What to do now:
1. **Refresh browser**
2. **Start interview**
3. **Speak your answer**
4. Watch console for: `[Whisper] 📊 Volume: X%`
5. **After finishing, wait 2 seconds** OR **click "Stop & Transcribe"**
6. Should see transcription!

---

## ❌ AI Voice Issue - TO FIX

The AI won't speak because TTS is not properly configured. Here's the **exact checklist**:

### Step 1: Check Backend .env

File: `backend/.env`

**Must have:**
```env
ELEVENLABS_API_KEY=your_actual_elevenlabs_key_here
```

**Get key from:** https://elevenlabs.io/app/speech-synthesis

### Step 2: Check Frontend .env.local

File: `frontend/.env.local`

**Must have (exactly like this):**
```env
NEXT_PUBLIC_ENABLE_QUESTION_TTS=true
OPENAI_API_KEY=sk-proj-your_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**CRITICAL:** The value must be the string `"true"` not boolean `true`

### Step 3: Restart BOTH servers

```bash
# Terminal 1: Stop backend (Ctrl+C), then:
cd backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload

# Look for this in startup logs:
# ElevenLabs: ✅ Configured

# Terminal 2: Stop frontend (Ctrl+C), then:
cd frontend
npm run dev
```

### Step 4: Test

1. Go to http://localhost:3000
2. Start interview
3. **Wait for question to appear**
4. **You should hear audio** playing the question
5. If you see avatar but no sound:
   - Check browser didn't block autoplay
   - Check volume is up
   - Check Network tab for `/interview/question/1/audio` (should be 200 OK)

---

## Quick Tests

### Test 1: Check ElevenLabs Key
```bash
cd backend
.venv\Scripts\activate
python -c "from app.config import settings; print('ElevenLabs:', 'CONFIGURED ✅' if settings.elevenlabs_api_key else 'MISSING ❌')"
```

**Expected output:** `ElevenLabs: CONFIGURED ✅`

### Test 2: Check Frontend Env
Open browser console and type:
```javascript
console.log(process.env.NEXT_PUBLIC_ENABLE_QUESTION_TTS);
```

**Expected output:** `"true"` (with quotes)
**If shows:** `undefined` → env var not loaded, restart frontend

### Test 3: Test TTS API Directly
```bash
# With backend running:
curl http://localhost:8000/interview/question/1/audio -o test.mp3

# If successful, you'll have a test.mp3 file with audio
# Play it to verify TTS works
```

---

## Common Issues

### Issue: "Voice not configured" message
**Fix:** Add `ELEVENLABS_API_KEY` to `backend/.env` and restart backend

### Issue: No sound but no error
**Fix:** Check browser autoplay settings, click play button manually first time

### Issue: 404 on /audio endpoint
**Fix:** Backend TTS route not registered, check `backend/app/main.py` includes TTS routes

### Issue: Still no TTS after following all steps
**Fix:** Check backend logs for errors when you try to play audio

---

## Expected Behavior

### When Working:
1. Start interview
2. Question appears on screen
3. **Audio automatically plays** (AI voice reading question)
4. Avatar pulses during playback
5. When audio finishes, your turn to answer
6. Recording auto-starts
7. You speak
8. Auto-transcribe after 2s silence or manual stop
9. Submit answer
10. Next question (repeat)

### If Not Working:
- ❌ No audio plays
- ❌ Just see text question
- ❌ Avatar doesn't pulse
- ✅ Still can type answer manually
- ✅ Interview still works (just no voice)

---

## Files to Check

### backend/.env
```bash
# Should contain (among other things):
ELEVENLABS_API_KEY=your_key_here
OPENAI_API_KEY=sk-proj-your_key_here
```

### frontend/.env.local
```bash
# Should contain:
NEXT_PUBLIC_ENABLE_QUESTION_TTS=true
OPENAI_API_KEY=sk-proj-your_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**NOTE:** 
- `OPENAI_API_KEY` in frontend = for Whisper (transcription)
- `ELEVENLABS_API_KEY` in backend = for TTS (AI voice)

---

## Status Check Commands

Run these to verify everything is configured:

```bash
# Check backend keys
cd backend
python -c "
from app.config import settings
print('OpenAI:', '✅' if settings.openai_api_key else '❌')
print('ElevenLabs:', '✅' if settings.elevenlabs_api_key else '❌')
print('Deepgram:', '✅' if settings.deepgram_api_key else '❌')
"

# Check backend is running
curl http://localhost:8000/docs
# Should return HTML

# Check TTS endpoint exists
curl http://localhost:8000/interview/question/1/audio
# Should return audio data or error message
```

---

## Final Checklist

Before saying "it doesn't work":

- [ ] `ELEVENLABS_API_KEY` in `backend/.env`
- [ ] `NEXT_PUBLIC_ENABLE_QUESTION_TTS=true` in `frontend/.env.local`
- [ ] `OPENAI_API_KEY` in `frontend/.env.local`
- [ ] Backend restarted after adding keys
- [ ] Frontend restarted after adding env vars
- [ ] Backend logs show "ElevenLabs: ✅ Configured" on startup
- [ ] Browser console shows TTS enabled: `process.env.NEXT_PUBLIC_ENABLE_QUESTION_TTS` = `"true"`
- [ ] Network tab shows request to `/interview/question/N/audio`
- [ ] Browser volume is not muted
- [ ] No autoplay blocked warning in console

If ALL checked and still no voice:
- Copy backend terminal output
- Copy browser console output
- Copy Network tab for `/audio` request
- Send to me for debugging

---

## Success Indicators

You'll know it's working when:
- ✅ Question appears
- ✅ **Audio plays immediately** (AI voice)
- ✅ Avatar pulses/animates during audio
- ✅ After audio, recording auto-starts
- ✅ Volume bar shows when speaking
- ✅ "Stop & Transcribe" button appears
- ✅ Can click button or wait 2s for auto-stop
- ✅ Transcription appears in text box
- ✅ Submit works
- ✅ Next question + audio

**If you're missing the audio part, follow the checklist above!**

