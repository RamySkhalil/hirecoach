# OpenAI Whisper STT Integration Setup

This project now uses **OpenAI Whisper** for Speech-to-Text (STT) transcription, replacing Web Speech API and LiveKit STT.

## Architecture Overview

```
User Speech → MediaRecorder (Browser) → Audio Blob → /api/transcribe → OpenAI Whisper API → Text → Interview Agent
```

### Key Components

1. **`frontend/app/api/transcribe/route.ts`** - Next.js API route that handles Whisper transcription
2. **`frontend/components/WhisperVoiceInput.tsx`** - React component for audio recording with MediaRecorder
3. **`frontend/app/interview/session/[sessionId]/page.tsx`** - Interview page using WhisperVoiceInput

### Features

✅ **High-Quality Transcription** - OpenAI Whisper provides industry-leading accuracy  
✅ **Silence Detection** - Automatically stops recording after 2 seconds of silence  
✅ **Visual Feedback** - Real-time volume indicator and status messages  
✅ **Error Handling** - Graceful error recovery with user-friendly messages  
✅ **Browser Compatibility** - Works in Chrome, Edge, Safari (any browser with MediaRecorder API)  
✅ **Production Ready** - TypeScript, proper error handling, and loading states  

---

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install openai
```

### 2. Configure Environment Variables

Create or update `frontend/.env.local`:

```env
# OpenAI API Key (required for Whisper transcription)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx

# Backend API URL (already configured)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Enable TTS for questions (optional)
NEXT_PUBLIC_ENABLE_QUESTION_TTS=true
```

**Important:** 
- `OPENAI_API_KEY` should **NOT** have the `NEXT_PUBLIC_` prefix (it's server-side only)
- Get your API key from: https://platform.openai.com/api-keys

### 3. Start the Application

```bash
# Terminal 1: Backend (if using ElevenLabs TTS)
cd backend
.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate  # Mac/Linux
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 4. Test the Integration

1. Navigate to an interview session
2. Click the microphone button to start recording
3. Speak your answer clearly
4. Recording will auto-stop after 2 seconds of silence (or click mic button again to stop manually)
5. Wait for transcription (shows "Transcribing..." indicator)
6. Your transcribed text appears in the text input field
7. Click Send or press Enter to submit

---

## Technical Details

### Audio Recording

- **API:** MediaRecorder (native browser API)
- **Format:** WebM/Opus (fallback to OGG, MP4, WAV based on browser support)
- **Sample Rate:** 48kHz (default)
- **Bit Rate:** 128 kbps
- **Features:** Echo cancellation, noise suppression, auto-gain control

### Whisper API

- **Model:** `whisper-1` (OpenAI's latest Whisper model)
- **Language:** English (`en` - can be removed for auto-detection)
- **Response Format:** JSON
- **Max File Size:** 25MB (MediaRecorder typically produces much smaller files)

### Silence Detection

- **Threshold:** 0.01 (normalized volume 0-1)
- **Duration:** 2000ms (2 seconds)
- **Method:** Real-time FFT analysis using Web Audio API

---

## Cost Considerations

**OpenAI Whisper Pricing** (as of 2024):
- $0.006 per minute of audio transcribed

**Example costs:**
- 30-second answer: $0.003 (less than half a cent)
- 10 interview sessions × 5 questions × 1 min avg: $0.30
- 100 interviews/month: ~$3.00

Much more cost-effective than continuous STT streaming (LiveKit, Deepgram).

---

## Troubleshooting

### "Microphone access denied"
- **Solution:** Allow microphone permission in browser settings
- **Chrome:** Click lock icon in address bar → Site settings → Microphone → Allow

### "No microphone found"
- **Solution:** Connect a microphone or use built-in laptop mic
- **Check:** System sound settings to verify mic is recognized

### "Microphone is in use by another app"
- **Solution:** Close Discord, Teams, Zoom, or other apps using the microphone

### "Transcription failed"
- **Check:** `OPENAI_API_KEY` is correctly set in `frontend/.env.local`
- **Check:** API key is valid and has credits
- **Check:** Network connection is stable
- **Check:** Browser console for detailed error messages

### "Empty transcription"
- **Solution:** Speak louder and more clearly
- **Solution:** Check microphone is not muted
- **Solution:** Reduce background noise

---

## Removed Components

The following components have been deprecated (renamed to `.deprecated`):

- ❌ `ContinuousVoiceInput.tsx` - Web Speech API (unreliable, browser-dependent)
- ❌ `LiveKitInterview.tsx` - LiveKit STT (doesn't work on Windows, requires agent worker)

These files are kept for reference but are no longer used in the application.

---

## Advantages Over Previous Solutions

### vs Web Speech API
- ✅ **More Accurate** - Whisper has better recognition, especially for accents
- ✅ **Language Support** - 99+ languages vs limited browser support
- ✅ **Consistent** - Same quality across all browsers
- ✅ **No Continuous Connection** - Only sends audio when needed (lower bandwidth)

### vs LiveKit
- ✅ **No Agent Worker** - No need to run Python agent on server
- ✅ **No WebSocket** - Simpler architecture, easier deployment
- ✅ **Works on Windows** - No SSL/networking issues
- ✅ **Cost-Effective** - Pay per transcription, not per minute of connection

### Hedra Avatar Integration

The Whisper STT integration **does not affect**:
- ✅ Hedra avatar rendering (InterviewAvatar component)
- ✅ ElevenLabs TTS for question playback
- ✅ Interview logic and scoring
- ✅ Chat interface and UI

Everything else remains unchanged - only the STT method was replaced.

---

## Future Enhancements

Potential improvements for the future:

1. **Real-time Transcription** - Stream audio chunks for faster feedback
2. **Multi-language Support** - Auto-detect or let user select language
3. **Confidence Scores** - Use Whisper's verbose mode to show confidence
4. **Audio Preprocessing** - Noise reduction before sending to Whisper
5. **Offline Fallback** - Use browser STT if Whisper API is unavailable
6. **Push-to-Talk Mode** - Alternative to silence detection

---

## Support

For issues or questions:
1. Check browser console for detailed error logs
2. Verify environment variables are set correctly
3. Test with the Whisper API directly: https://platform.openai.com/playground/audio
4. Check OpenAI API status: https://status.openai.com/

