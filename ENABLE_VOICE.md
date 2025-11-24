# 🎤 Enable Voice Features

Quick guide to enable Text-to-Speech (question audio) for Interviewly.

## What You're Seeing

If you see this message in the avatar:
```
💡 Voice Feature Not Configured
Configure ELEVENLABS_API_KEY for voice
```

It means the interview is working in **text-only mode**. Questions appear in the chat, but are not read aloud.

## Why Voice Matters

With voice enabled:
- ✅ Questions are automatically read aloud by AI interviewer
- ✅ More realistic interview experience  
- ✅ Practice listening comprehension
- ✅ Better engagement

Without voice:
- ⚠️ Questions only appear as text
- ⚠️ Avatar shows warning message
- ⚠️ Less immersive experience

## Enable Voice in 3 Steps

### Step 1: Get ElevenLabs API Key (FREE)

1. **Go to** https://elevenlabs.io/
2. **Sign up** for free account
3. **Free tier includes**:
   - 10,000 characters per month
   - ~50-100 interview questions
   - High-quality voices
   - No credit card required

4. **Get API key**:
   - Click your profile icon
   - Go to "Profile" → "API Keys"
   - Click "Create API Key"
   - Copy the key (keep it secret!)

### Step 2: Add Key to Backend

**Edit** `backend/.env` file:

```env
# Add this line (replace with your actual key)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Optional: Choose a different voice
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel (default)
ELEVENLABS_MODEL=eleven_multilingual_v2
```

**Don't have a `.env` file?**

```bash
# Windows
copy backend\env.example backend\.env

# Mac/Linux
cp backend/env.example backend/.env
```

Then edit it with your API key.

### Step 3: Restart Backend

```bash
# Stop backend (Ctrl+C in terminal)

# Restart
cd backend
uvicorn app.main:app --reload
```

## Test It Works

1. **Start new interview** at http://localhost:3000
2. **Look at avatar** (left side):
   - Should see animated waves
   - Should hear question spoken
   - Should say "AI Interviewer is speaking..."
3. **Check chat** (right side):
   - Question appears as text AND audio

### Troubleshooting

**Still not working?**

1. **Check backend console** for errors
2. **Verify API key** is correct (no extra spaces)
3. **Test API key** at https://elevenlabs.io/docs/api-reference
4. **Check free tier limit** (10K chars/month)

**Error: "Invalid API key"**
- Double-check the key in .env
- Make sure it starts with alphanumeric characters
- Verify it's active in ElevenLabs dashboard

**Error: "Quota exceeded"**
- You've used your free 10K characters
- Either wait for next month or upgrade plan

## Voice Settings (Optional)

Want a different voice? Edit `backend/.env`:

```env
# Popular voices:
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel (default, female)
ELEVENLABS_VOICE_ID=VR6AewLTigWG4xSOukaG  # Arnold (male)
ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL  # Bella (female)
```

**Find more voices**:
1. Visit https://elevenlabs.io/voice-library
2. Preview voices
3. Copy Voice ID
4. Update .env file

## Cost Estimates

**Free Tier** (10,000 chars/month):
- ~100 interview questions
- ~20 complete interviews (5 questions each)
- **Perfect for testing!**

**Paid Tier** ($5/month - Starter):
- 30,000 characters
- ~300 questions
- ~60 interviews

**Typical question**: 100-200 characters

## Without Voice (Text-Only Mode)

The app works perfectly without voice:
- ✅ All features work
- ✅ Questions in chat
- ✅ Text/voice answers
- ✅ AI evaluation
- ⚠️ No audio playback

**Good for**:
- Testing the app
- Quiet environments
- Saving API costs
- Quick practice

## Alternative: Use OpenAI Whisper (Future)

Coming soon: OpenAI's TTS as alternative to ElevenLabs.

Pros:
- Same API key as LLM
- Cheaper ($15/1M chars vs $30/1M)
- Good quality

Cons:
- Slightly less natural
- Fewer voice options

---

## Summary

**To enable voice NOW**:

1. Get free API key: https://elevenlabs.io/
2. Add to `backend/.env`: `ELEVENLABS_API_KEY=your_key`
3. Restart backend
4. Enjoy voiced interviews! 🎉

**Total time**: 5 minutes

**Cost**: FREE (10K chars/month)

---

**Questions?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md)

