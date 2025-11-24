# 🧪 Testing Guide for Interviewly

This guide helps you verify that all components of Interviewly are working correctly.

## Pre-Testing Checklist

- [ ] Backend is running on http://localhost:8000
- [ ] Frontend is running on http://localhost:3000
- [ ] No error messages in backend terminal
- [ ] No error messages in frontend terminal

## Backend API Tests

### Test 1: Health Check

**Endpoint**: `GET http://localhost:8000/`

**Expected Response**:
```json
{
  "status": "healthy",
  "app_name": "Interviewly",
  "timestamp": "2024-11-16T..."
}
```

**Test in Browser**: Visit http://localhost:8000

**Test with curl**:
```bash
curl http://localhost:8000/
```

### Test 2: API Documentation

**Test**: Visit http://localhost:8000/docs

**Expected**: 
- Swagger UI loads
- All endpoints visible:
  - GET /
  - GET /health
  - POST /interview/start
  - POST /interview/answer
  - POST /interview/finish
  - GET /interview/session/{session_id}
  - POST /media/stt
  - POST /media/tts

### Test 3: Start Interview

**Endpoint**: `POST http://localhost:8000/interview/start`

**Request**:
```json
{
  "job_title": "Software Engineer",
  "seniority": "mid",
  "language": "en",
  "num_questions": 3
}
```

**Expected Response**:
```json
{
  "session_id": "abc-123-def...",
  "first_question": {
    "id": 1,
    "idx": 1,
    "type": "technical",
    "competency": "Problem Solving",
    "question_text": "Describe your experience with..."
  }
}
```

**Test in Swagger UI**:
1. Click on `POST /interview/start`
2. Click "Try it out"
3. Paste the request JSON
4. Click "Execute"
5. Verify response is 200 with correct structure

### Test 4: Submit Answer

**Endpoint**: `POST http://localhost:8000/interview/answer`

**Request** (use session_id and question_id from Test 3):
```json
{
  "session_id": "YOUR_SESSION_ID",
  "question_id": 1,
  "user_answer_text": "I have extensive experience with Python and JavaScript. In my previous role, I worked on building scalable web applications using FastAPI and React. I've also led a team of developers in implementing best practices and design patterns."
}
```

**Expected Response**:
```json
{
  "score_overall": 75,
  "dimension_scores": {
    "relevance": 80,
    "clarity": 75,
    "structure": 70,
    "impact": 75
  },
  "coach_notes": "Your answer demonstrates...",
  "is_last_question": false,
  "next_question": {
    "id": 2,
    "idx": 2,
    "type": "behavioral",
    "competency": "Teamwork",
    "question_text": "Tell me about a time..."
  }
}
```

### Test 5: Finish Interview

**Endpoint**: `POST http://localhost:8000/interview/finish`

**Note**: Answer all questions first (Test 4 for each question)

**Request**:
```json
{
  "session_id": "YOUR_SESSION_ID"
}
```

**Expected Response**:
```json
{
  "session_id": "YOUR_SESSION_ID",
  "summary": {
    "overall_score": 78,
    "strengths": [
      "Strong relevance - you consistently provided on-topic answers",
      "Excellent communication - clear and easy to follow"
    ],
    "weaknesses": [
      "Minor: Could provide even more specific examples"
    ],
    "action_plan": [
      "Deepen your technical knowledge in key areas",
      "Prepare more quantifiable examples of achievements"
    ],
    "suggested_roles": [
      "Mid Software Engineer",
      "Software Engineer - smaller companies or startups"
    ]
  }
}
```

### Test 6: Get Session

**Endpoint**: `GET http://localhost:8000/interview/session/{session_id}`

**Expected Response**: Full session details with questions and answers count

## Frontend Tests

### Test 1: Landing Page

**URL**: http://localhost:3000

**Verify**:
- [ ] Page loads without errors
- [ ] Navbar is visible with logo and "Start Interview" button
- [ ] Hero section with headline "Ace Your Next Job Interview"
- [ ] Blue/indigo gradient styling
- [ ] Three feature cards visible
- [ ] "How It Works" section with 3 steps
- [ ] CTA section at bottom
- [ ] Footer with Interviewly branding
- [ ] Smooth animations on scroll
- [ ] All buttons are clickable

