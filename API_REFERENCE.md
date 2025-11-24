# 📡 Interviewly API Reference

Complete reference for all backend API endpoints.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation.

---

## Health Check Endpoints

### GET `/`

Health check endpoint.

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "app_name": "Interviewly",
  "timestamp": "2024-11-16T12:00:00.000Z"
}
```

### GET `/health`

Alternative health check endpoint.

**Response**: Same as GET `/`

---

## Interview Endpoints

### POST `/interview/start`

Start a new interview session. Creates a session, generates questions using LLM service, and returns the first question.

**Request Body**:
```json
{
  "job_title": "Software Engineer",
  "seniority": "mid",
  "language": "en",
  "num_questions": 5
}
```

**Parameters**:
- `job_title` (string, required): Job title/role for interview (1-255 chars)
- `seniority` (string, required): One of: `"junior"`, `"mid"`, `"senior"`
- `language` (string, required): One of: `"en"`, `"ar"`
- `num_questions` (integer, required): Number of questions (1-20)

**Response**: `200 OK`
```json
{
  "session_id": "abc-123-def-456",
  "first_question": {
    "id": 1,
    "idx": 1,
    "type": "technical",
    "competency": "Problem Solving",
    "question_text": "Describe your experience with key technologies used in Software Engineer roles."
  }
}
```

**Error Responses**:
- `422 Unprocessable Entity`: Validation error (invalid parameters)

**Example curl**:
```bash
curl -X POST http://localhost:8000/interview/start \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Data Scientist",
    "seniority": "senior",
    "language": "en",
    "num_questions": 3
  }'
```

---

### POST `/interview/answer`

Submit an answer to a question. Evaluates the answer, stores it, and returns feedback with the next question.

**Request Body**:
```json
{
  "session_id": "abc-123-def-456",
  "question_id": 1,
  "user_answer_text": "I have extensive experience with Python, JavaScript, and SQL. In my current role, I've built several REST APIs using FastAPI and created data pipelines for processing millions of records. I focus on writing clean, maintainable code and following best practices."
}
```

**Parameters**:
- `session_id` (string, required): Session ID from `/interview/start`
- `question_id` (integer, required): Question ID to answer
- `user_answer_text` (string, required): User's answer (min 1 char)

**Response**: `200 OK`
```json
{
  "score_overall": 78,
  "dimension_scores": {
    "relevance": 80,
    "clarity": 78,
    "structure": 75,
    "impact": 79
  },
  "coach_notes": "Your technical explanation shows good understanding. Consider adding more specific examples or metrics to strengthen your answer.",
  "is_last_question": false,
  "next_question": {
    "id": 2,
    "idx": 2,
    "type": "behavioral",
    "competency": "Teamwork",
    "question_text": "Tell me about a time when you had to work under pressure. How did you handle it?"
  }
}
```

**Response Fields**:
- `score_overall` (integer): Overall score 0-100
- `dimension_scores` (object): Breakdown by dimension
  - `relevance` (integer): How relevant the answer is (0-100)
  - `clarity` (integer): How clear the answer is (0-100)
  - `structure` (integer): How well-structured (0-100)
  - `impact` (integer): Impact/results shown (0-100)
- `coach_notes` (string): AI-generated feedback
- `is_last_question` (boolean): Whether this was the last question
- `next_question` (object|null): Next question or null if last

**Error Responses**:
- `404 Not Found`: Session or question not found
- `400 Bad Request`: Session not active or answer already submitted
- `422 Unprocessable Entity`: Validation error

**Example curl**:
```bash
curl -X POST http://localhost:8000/interview/answer \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123-def-456",
    "question_id": 1,
    "user_answer_text": "I have 5 years of experience..."
  }'
```

---

### POST `/interview/finish`

Finish an interview session and generate comprehensive report. Must answer all questions first.

**Request Body**:
```json
{
  "session_id": "abc-123-def-456"
}
```

**Parameters**:
- `session_id` (string, required): Session ID to finish

**Response**: `200 OK`
```json
{
  "session_id": "abc-123-def-456",
  "summary": {
    "overall_score": 78,
    "strengths": [
      "Strong relevance - you consistently provided on-topic, applicable answers",
      "Excellent communication - your answers were clear and easy to follow",
      "Well-structured responses - you organized your thoughts logically"
    ],
    "weaknesses": [
      "Demonstrating impact - include more specific metrics and measurable outcomes"
    ],
    "action_plan": [
      "Deepen your technical knowledge in key Software Engineer areas",
      "Prepare more quantifiable examples of your achievements",
      "Practice articulating complex ideas more concisely"
    ],
    "suggested_roles": [
      "Mid Software Engineer",
      "Software Engineer - smaller companies or startups"
    ]
  }
}
```

**Response Fields**:
- `session_id` (string): The session ID
- `summary` (object): Comprehensive report
  - `overall_score` (integer): Average of all question scores (0-100)
  - `strengths` (array of strings): List of identified strengths
  - `weaknesses` (array of strings): Areas for improvement
  - `action_plan` (array of strings): Concrete steps to improve
  - `suggested_roles` (array of strings): Recommended job titles/levels

**Error Responses**:
- `404 Not Found`: Session not found
- `400 Bad Request`: Not all questions answered yet
- `422 Unprocessable Entity`: Validation error

**Example curl**:
```bash
curl -X POST http://localhost:8000/interview/finish \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123-def-456"
  }'
