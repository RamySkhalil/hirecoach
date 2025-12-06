# Quick Start: Hedra Avatar Setup

## Installation Steps

### 1. Install Dependencies

```bash
cd backend/livekit-voice-agent
pip install -r requirements.txt
```

This will install:
- `livekit-agents[hedra]` - Hedra avatar plugin
- `livekit-agents[images]` - PIL/Pillow for image handling

### 2. Verify Avatar Image

```bash
# Check if avatar.png exists
ls -la ../avatar.png
```

Should show your avatar image in the `backend` folder.

### 3. Set API Key

Make sure your `.env.local` has:

```env
HEDRA_API_KEY=your_key_here
```

### 4. Test the Agent

```bash
python interview_agent.py start
```

Look for these success messages:

```
✅ Avatar image found: /path/to/backend/avatar.png
✅ HEDRA_API_KEY: Set
```

### 5. Run an Interview

1. Start frontend: `npm run dev`
2. Create interview session
3. Join the room
4. **You should see the avatar in the video panel!**

---

## Quick Verification

```bash
# Verify all required packages
pip list | grep livekit

# Should show:
# livekit-agents    1.2.x
# livekit-plugins-hedra    1.x.x
```

---

## If Avatar Doesn't Show

**Checklist:**
1. Is `HEDRA_API_KEY` set in `.env.local`?
2. Does `backend/avatar.png` exist?
3. Did you install the new requirements?
4. Are there any errors in agent logs?

**Quick Fix:**
```bash
# Reinstall with all extras
pip install "livekit-agents[hedra,images]>=1.2.0" --upgrade
```

---

## What You'll See

**Before (Audio Only):**
- Just microphone icon in video panel
- Voice conversation

**After (With Avatar):**
- 512x512px video of AI coach
- Lips synced with speech
- Professional, engaging presence

---

## Next Steps

See `HEDRA_AVATAR_INTEGRATION.md` for:
- Detailed documentation
- Customization options
- Troubleshooting guide
- Advanced features

---

That's it! Your avatar should now be working! 🎉