### Test 2: Setup Page

**URL**: http://localhost:3000/interview/setup

**Verify**:
- [ ] Page loads without errors
- [ ] Form displays with all fields:
  - Job Title input field
  - Seniority buttons (Junior, Mid, Senior)
  - Language buttons (English, Arabic)
  - Number of questions dropdown
- [ ] Selected button has gradient background
- [ ] Submit button is disabled when job title is empty
- [ ] Submit button shows loading state when clicked
- [ ] Info cards at bottom display correctly

**Test Flow**:
1. Enter "Product Manager" in job title
2. Select "Senior" seniority
3. Select "English" language
4. Choose "5 Questions"
5. Click "Start Interview"
6. Should redirect to `/interview/session/[sessionId]`

### Test 3: Interview Session Page

**URL**: http://localhost:3000/interview/session/[sessionId]
(Will be redirected here from setup)

**Verify**:
- [ ] Progress bar shows "Question 1 of 5"
- [ ] Current question displays with type and competency
- [ ] Large textarea for answer input
- [ ] Submit button is disabled when answer is empty
- [ ] Submit button shows loading state
- [ ] After submitting:
  - Score card appears with overall score
  - Dimension scores (relevance, clarity, structure, impact) displayed
  - Coach notes visible
  - "Next Question" or "View Final Report" button appears
- [ ] Clicking next loads the next question
- [ ] Progress bar updates correctly

**Test Flow**:
1. Read question 1
2. Type a detailed answer (100+ words)
3. Click "Submit Answer"
4. Wait for feedback
5. Review score and coach notes
6. Click "Next Question"
7. Repeat for all questions
8. On last question, click "View Final Report"

### Test 4: Report Page

**URL**: http://localhost:3000/interview/report/[sessionId]
(Will be redirected here after last question)

**Verify**:
- [ ] Loading state appears briefly
- [ ] Report page loads with all sections:
  - Overall score with circular progress
  - Score label (Excellent/Good/Fair/Needs Improvement)
  - Strengths section with checkmarks
  - Weaknesses/Areas for Improvement section
  - Action Plan with numbered items
  - Recommended Roles as badges
  - "Start New Interview" and "Back to Home" buttons
- [ ] All animations play smoothly
- [ ] Buttons work correctly

**Test Flow**:
1. Review all sections of the report
2. Click "Start New Interview" → redirects to setup
3. Click "Back to Home" → redirects to landing page

## Integration Tests

### Full User Journey Test

**Test the complete flow from start to finish:**

1. **Landing Page**
   - Open http://localhost:3000
   - Click "Start Mock Interview" in hero section
   - Should navigate to /interview/setup

2. **Setup**
   - Fill in form: "Data Scientist", "Mid", "English", "3 Questions"
   - Click "Start Interview"
   - Should create session and navigate to session page

3. **Question 1**
   - Read question
   - Type answer: "I have 5 years of experience in data science, working primarily with Python, scikit-learn, and TensorFlow. I've built predictive models for customer churn, implemented A/B testing frameworks, and created data pipelines for real-time analytics."
   - Submit answer
   - Verify score appears (should be 70-85)
   - Click "Next Question"

4. **Question 2**
   - Read question
   - Type answer: "When faced with a challenging problem, I start by breaking it down into smaller components. For example, when tasked with reducing model latency by 50%, I profiled the code, identified bottlenecks, optimized data loading, and implemented caching strategies. This reduced latency by 60%."
   - Submit answer
   - Verify score appears
   - Click "Next Question"

5. **Question 3**
   - Read question
   - Type answer: "I stay updated by reading research papers on arXiv, following ML blogs like Distill and TowardsDataScience, attending conferences like NeurIPS, and experimenting with new techniques in personal projects. I also contribute to open-source ML libraries."
   - Submit answer
   - Verify score appears
   - Click "View Final Report"

6. **Report**
   - Verify overall score is calculated (average of 3 scores)
   - Verify strengths listed
   - Verify weaknesses listed
   - Verify action plan provided
   - Verify suggested roles displayed
   - Click "Start New Interview" to test loop

