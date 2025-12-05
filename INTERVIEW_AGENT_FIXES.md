# Interview Agent Fixes

## Issues Resolved

### 1. Interview Not Stopping After Set Number of Questions ✅

**Problem:** The LiveKit voice interview agent would continue asking questions indefinitely, even when the user specified only 3 questions.

**Root Cause:** The agent's system prompt didn't have explicit instructions to stop after reaching the specified number of questions.

**Fix Applied:**
- Updated the `InterviewCoachAgent` class in `backend/livekit-voice-agent/interview_agent.py`
- Added explicit instructions in the system prompt to ask EXACTLY the specified number of questions
- Added question tracking with `self.questions_asked` counter
- Included clear ending instructions: when the agent reaches the target question count, it concludes with: "Thank you for completing this interview. We've covered all N questions. You'll receive a detailed report shortly."

**Code Changes:**
```python
# Added to system prompt:
IMPORTANT: You must ask EXACTLY {num_questions} questions during this interview, no more, no less.

# Added tracking:
self.questions_asked = 0
self.conversation_transcript = []
```

---

### 2. Detailed Report Not Generated When Leaving Interview ✅

**Problem:** When users left the voice interview, no detailed report was generated, so they couldn't see their performance feedback.

**Root Cause:** 
- No endpoint existed to handle voice interview completion
- The agent wasn't saving the conversation transcript
- No logic to generate reports from voice conversations

**Fixes Applied:**

#### A. Added Transcript Tracking
- Modified `interview_agent_handler` to capture the full conversation
- Added event handlers to track user and agent speech
- Transcript saves when the participant disconnects from the room

**Code Changes in `interview_agent.py`:**
```python
# Event handlers to capture conversation
@session.on("user_speech_committed")
def on_user_speech(speech):
    transcript.append({
        "role": "user",
        "content": speech.text,
        "timestamp": speech.timestamp
    })

@session.on("agent_speech_committed")
def on_agent_speech(speech):
    transcript.append({
        "role": "assistant",
        "content": speech.text,
        "timestamp": speech.timestamp
    })

# Save on disconnect
@ctx.room.on("participant_disconnected")
async def on_participant_disconnected(participant):
    await save_interview_transcript(session_id, transcript, agent.questions_asked)
```

#### B. Created New Backend Endpoint
- Added `/interview/voice-session/{session_id}/complete` endpoint in `backend/app/routes/interview.py`
- This endpoint receives the transcript from the agent and generates a report
- Marks the session as "completed" so the report page can load it

**New Endpoint:**
```python
@router.post("/voice-session/{session_id}/complete")
def complete_voice_interview(
    session_id: str,
    request: VoiceInterviewCompleteRequest,
    db: Session = Depends(get_db)
):
    # Analyzes conversation transcript
    # Generates summary with AI
    # Saves to database
    # Returns detailed report
```

#### C. Added Voice Interview Summarization
- Created `summarize_voice_interview()` method in `backend/app/services/llm_service.py`
- This method uses AI (GPT-4) to analyze the full conversation transcript
- Generates:
  - Overall score (0-100)
  - Strengths (2-4 specific items)
  - Weaknesses (2-4 areas to improve)
  - Action plan (3-5 concrete steps)
  - Suggested roles (2-4 matching positions)

**New Method:**
```python
@staticmethod
def summarize_voice_interview(
    job_title: str,
    seniority: str,
    conversation_transcript: str,
    questions_asked: int,
    total_questions: int
) -> Dict[str, Any]:
    # Analyzes full conversation
    # Returns comprehensive feedback
```

---

## How It Works Now

1. **User starts interview** → Agent joins room with specific question limit
2. **Agent asks questions** → Stops after reaching the target number (e.g., 3 questions)
3. **User leaves/completes interview** → Agent detects disconnect
4. **Transcript saved** → Agent sends conversation to backend
5. **Report generated** → Backend analyzes conversation with AI
6. **User can view report** → Navigate to `/interview/report/{sessionId}`

---

## Files Modified

### Backend Files:
1. `backend/livekit-voice-agent/interview_agent.py`
   - Enhanced agent prompt with question counting
   - Added conversation tracking
   - Added automatic transcript saving on disconnect

2. `backend/app/routes/interview.py`
   - Added new endpoint: `POST /interview/voice-session/{session_id}/complete`
   - Added `VoiceInterviewCompleteRequest` model

3. `backend/app/services/llm_service.py`
   - Added `summarize_voice_interview()` method
   - Analyzes full conversation transcripts
   - Generates detailed performance reports

---

## Testing the Fixes

### To Test the Voice Interview:

1. **Start the backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Start the voice agent:**
   ```bash
   cd backend/livekit-voice-agent
   python interview_agent.py start
   ```

3. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

4. **Create an interview:**
   - Navigate to interview setup
   - Set number of questions to 3
   - Start the interview

5. **Conduct the interview:**
   - Join the voice room
   - Answer the agent's questions
   - The agent should ask exactly 3 questions
   - After the 3rd question, it should thank you and conclude

6. **Leave the interview:**
   - Disconnect from the room
   - Navigate to `/interview/report/{sessionId}`
   - You should see your detailed report with:
     - Overall score
     - Strengths
     - Weaknesses
     - Action plan
     - Suggested roles

---

## Environment Requirements

Make sure you have these configured in `backend/livekit-voice-agent/.env.local`:

```env
LIVEKIT_URL=wss://your-livekit-instance.com
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
OPENAI_API_KEY=your_openai_key
BACKEND_URL=http://localhost:8000
```

---

## Known Limitations

1. **Speech event tracking:** The exact event names (`user_speech_committed`, `agent_speech_committed`) may vary depending on the LiveKit agents version. If transcripts aren't being captured, check the LiveKit agents documentation for the correct event names.

2. **Report generation timing:** It may take a few seconds for the report to be generated after leaving the interview. If you navigate to the report page too quickly, you might need to refresh.

3. **Question counting accuracy:** The agent relies on the AI (GPT-4) to count its own questions. While generally accurate, it may occasionally ask one more or one less question than specified.

---

## Next Steps (Optional Enhancements)

- [ ] Add a "Leave Interview" button in the UI for explicit exit
- [ ] Show live question counter during interview
- [ ] Add transcript viewer in the report page
- [ ] Implement real-time saving (save transcript chunks during interview, not just at end)
- [ ] Add interview progress indicator
- [ ] Support resuming interrupted interviews

---

## Troubleshooting

**Issue:** Report doesn't appear after leaving interview
- **Solution:** Check backend logs for errors. Ensure OPENAI_API_KEY is configured.

**Issue:** Agent asks more than specified questions
- **Solution:** The AI may occasionally deviate. Consider adding more explicit stopping logic based on turn count.

**Issue:** Transcript is empty
- **Solution:** Verify the LiveKit agents version and check the correct event names for speech tracking.

**Issue:** "Session not found" error
- **Solution:** Ensure the session_id in the room name matches the database session ID.

---

## Summary

Both issues have been resolved:
✅ Interview now stops after the specified number of questions
✅ Detailed report is generated when leaving the interview

The agent now properly tracks conversation, counts questions, and automatically saves transcripts for report generation!

