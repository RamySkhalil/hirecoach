# Transcription Display Fix

## Issue
The transcriptions from the LiveKit voice interview agent were not showing up on the frontend during the interview session.

## Root Cause
The frontend was not listening to LiveKit transcription events. The interview session page (`frontend/app/interview/session/[sessionId]/page.tsx`) was only displaying messages from:
1. Pre-loaded questions
2. Text input submissions
3. API responses

However, it was **not** listening to real-time transcriptions from the LiveKit room, so voice conversations were not being displayed.

## Additional Issue Discovered
When implementing the fix, we encountered a "text stream handler already registered" error. This was because:
- React's `useEffect` can run multiple times (especially in development with Strict Mode)
- The handler was being registered on every render
- LiveKit doesn't allow multiple handlers for the same topic

**Solutions Applied**:
1. **useRef for handler tracking**: Changed from `useState` to `useRef` so the flag persists across renders without causing re-renders
2. **Connection state check**: Added a check to prevent connecting if already connected/connecting
3. **Handler registration guard**: Only register the handler once per room instance using the ref flag

## Solution
Added a text stream handler to listen for LiveKit transcriptions using the modern `registerTextStreamHandler` API.

### Key Changes

#### Frontend (`frontend/app/interview/session/[sessionId]/page.tsx`)

1. **Added Text Stream Handler**:
   - Registered a handler for the `lk.transcription` topic
   - This receives transcriptions from both the user and the AI agent in real-time

2. **Transcription Processing**:
   - Filters to only show final transcriptions (avoids showing interim/partial results)
   - Identifies speaker based on participant identity (agent vs user)
   - Adds transcriptions to the message list with proper formatting
   - Includes duplicate detection to prevent repeated messages

3. **Code Added**:
```typescript
// Use ref to track handler registration (persists across renders)
const transcriptionHandlerRegistered = useRef(false);

// Prevent duplicate connections
const connectToLiveKit = async () => {
  if (roomInstance.state === 'connected' || roomInstance.state === 'connecting') {
    console.log('⚠️ Already connected/connecting to LiveKit, skipping...');
    return;
  }
  
  // ... connection code ...
  
  // Listen for transcription text streams (only register once per room instance)
  if (!transcriptionHandlerRegistered.current) {
    roomInstance.registerTextStreamHandler('lk.transcription', async (reader, participantInfo) => {
      try {
        const message = await reader.readAll();
        const isTranscription = reader.info.attributes?.['lk.transcribed_track_id'];
        const isFinal = reader.info.attributes?.['lk.transcription_final'] === 'true';
        
        if (isTranscription && message && message.trim().length > 0) {
          const isAgent = participantInfo.identity?.includes('agent');
          
          // Only add final transcriptions to avoid duplicates
          if (isFinal) {
            const newMessage: Message = {
              role: isAgent ? "agent" : "user",
              content: message,
              timestamp: new Date()
            };
            
            setMessages(prev => {
              // Avoid adding duplicate messages
              const isDuplicate = prev.some(m => 
                m.content === newMessage.content && 
                m.role === newMessage.role &&
                Math.abs(m.timestamp.getTime() - newMessage.timestamp.getTime()) < 1000
              );
              
              if (isDuplicate) return prev;
              return [...prev, newMessage];
            });
          }
        }
      } catch (error) {
        console.error('Error reading transcription stream:', error);
      }
    });
    transcriptionHandlerRegistered.current = true;
  }
};

// Cleanup on unmount
return () => {
  transcriptionHandlerRegistered.current = false;
  roomInstance.disconnect();
};
```

#### Backend (No changes needed)
The backend agent (`backend/livekit-voice-agent/interview_agent.py`) already:
- Uses `AgentSession` which automatically publishes transcriptions by default
- Has proper STT configured (`assemblyai/universal-streaming:en`)
- Publishes both user and agent speech to the `lk.transcription` topic

## How It Works Now