### Multiple Session Test

**Test creating multiple interviews:**

1. Create first interview session (follow setup)
2. Complete all questions
3. View report
4. Click "Start New Interview"
5. Create second interview with different parameters
6. Verify each session has unique ID
7. Verify sessions don't interfere with each other

## Error Handling Tests

### Backend Error Tests

**Test 1: Submit answer for non-existent session**
```json
{
  "session_id": "invalid-id",
  "question_id": 1,
  "user_answer_text": "Test"
}
```
**Expected**: 404 error with message "Interview session not found"

**Test 2: Submit answer twice for same question**
- Submit answer for question 1
- Try to submit again for same question
**Expected**: 400 error "Answer already submitted for this question"

**Test 3: Finish interview before answering all questions**
- Start session with 5 questions
- Answer only 2 questions
- Try to finish
**Expected**: 400 error with message about unanswered questions

### Frontend Error Tests

**Test 1: Invalid session ID**
- Navigate to http://localhost:3000/interview/session/invalid-id
**Expected**: Error message with "Back to Setup" button

**Test 2: Empty form submission**
- Go to setup page
- Leave job title empty
- Try to submit
**Expected**: Submit button should be disabled

**Test 3: Backend not running**
- Stop backend server
- Try to start interview from frontend
**Expected**: Error message "Failed to start interview"

## Performance Tests

### Backend Performance

**Test**: Create 10 sessions rapidly

```bash
# Use this bash script or similar
for i in {1..10}
do
  curl -X POST http://localhost:8000/interview/start \
    -H "Content-Type: application/json" \
    -d '{"job_title":"Engineer","seniority":"mid","language":"en","num_questions":5}'
done
```

**Expected**: All requests complete successfully in < 5 seconds total

### Frontend Performance

**Test**: Open Chrome DevTools → Lighthouse
- Run audit on landing page
**Expected**: Performance score > 90

## Browser Compatibility Tests

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

Verify all features work on each browser.

## Mobile Responsiveness Tests

**Test on different viewport sizes:**
- [ ] Mobile (375px width)
- [ ] Tablet (768px width)
- [ ] Desktop (1280px width)

**Verify**:
- Layout adjusts properly
- Text is readable
- Buttons are tappable
- No horizontal scroll
- Navigation works

## Database Tests

### SQLite Tests

**View database**:
```bash
cd backend
sqlite3 interviewly.db

-- Check tables exist
.tables

-- View sessions
SELECT * FROM interview_sessions;

-- View questions
SELECT * FROM interview_questions;

-- View answers
SELECT * FROM interview_answers;

-- Exit
.quit
```

**Expected**: Tables exist and data is stored correctly

## Common Issues and Solutions

### Issue: "Module not found" in backend
**Solution**: 
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: Frontend won't connect to backend
**Solution**:
- Check backend is running: http://localhost:8000
- Check `.env.local` has correct URL
- Check browser console for CORS errors

### Issue: Database locked
**Solution**:
- Close all connections to database
- Delete `backend/interviewly.db`
- Restart backend (will recreate DB)

### Issue: Scores seem random
**Solution**: This is expected! The dummy LLM service generates semi-random scores for testing. Real LLM integration will provide accurate evaluation.

## Test Report Template

Use this template to document your test results:

```
## Test Session Report

**Date**: [Date]
**Tester**: [Name]
**Environment**: Windows/Mac/Linux

### Backend Tests
- [ ] Health check: PASS/FAIL
- [ ] API docs: PASS/FAIL
- [ ] Start interview: PASS/FAIL
- [ ] Submit answer: PASS/FAIL
- [ ] Finish interview: PASS/FAIL

### Frontend Tests
- [ ] Landing page: PASS/FAIL
- [ ] Setup page: PASS/FAIL
- [ ] Session page: PASS/FAIL
- [ ] Report page: PASS/FAIL

### Integration Tests
- [ ] Full user journey: PASS/FAIL
- [ ] Multiple sessions: PASS/FAIL

### Notes
[Any issues or observations]
```

---

**All tests passing? You're ready to start building on Interviewly! 🎉**