```

---

### GET `/interview/session/{session_id}`

Get detailed information about an interview session.

**Path Parameters**:
- `session_id` (string): Session ID

**Response**: `200 OK`
```json
{
  "session_id": "abc-123-def-456",
  "job_title": "Software Engineer",
  "seniority": "mid",
  "language": "en",
  "status": "active",
  "num_questions": 5,
  "questions": [
    {
      "id": 1,
      "idx": 1,
      "type": "technical",
      "competency": "Problem Solving",
      "question_text": "Describe your experience..."
    },
    // ... more questions
  ],
  "answers_count": 2,
  "overall_score": null,
  "summary": null
}
```

**Response Fields**:
- `session_id` (string): Session ID
- `job_title` (string): Job title for interview
- `seniority` (string): Seniority level
- `language` (string): Interview language
- `status` (string): "active" or "completed"
- `num_questions` (integer): Total questions in session
- `questions` (array): All questions in session
- `answers_count` (integer): Number of answers submitted
- `overall_score` (integer|null): Final score (null if not completed)
- `summary` (object|null): Summary report (null if not completed)

**Error Responses**:
- `404 Not Found`: Session not found

**Example curl**:
```bash
curl http://localhost:8000/interview/session/abc-123-def-456
```

---

## Media Endpoints

### POST `/media/stt`

Convert speech audio to text (Speech-to-Text). Currently returns dummy text.

**Request**: `multipart/form-data`
- `audio` (file): Audio file (any audio format)

**Response**: `200 OK`
```json
{
  "text": "This is a dummy transcription. Real STT integration coming soon."
}
```

**Error Responses**:
- `400 Bad Request`: Invalid audio file type
- `500 Internal Server Error`: STT processing error

**Example curl**:
```bash
curl -X POST http://localhost:8000/media/stt \
  -F "audio=@recording.wav"
```

**Future Integration**: Will use Deepgram, OpenAI Whisper, or similar.

---

### POST `/media/tts`

Convert text to speech audio (Text-to-Speech). Currently returns dummy data.

**Request Body**:
```json
{
  "text": "Hello, welcome to your interview!"
}
```

**Parameters**:
- `text` (string, required): Text to synthesize (min 1 char)

**Response**: `200 OK`
```json
{
  "audio_url": null,
  "audio_bytes_length": 3200
}
```

**Response Fields**:
- `audio_url` (string|null): URL to audio file (null in dummy mode)
- `audio_bytes_length` (integer): Length of audio data in bytes

**Error Responses**:
- `400 Bad Request`: Text is empty
- `500 Internal Server Error`: TTS processing error

**Example curl**:
```bash
curl -X POST http://localhost:8000/media/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a test."
  }'
