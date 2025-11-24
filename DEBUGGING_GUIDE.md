# Debugging Guide - Recording & AI Voice Issues

## Issue 1: Recording Not Working

### Check Browser Console

Open browser console (F12) and look for these messages:

#### ✅ **What You SHOULD See (Working)**
```
[Whisper] startRecording called, current state: {...}
[Whisper] Recording started successfully with audio/webm;codecs=opus
[Whisper] MediaRecorder state: recording
[Whisper] Recording stopped, processing...
[Whisper] processRecording called, chunks: 10
[Whisper] Created blob: 12345 bytes, type: audio/webm
[Whisper] Sending to /api/transcribe...
[Whisper] Received transcript: "Hello world"
[Whisper] Valid transcription, calling onTranscript
[Whisper] Auto-restarting recording (continuous mode)
```

#### ❌ **What Indicates Problems**

**Problem 1: No audio chunks**
```
[Whisper] processRecording called, chunks: 0
[Whisper] No audio data recorded - chunks array is empty
```
**Fix:** Microphone not capturing audio, check permissions

**Problem 2: Empty blob**
```
[Whisper] Created blob: 0 bytes
```
**Fix:** MediaRecorder not collecting data

**Problem 3: API error**
```
[Whisper] Transcription failed: OPENAI_API_KEY not configured
```
**Fix:** Add API key to `frontend/.env.local`

**Problem 4: Not auto-restarting**
```
[Whisper] Not restarting (isActive: false disabled: true)
```
**Fix:** Component not active or disabled

### Step-by-Step Debugging

#### Step 1: Check Microphone Permission
```
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for: "[Whisper] Recording started successfully"
4. If you see "Microphone access denied" → Allow permission
```

#### Step 2: Check OpenAI API Key
```
1. Check frontend/.env.local exists
2. Verify it has: OPENAI_API_KEY=sk-proj-...
3. Restart frontend: npm run dev
4. Refresh browser
```

#### Step 3: Test Microphone in System
```
Windows:
1. Right-click speaker icon → Sound settings
2. Input → Test your microphone
3. Speak - bar should move
4. If not working, select different mic

Mac:
1. System Preferences → Sound → Input
2. Select microphone
3. Speak - input level should move
```

#### Step 4: Check Browser Console for Errors
```
1. F12 → Console tab
2. Clear console
3. Start interview
4. Look for RED errors
5. Copy entire error message
```

---

## Issue 2: AI Not Talking (TTS Not Working)

### Requirements for AI Voice

1. **Backend must be running**
   ```bash
   cd backend
   .venv\Scripts\activate
   python -m uvicorn app.main:app --reload
   ```

2. **ElevenLabs API key configured** (backend)
   ```
   Check backend/.env has:
   ELEVENLABS_API_KEY=your_key_here
   ```

3. **TTS enabled in frontend**
   ```
   frontend/.env.local must have:
   NEXT_PUBLIC_ENABLE_QUESTION_TTS=true
   ```

4. **Question must have audio endpoint**
   ```
   Backend must support: GET /interview/question/{id}/audio
   ```

### Check TTS Status

#### Check 1: Environment Variable
```javascript
// Open browser console
console.log(process.env.NEXT_PUBLIC_ENABLE_QUESTION_TTS);
// Should show: "true" (not true without quotes)
```

#### Check 2: Backend Running
```
Open: http://localhost:8000/docs
Should see FastAPI Swagger UI
If not: Backend not running
```

#### Check 3: ElevenLabs Configured
```
Check backend logs when starting:
Should see: ElevenLabs: ✅ Configured
Not: ElevenLabs: ❌ Not set
```

#### Check 4: Audio Request
```
Open Network tab (F12)
Look for: /interview/question/1/audio
Status should be: 200 OK
If 404: Backend route missing
If 500: ElevenLabs error
```

### Common TTS Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Voice not configured" | TTS disabled or key missing | Add ELEVENLABS_API_KEY to backend/.env |
| 404 on /audio endpoint | Backend route missing | Check backend has TTS routes |
| No sound but 200 OK | Browser blocked autoplay | Click play button manually first time |
| CORS error | Backend CORS not configured | Check backend allows localhost:3000 |

---

## Quick Fix Checklist

### For Recording Issues:
- [ ] Microphone permission allowed in browser
- [ ] `OPENAI_API_KEY` in `frontend/.env.local`
- [ ] Frontend restarted after adding API key
- [ ] Microphone not used by other app (Discord, Teams, etc.)
- [ ] Browser console shows "[Whisper] Recording started successfully"
- [ ] After 2 seconds of silence, shows "[Whisper] processRecording called"

### For AI Voice Issues:
- [ ] Backend is running (`python -m uvicorn app.main:app --reload`)
- [ ] `ELEVENLABS_API_KEY` in `backend/.env`
- [ ] `NEXT_PUBLIC_ENABLE_QUESTION_TTS=true` in `frontend/.env.local`
- [ ] Frontend restarted after env change
- [ ] Backend logs show "ElevenLabs: ✅ Configured"
- [ ] Network tab shows 200 OK for `/interview/question/N/audio`