1. **User speaks** → Microphone captures audio → LiveKit processes it
2. **Agent performs STT** → Speech is transcribed
3. **Transcription published** → Sent to room via `lk.transcription` text stream
4. **Frontend receives** → Text stream handler captures the transcription
5. **UI updates** → Transcription appears in the chat interface

Same process happens for agent speech:
1. **Agent speaks** → TTS generates audio
2. **Agent publishes text** → Synchronized with audio playback
3. **Frontend receives** → Text stream handler captures it
4. **UI updates** → Agent's words appear in the chat

## Testing

To verify the fix works:

1. **Start the backend**:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

2. **Start the voice agent**:
```bash
cd backend/livekit-voice-agent
python interview_agent.py start
```

3. **Start the frontend**:
```bash
cd frontend
npm run dev
```

4. **Create and join an interview**:
   - Navigate to `http://localhost:3000/interview/setup`
   - Create a new interview session
   - Join the voice interview
   - Speak into your microphone
   - Watch the transcriptions appear in real-time in the chat panel

## Expected Behavior

✅ **User speech** should appear in the chat as blue bubbles (right side)
✅ **Agent speech** should appear in the chat as gray bubbles (left side)
✅ **Transcriptions sync in real-time** as the conversation happens
✅ **No duplicates** due to the duplicate detection logic
✅ **Only final transcriptions** are shown (no flickering interim text)

## Technical Details

### LiveKit Text Streams
LiveKit uses **text streams** (not events) for transcriptions in modern SDKs:
- Topic: `lk.transcription`
- Attributes:
  - `lk.transcribed_track_id`: ID of the audio track being transcribed
  - `lk.transcription_final`: `"true"` for final, `"false"` for interim
  - `lk.segment_id`: Unique ID for each speech segment

### Why Text Streams?
- More efficient than events
- Better for streaming data
- Supports interim and final transcripts
- Synchronized with audio playback

### Alternative: TranscriptionReceived Event
The older `RoomEvent.TranscriptionReceived` event is deprecated in newer LiveKit versions. While it may still work in some versions, the recommended approach is to use `registerTextStreamHandler`.

## References

- [LiveKit Text & Transcriptions Docs](https://docs.livekit.io/agents/build/text)
- [LiveKit Text Streams](https://docs.livekit.io/home/client/data/text-streams)
- [LiveKit Components React](https://docs.livekit.io/reference/components/react/)

## Troubleshooting

**Issue**: Error "A text stream handler for topic 'lk.transcription' has already been set"
- **Cause**: React's useEffect running multiple times (especially in dev mode with Strict Mode)
- **Solution Applied**: 
  - Changed to `useRef` instead of `useState` for handler tracking
  - Added connection state check: `if (roomInstance.state === 'connected' || roomInstance.state === 'connecting') return;`
  - Guard handler registration with `if (!transcriptionHandlerRegistered.current)`
- **Why it works**: useRef persists across renders + connection check prevents duplicate attempts + handler registration is protected

**Issue**: Transcriptions still not showing
- **Check**: Browser console for any JavaScript errors
- **Check**: Backend agent logs to confirm STT is working
- **Verify**: LiveKit connection is successful (green status in UI)
- **Verify**: Microphone permissions are granted

**Issue**: Duplicate transcriptions
- **Solution**: The duplicate detection logic should prevent this, but if you see duplicates, check the timestamp threshold (currently 1000ms)

**Issue**: Only seeing interim transcripts (flickering text)
- **Solution**: The code filters to only show final transcripts where `lk.transcription_final === 'true'`

**Issue**: Agent transcriptions show up as user (or vice versa)
- **Solution**: Check the participant identity logic - agent participants should have "agent" in their identity

---

## Summary

The fix adds real-time transcription display to the frontend by:
1. Listening to the `lk.transcription` text stream topic
2. Processing final transcriptions only
3. Identifying speaker (agent vs user)
4. Adding messages to the chat UI with duplicate prevention

This brings voice interview transcriptions to parity with text-based interviews!

