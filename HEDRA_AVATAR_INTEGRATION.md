# Hedra Avatar Integration

## Overview
Your AI Interview Agent now includes a visual avatar powered by Hedra! The avatar will display in the video panel during interviews, creating a more engaging and human-like experience.

---

## What's New

✅ **Visual Avatar** - AI interviewer now has a face using your `avatar.png`
✅ **Synchronized Speech** - Avatar lips move in sync with voice
✅ **Automatic Setup** - Loads `backend/avatar.png` automatically
✅ **Fallback Mode** - Works without avatar if image/API key missing
✅ **512x512px Video** - Professional avatar rendering

---

## Requirements

### 1. Hedra API Key ✅
You've already added `HEDRA_API_KEY` to your `.env.local` file.

### 2. Avatar Image ✅
You have `backend/avatar.png` ready to use.

### 3. Updated Dependencies
Install the new requirements:

```bash
cd backend/livekit-voice-agent
pip install -r requirements.txt
```

Or manually:
```bash
pip install "livekit-agents[hedra,images]>=1.2.0"
```

---

## How It Works

### Avatar Loading Process

1. **Agent starts** → Loads `backend/avatar.png`
2. **Hedra initializes** → Uploads image to Hedra API
3. **Avatar joins room** → Appears as video participant
4. **Speech synthesis** → Avatar lips sync with TTS
5. **Frontend displays** → Video shows in LiveKit panel

### Technical Flow

```python
# 1. Load avatar image
avatar_image = Image.open("../avatar.png")

# 2. Initialize Hedra session
avatar = hedra.AvatarSession(
    avatar_image=avatar_image,
    avatar_participant_name="AI Interview Coach",
)

# 3. Start avatar (must be before session.start)
await avatar.start(session, room=ctx.room)

# 4. Start agent session
await session.start(room=ctx.room, agent=agent, ...)
```

---

## Configuration

### Environment Variables

Add to `backend/livekit-voice-agent/.env.local`:

```env
# Hedra Configuration
HEDRA_API_KEY=your_hedra_api_key_here

# Existing configs
LIVEKIT_URL=wss://your-livekit-instance.com
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
OPENAI_API_KEY=your_openai_key
BACKEND_URL=http://localhost:8000
```

### Avatar Image Requirements

**Supported Formats:**
- PNG, JPG, JPEG
- 512x512px recommended
- Humanoid faces work best
- Photo-realistic or animated styles

**Image Guidelines:**
- Clear, well-lit face
- Centered composition
- Hedra auto-crops around face
- Works with various styles

---

## Files Modified

### 1. `backend/livekit-voice-agent/requirements.txt`

**Before:**
```python
livekit-agents>=0.8.0
```

**After:**
```python
livekit-agents[hedra,images]>=1.2.0
```

- Added `[hedra]` extra for avatar plugin
- Added `[images]` extra for PIL/Pillow support
- Updated to version 1.2+ for latest features

### 2. `backend/livekit-voice-agent/interview_agent.py`

**New Imports:**
```python
from PIL import Image
from livekit.plugins import hedra
```

**New Features:**
- Avatar image loading
- Hedra session initialization
- Avatar startup before agent session
- Fallback handling if avatar unavailable
- Debug logging for avatar status

---

## Usage

### Starting the Agent

```bash
cd backend/livekit-voice-agent
python interview_agent.py start
```

You'll see:

```
============================================================
🎤 LiveKit AI Interview Agent with Hedra Avatar
============================================================
LIVEKIT_URL: wss://your-instance.livekit.cloud
LIVEKIT_API_KEY: Set
OPENAI_API_KEY: Set
HEDRA_API_KEY: Set
BACKEND_URL: http://localhost:8000
============================================================
✅ Avatar image found: /path/to/backend/avatar.png

Waiting for interview sessions...
```

### During Interview

When a candidate joins:

```
✅ AI Interview Agent joining room: interview-abc123
   Session ID: abc123
   Job Title: Software Engineer
   Seniority: senior
   Questions: 5
✅ Loaded avatar image from: /path/to/backend/avatar.png
✅ Hedra avatar initialized
🎬 Starting Hedra avatar...
✅ Hedra avatar started and joined the room
✅ Agent greeted candidate in room: interview-abc123
```

---

## Frontend Experience

### What Users See

1. **Video Panel (Left):**
   - AI Interview Coach avatar (512x512px)
   - Lips moving synchronized with speech
   - Professional, engaging presence

2. **Transcription Panel (Right):**
   - Real-time conversation transcript
   - Same as before

### Participant List

The room will show:
- **"You"** - The candidate
- **"AI Interview Coach"** - The Hedra avatar
- Both with video/audio tracks