---

## Test Commands

### Test 1: Check API Keys Loaded
```bash
# Frontend (in frontend directory)
npm run dev
# Check startup output - should not show env errors

# Backend (in backend directory)
python -c "from app.config import settings; print('OpenAI:', 'OK' if settings.openai_api_key else 'MISSING'); print('ElevenLabs:', 'OK' if settings.elevenlabs_api_key else 'MISSING')"
```

### Test 2: Test Microphone Access
```javascript
// Paste in browser console
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    console.log('✅ Microphone access granted');
    stream.getTracks().forEach(track => track.stop());
  })
  .catch(err => console.error('❌ Microphone error:', err));
```

### Test 3: Test Whisper API Directly
```bash
# Create a test audio file first, then:
curl -X POST http://localhost:3000/api/transcribe \
  -F "file=@test-audio.wav"
```

### Test 4: Test TTS API Directly
```bash
# Backend must be running
curl http://localhost:8000/interview/question/1/audio \
  -o test-tts.mp3

# If successful, plays audio file
```

---

## Common Solutions

### "Recording starts but no transcription"

**Cause:** Audio chunks not being collected

**Fix:**
```javascript
// Check in browser console:
console.log(MediaRecorder.isTypeSupported('audio/webm;codecs=opus'));
// Should return true

// If false, browser doesn't support webm - try different browser
```

### "Transcription fails immediately"

**Cause:** API key not loaded or invalid

**Fix:**
```bash
# Verify API key format (should start with sk-proj-)
cd frontend
cat .env.local | grep OPENAI

# Should show: OPENAI_API_KEY=sk-proj-...
# NOT: NEXT_PUBLIC_OPENAI_API_KEY=...

# Restart frontend
npm run dev
```

### "AI never talks"

**Cause 1:** TTS not enabled
```bash
# Check frontend/.env.local has:
NEXT_PUBLIC_ENABLE_QUESTION_TTS=true
# Note: Must be string "true", not boolean
```

**Cause 2:** Backend not running
```bash
# Check backend is running:
curl http://localhost:8000/docs
# Should return HTML
```

**Cause 3:** ElevenLabs key missing
```bash
# Check backend/.env has:
ELEVENLABS_API_KEY=your_key_here

# Test with:
cd backend
.venv\Scripts\activate
python -c "from app.config import settings; print(settings.elevenlabs_api_key[:10] if settings.elevenlabs_api_key else 'MISSING')"
```

---

## Still Not Working?

### Collect Debug Information

1. **Browser Console Log**
   ```
   F12 → Console → Right-click → Save as...
   Save all console output
   ```

2. **Network Tab**
   ```
   F12 → Network tab → Record
   Try recording → Right-click → "Copy all as HAR"
   ```

3. **Backend Logs**
   ```
   Copy entire backend terminal output
   ```

4. **Environment Files** (remove API keys before sharing!)
   ```
   # Frontend
   cat frontend/.env.local | sed 's/sk-.*$/sk-REDACTED/'
   
   # Backend  
   cat backend/.env | sed 's/sk-.*$/sk-REDACTED/' | sed 's/key_.*$/key_REDACTED/'
   ```

5. **Browser & OS Info**
   ```
   Browser: Chrome/Edge/Safari + version
   OS: Windows/Mac/Linux + version
   Microphone: Built-in / USB / Bluetooth
   ```

---

## Expected Behavior (Working System)

### Recording Flow
1. Interview starts → Auto-record begins (no button)
2. Red indicator shows "🎤 Listening..."
3. Volume bar moves when speaking
4. After 2s silence → "Transcribing..." appears
5. Text appears in input box
6. Recording auto-restarts immediately
7. Continuous loop - no clicking needed

### AI Voice Flow
1. Question appears on screen
2. Avatar starts speaking (audio plays)
3. Progress bar shows during playback
4. Audio completes
5. Your turn to answer

### Full Interview Flow
1. Start → AI speaks question
2. Auto-record starts
3. You answer
4. Auto-transcribe
5. Submit answer
6. AI evaluates (text feedback)
7. Next question → AI speaks
8. Repeat...

---

## Emergency Fallback

If nothing works, use **manual text input** while debugging:

1. Disable voice input:
   ```typescript
   // In page.tsx, set:
   const [voiceEnabled, setVoiceEnabled] = useState(false);
   ```

2. Type answers manually in text box

3. Debug recording separately:
   ```bash
   # Test recording in isolation
   cd frontend
   npm run dev
   # Open http://localhost:3000/test-recording (if you create test page)
   ```

---

## Success Indicators

You'll know everything is working when:

✅ Console shows: "[Whisper] Recording started successfully"  
✅ Red mic indicator pulses when active  
✅ Volume bar moves when speaking  
✅ After silence: "Transcribing..." appears  
✅ Text appears in input box  
✅ Recording auto-restarts after transcription  
✅ AI voice plays question audio  
✅ No errors in console  

---

**Need more help? Share the console logs and I'll debug further!**