```

**Future Integration**: Will use ElevenLabs, Google TTS, or similar.

---

## Data Models

### InterviewSession

Database model representing an interview session.

**Fields**:
- `id` (string): UUID, primary key
- `user_id` (string|null): User ID (for future auth)
- `job_title` (string): Job title
- `seniority` (string): junior/mid/senior
- `language` (string): en/ar
- `num_questions` (integer): Number of questions
- `status` (string): active/completed
- `overall_score` (integer|null): Final score (0-100)
- `summary_json` (object|null): Summary report
- `created_at` (datetime): Creation timestamp
- `completed_at` (datetime|null): Completion timestamp

### InterviewQuestion

Database model for interview questions.

**Fields**:
- `id` (integer): Auto-increment primary key
- `session_id` (string): Foreign key to InterviewSession
- `idx` (integer): 1-based question index
- `type` (string): technical/behavioral/situational/general
- `competency` (string|null): Competency being tested
- `question_text` (text): The question

### InterviewAnswer

Database model for user answers.

**Fields**:
- `id` (integer): Auto-increment primary key
- `session_id` (string): Foreign key to InterviewSession
- `question_id` (integer): Foreign key to InterviewQuestion
- `user_answer_text` (text): User's answer
- `user_answer_audio` (string|null): Audio URL (future)
- `score_overall` (integer): Overall score (0-100)
- `score_relevance` (integer): Relevance score (0-100)
- `score_clarity` (integer): Clarity score (0-100)
- `score_structure` (integer): Structure score (0-100)
- `score_impact` (integer): Impact score (0-100)
- `coach_notes` (text): AI feedback
- `created_at` (datetime): Creation timestamp

---

## Question Types

### Technical
Tests technical knowledge and skills.

**Example**: "Describe your experience with key technologies used in this role."

### Behavioral
Tests soft skills through past behavior.

**Example**: "Tell me about a time when you had to work under pressure."

### Situational
Tests problem-solving in hypothetical scenarios.

**Example**: "If you joined our team, what would be your priorities in the first 90 days?"

### General
Tests career goals, motivations, and self-awareness.

**Example**: "Why are you interested in this position?"

---

## Scoring System

### Overall Score (0-100)
Average of four dimension scores.

### Dimension Scores (0-100 each)

**Relevance**
- Is the answer on-topic?
- Does it address the question?
- Is it applicable to the role?

**Clarity**
- Is the answer clear and easy to understand?
- Is the language appropriate?
- Is it well-articulated?

**Structure**
- Is the answer well-organized?
- Does it follow a logical flow?
- Does it use frameworks (e.g., STAR method)?

**Impact**
- Does it show results or outcomes?
- Are there specific examples?
- Are there metrics or measurable achievements?

### Score Ranges
- **80-100**: Excellent
- **70-79**: Good
- **60-69**: Fair
- **0-59**: Needs Improvement

---

## Error Codes

### 200 OK
Request successful.

### 400 Bad Request
Invalid request (e.g., already submitted, not all questions answered).

### 404 Not Found
Resource not found (e.g., invalid session_id, question_id).

### 422 Unprocessable Entity
Validation error (e.g., invalid parameters, missing required fields).

### 500 Internal Server Error
Server error (e.g., database error, service failure).

---

## Rate Limiting (Future)

Not currently implemented. Future plans:
- 10 requests per minute per IP
- 100 sessions per day per IP
- Configurable limits for authenticated users

---

## Authentication (Future)

Not currently implemented. Future plans:
- JWT-based authentication
- User registration and login
- API key for external integrations
- OAuth support (Google, LinkedIn)

---

## Best Practices

### Starting an Interview
1. Validate all input fields client-side first
2. Store `session_id` securely (localStorage/sessionStorage)
3. Handle errors gracefully with user-friendly messages
4. Show loading states during API calls

### Submitting Answers
1. Validate answer is not empty
2. Include session_id and question_id
3. Wait for response before allowing next submission
4. Store feedback for review later

### Finishing Interview
1. Ensure all questions are answered
2. Handle case where session is already completed
3. Display comprehensive report
4. Provide options to start new interview or go home

### Error Handling
1. Always check response status codes
2. Parse error messages from `detail` field
3. Provide recovery options (retry, go back, start over)
4. Log errors for debugging

---

## Examples

### Complete Interview Flow

**1. Start Interview**
```bash
curl -X POST http://localhost:8000/interview/start \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Product Manager",
    "seniority": "senior",
    "language": "en",
    "num_questions": 3
  }'
```

**2. Answer Question 1**
```bash
curl -X POST http://localhost:8000/interview/answer \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID_FROM_STEP_1",
    "question_id": 1,
    "user_answer_text": "As a Product Manager with 8 years of experience..."
  }'
```

**3. Answer Question 2**
```bash
curl -X POST http://localhost:8000/interview/answer \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID_FROM_STEP_1",
    "question_id": 2,
    "user_answer_text": "I prioritize user needs through research and data..."
  }'
```

**4. Answer Question 3**
```bash
curl -X POST http://localhost:8000/interview/answer \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID_FROM_STEP_1",
    "question_id": 3,
    "user_answer_text": "I led the launch of a new feature that increased engagement..."
  }'
```

**5. Finish Interview**
```bash
curl -X POST http://localhost:8000/interview/finish \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID_FROM_STEP_1"
  }'
```

---

## Support

For API issues:
- Check interactive docs: http://localhost:8000/docs
- Review this reference
- Check backend logs
- Verify database state

---

**Last Updated**: 2024-11-16
**API Version**: 1.0.0