---

## Error Handling & Fallback

The agent gracefully handles missing components:

### If avatar.png is missing:
```
⚠️ Avatar image not found at: /path/to/backend/avatar.png
```
→ Agent continues **without avatar** (audio-only)

### If HEDRA_API_KEY is not set:
```
⚠️ HEDRA_API_KEY not set, avatar disabled
```
→ Agent continues **without avatar** (audio-only)

### If avatar fails to start:
```
⚠️ Failed to start avatar: [error message]
```
→ Agent continues **without avatar** (audio-only)

**The interview always works**, avatar is an enhancement!

---

## Troubleshooting

### Avatar Not Showing

**Check 1: Image File**
```bash
ls -la backend/avatar.png
```
Should show the file exists.

**Check 2: API Key**
```bash
grep HEDRA_API_KEY backend/livekit-voice-agent/.env.local
```
Should show your key.

**Check 3: Dependencies**
```bash
pip show livekit-plugins-hedra
```
Should show version 1.2.0 or higher.

**Check 4: Agent Logs**
Look for these messages in agent output:
- ✅ Loaded avatar image
- ✅ Hedra avatar initialized
- ✅ Hedra avatar started

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'livekit.plugins.hedra'`
**Solution:**
```bash
pip install "livekit-agents[hedra]>=1.2.0"
```

**Issue:** `ModuleNotFoundError: No module named 'PIL'`
**Solution:**
```bash
pip install "livekit-agents[images]>=1.2.0"
```

**Issue:** Avatar video is black/frozen
**Solution:**
- Check internet connection (uploads to Hedra)
- Verify HEDRA_API_KEY is valid
- Try a different avatar.png image

**Issue:** "Avatar image not found"
**Solution:**
```bash
# Verify path is correct
cd backend/livekit-voice-agent
python -c "import os; print(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'avatar.png'))"
```

---

## Performance Notes

### First Load
- Avatar image uploaded to Hedra (one-time)
- Takes a few seconds on first session
- Subsequent sessions are faster

### Video Quality
- 512x512px resolution
- 30 FPS typical
- Synced with audio

### Resource Usage
- Minimal CPU on your server
- Avatar rendering done by Hedra
- Published as video track to room

---

## Customization

### Using Different Avatar

Replace `backend/avatar.png` with any image:

```bash
cp /path/to/your/photo.png backend/avatar.png
```

Or use Hedra avatar ID:

```python
avatar = hedra.AvatarSession(
    avatar_id="your-hedra-avatar-id",  # Instead of avatar_image
    avatar_participant_name="AI Interview Coach",
)
```

### Changing Avatar Name

```python
avatar = hedra.AvatarSession(
    avatar_image=avatar_image,
    avatar_participant_name="Career Coach",  # Custom name
)
```

### Additional Options

See [Hedra plugin reference](https://docs.livekit.io/reference/python/v1/livekit/plugins/hedra/) for more parameters.

---

## Cost Considerations

### Hedra Pricing

Check [Hedra pricing](https://hedra.ai/pricing) for current rates.

Typical usage:
- Charged per minute of avatar video
- Only during active interviews
- No cost when agent is idle

### Optimization Tips

1. **Enable only when needed** - Avatar adds value but has cost
2. **Monitor usage** - Track via Hedra dashboard
3. **Consider fallback** - Disable avatar for free tier users

---

## Future Enhancements

Possible improvements:

- [ ] User-selectable avatars (different coaches)
- [ ] Dynamic avatar emotions (smiling, thinking)
- [ ] Custom avatar per job role
- [ ] Avatar gestures/body language
- [ ] Multiple avatar styles (professional, casual)
- [ ] User uploads their own avatar preference

---

## Testing Checklist

- [ ] Avatar image loads correctly
- [ ] Hedra API key is valid
- [ ] Avatar appears in video panel
- [ ] Lips sync with speech
- [ ] No lag or stuttering
- [ ] Fallback works without avatar
- [ ] Works on mobile devices
- [ ] Multiple concurrent interviews work

---

## Summary

Your AI Interview Agent now features:

🎭 **Visual Avatar** - Professional AI coach with a face
🎙️ **Synchronized Speech** - Lips move naturally with voice
🖼️ **Your Image** - Uses your custom `avatar.png`
🛡️ **Robust Fallback** - Works without avatar if needed
🚀 **Easy Setup** - Automatically loads and configures

Just make sure:
1. ✅ `HEDRA_API_KEY` in `.env.local`
2. ✅ `backend/avatar.png` exists
3. ✅ Dependencies installed
4. ✅ Agent running

The avatar will automatically appear in interviews! 🎉

