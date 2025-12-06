# Avatar Display Fix

## Issues Fixed

### Issue 1: Multiple Participants (Agent + Avatar)
**Problem:** Seeing both "agent" and "AI Interview Coach" (avatar) as separate participants

**Root Cause:** Agent session was publishing its own audio track, so you had:
- Agent participant (audio only)
- Avatar participant (audio + video)

**Solution:** Disabled audio output from agent session when avatar is active

```python
await session.start(
    room=ctx.room,
    agent=agent,
    room_options=room_io.RoomOptions(
        audio_input=room_io.AudioInputOptions(
            noise_cancellation=lambda params: noise_cancellation.BVC(),
        ),
        audio_output=False if avatar else True,  # Disable when avatar active
    ),
)
```

### Issue 2: Microphone Controls Not Visible
**Problem:** Can't see/access microphone controls in the interface

**Solution:** The `ControlBar` component is already present, but you need to ensure:

1. **Your microphone is enabled in browser**
2. **LiveKit is properly connected**
3. **Controls are not being hidden by CSS**

---

## What You Should See Now

### Participants in Room

✅ **You** (Candidate)
- Your video (if camera enabled)
- Your audio (microphone)

✅ **AI Interview Coach** (Avatar)
- Avatar video (512x512px)
- Synchronized audio
- Lips moving with speech

❌ **No separate "agent" participant**

### Controls (ControlBar)

You should see at bottom of video panel:
- 🎤 **Microphone toggle** (mute/unmute)
- 📹 **Camera toggle** (on/off)
- 🔊 **Speaker controls**
- 🚪 **Leave button**

---

## If Microphone Controls Still Missing

### Check 1: Browser Permissions

Make sure you've granted microphone permission:
```
Chrome: Settings > Privacy and security > Site settings > Microphone
```

### Check 2: LiveKit Connection

In browser console, you should see:
```
✅ LiveKit connected: {room: 'interview-...', url: '...'}
```

### Check 3: ControlBar Visibility

The ControlBar is at the bottom of the video panel. It might be styled differently in dark mode.

Try adding this to make it more visible (if needed):

```tsx
<ControlBar 
  variation="minimal"
  controls={{
    microphone: true,
    camera: true,
    screenShare: false,
    settings: true,
  }}
/>
```

---

## Restart Steps

1. **Stop the agent** (Ctrl+C)
2. **Restart the agent:**
   ```bash
   python interview_agent.py start
   ```
3. **Refresh your browser**
4. **Join a new interview session**

---

## What Changed in Code

### `interview_agent.py` - Line ~280

**Before:**
```python
await session.start(
    room=ctx.room,
    agent=agent,
    room_options=room_io.RoomOptions(
        audio_input=room_io.AudioInputOptions(
            noise_cancellation=lambda params: noise_cancellation.BVC(),
        ),
    ),
)
```

**After:**
```python
await session.start(
    room=ctx.room,
    agent=agent,
    room_options=room_io.RoomOptions(
        audio_input=room_io.AudioInputOptions(
            noise_cancellation=lambda params: noise_cancellation.BVC(),
        ),
        audio_output=False if avatar else True,  # NEW!
    ),
)
```

This ensures:
- ✅ When avatar exists: Agent doesn't publish audio (avatar does it)
- ✅ When no avatar: Agent publishes audio normally (fallback)

---

## Expected Behavior

### Room Participants

| Participant | Audio | Video | Role |
|------------|-------|-------|------|
| You | ✅ | ✅ (optional) | Candidate |
| AI Interview Coach | ✅ | ✅ | Avatar |

**Total:** 2 participants (not 3!)

### Control Bar

At the bottom of the left panel, you should see:
- Microphone icon (click to mute/unmute)
- Camera icon (click to toggle camera)
- Settings gear icon
- Leave/hang up button

---

## Troubleshooting

### Still seeing 3 participants?

**Restart both:**
```bash
# Terminal 1: Stop and restart agent
Ctrl+C
python interview_agent.py start

# Terminal 2: Refresh browser
# Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
```

### Can't hear avatar?

Check:
- Volume is up
- `RoomAudioRenderer` is present (it is, line 275)
- No browser autoplay restrictions

### Can't see controls?

The ControlBar might be styled transparently. Try hovering over the bottom of the video panel.

Or check browser console for errors.

---

## Summary

✅ **Fixed:** Agent no longer publishes audio when avatar is active
✅ **Result:** Only 2 participants (You + Avatar)
✅ **ControlBar:** Should be visible at bottom of video panel

The avatar now handles all audio/video for the AI interviewer!

