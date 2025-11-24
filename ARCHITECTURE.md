# 🏗️ Interviewly Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER BROWSER                            │
│                     http://localhost:3000                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/JSON
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      NEXT.JS FRONTEND                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Pages (App Router)                                       │   │
│  │  • / (Landing)                                           │   │
│  │  • /interview/setup (Form)                               │   │
│  │  • /interview/session/[id] (Interview Room)              │   │
│  │  • /interview/report/[id] (Results)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Components                                               │   │
│  │  • Navbar                                                │   │
│  │  • Forms, Cards, Buttons                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  API Client (lib/api.ts)                                 │   │
│  │  • startInterview()                                      │   │
│  │  • submitAnswer()                                        │   │
│  │  • finishInterview()                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ REST API
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      FASTAPI BACKEND                             │
│                    http://localhost:8000                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Routes (app/routes/)                                    │   │
│  │  • POST /interview/start                                 │   │
│  │  • POST /interview/answer                                │   │
│  │  • POST /interview/finish                                │   │
│  │  • GET  /interview/session/{id}                          │   │
│  │  • POST /media/stt                                       │   │
│  │  • POST /media/tts                                       │   │
│  └───────────────────┬──────────────────────────────────────┘   │
│                      │                                           │
│  ┌───────────────────▼──────────────────────────────────────┐   │
│  │  Services (app/services/)                                │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  LLMService                                        │  │   │
│  │  │  • generate_interview_plan()                       │  │   │
│  │  │  • evaluate_answer()                               │  │   │
│  │  │  • summarize_session()                             │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  STTService (stub)                                 │  │   │
│  │  │  • transcribe_audio()                              │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  TTSService (stub)                                 │  │   │
│  │  │  • synthesize_speech()                             │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  AvatarService (stub)                              │  │   │
│  │  │  • generate_avatar_video()                         │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └───────────────────┬──────────────────────────────────────┘   │
│                      │                                           │
│  ┌───────────────────▼──────────────────────────────────────┐   │
│  │  Database Layer (SQLAlchemy)                             │   │
│  │  • InterviewSession model                                │   │
│  │  • InterviewQuestion model                               │   │
│  │  • InterviewAnswer model                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ SQL
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    DATABASE (PostgreSQL/SQLite)                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Tables:                                                  │   │
│  │  • interview_sessions                                    │   │
│  │  • interview_questions                                   │   │
│  │  • interview_answers                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Start Interview Flow

```
User fills form
     ↓
Frontend: POST /interview/start
     ↓
Backend Routes: interview.start_interview()
     ↓
LLMService.generate_interview_plan()
     ↓
Create InterviewSession in DB
     ↓
Create InterviewQuestions in DB
     ↓
Return session_id + first_question
     ↓
Frontend: Navigate to /interview/session/{id}
```

### 2. Answer Question Flow

```
User types answer
     ↓
Frontend: POST /interview/answer
     ↓
Backend Routes: interview.submit_answer()
     ↓
Validate session and question
     ↓
LLMService.evaluate_answer()
     ↓
Create InterviewAnswer in DB with scores
     ↓
Determine next question
     ↓
Return scores + coach_notes + next_question
     ↓
Frontend: Show feedback → Next question
```

### 3. Finish Interview Flow

```
Last question answered
     ↓
Frontend: POST /interview/finish
     ↓
Backend Routes: interview.finish_interview()
     ↓
Load all questions and answers
     ↓
LLMService.summarize_session()
     ↓
Update session with summary
     ↓
Return comprehensive report
     ↓
Frontend: Navigate to /interview/report/{id}
```

## Database Schema

```
┌──────────────────────────────────────┐
│     interview_sessions               │
├──────────────────────────────────────┤
│ id (PK)              STRING(36)      │
│ user_id              STRING(36)      │ (nullable, for future)
│ job_title            STRING(255)     │
│ seniority            STRING(20)      │
│ language             STRING(10)      │
│ num_questions        INTEGER         │
│ status               STRING(20)      │
│ overall_score        INTEGER         │
│ summary_json         JSON            │
│ created_at           DATETIME        │
│ completed_at         DATETIME        │
└──────────────────────────────────────┘
           ↓
           │ 1:N
           ↓
┌──────────────────────────────────────┐
│     interview_questions              │
├──────────────────────────────────────┤
│ id (PK)              INTEGER         │
│ session_id (FK)      STRING(36)      │ → interview_sessions.id
│ idx                  INTEGER         │
│ type                 STRING(50)      │
│ competency           STRING(255)     │
│ question_text        TEXT            │
└──────────────────────────────────────┘
           ↓
           │ 1:1
           ↓
┌──────────────────────────────────────┐
│     interview_answers                │
├──────────────────────────────────────┤
│ id (PK)              INTEGER         │
│ session_id (FK)      STRING(36)      │ → interview_sessions.id
│ question_id (FK)     INTEGER         │ → interview_questions.id
│ user_answer_text     TEXT            │
│ user_answer_audio    STRING(512)     │ (nullable, future)
│ score_overall        INTEGER         │
│ score_relevance      INTEGER         │
│ score_clarity        INTEGER         │
│ score_structure      INTEGER         │
│ score_impact         INTEGER         │
│ coach_notes          TEXT            │
│ created_at           DATETIME        │
└──────────────────────────────────────┘
```

## Component Architecture

### Frontend Components

```
app/
├── layout.tsx (Root Layout)
│   └── <Navbar />
│       └── {children}
│
├── page.tsx (Landing Page)
│   ├── Hero Section
│   ├── Features Section
│   ├── How It Works Section
│   ├── CTA Section
│   └── Footer
│
└── interview/
    ├── setup/page.tsx (Setup Form)
    │   ├── Job Title Input
    │   ├── Seniority Selector
    │   ├── Language Selector
    │   ├── Questions Selector
    │   └── Submit Button
    │
    ├── session/[sessionId]/page.tsx (Interview Room)
    │   ├── Progress Bar
    │   ├── Question Display
    │   ├── Answer Textarea
    │   ├── Submit Button
    │   └── Feedback Display (conditional)
    │       ├── Score Card
    │       ├── Dimension Scores
    │       ├── Coach Notes
    │       └── Next Button
    │
    └── report/[sessionId]/page.tsx (Final Report)
        ├── Overall Score Circle
        ├── Strengths List
        ├── Weaknesses List
        ├── Action Plan
        ├── Suggested Roles
        └── Action Buttons
```

### Backend Services

```
Services Layer (Abstraction for external APIs)
├── LLMService
│   ├── generate_interview_plan()
│   │   Input: job_title, seniority, language, num_questions
│   │   Output: List[Question]
│   │   Current: Dummy implementation with templates
│   │   Future: OpenAI GPT-4 / Anthropic Claude
│   │
│   ├── evaluate_answer()
│   │   Input: question, answer, context
│   │   Output: scores + feedback
│   │   Current: Length-based scoring with random variation
│   │   Future: Real LLM evaluation
│   │
│   └── summarize_session()
│       Input: questions, answers
│       Output: overall_score, strengths, weaknesses, action_plan
│       Current: Statistics-based analysis
│       Future: LLM-generated insights
│
├── STTService
│   └── transcribe_audio()
│       Current: Returns dummy text
│       Future: Deepgram / OpenAI Whisper
│
├── TTSService
│   └── synthesize_speech()
│       Current: Returns dummy data
│       Future: ElevenLabs / Google TTS
│
└── AvatarService
    └── generate_avatar_video()
        Current: Not implemented
        Future: D-ID / HeyGen / Synthesia
```

## API Request/Response Flow

### POST /interview/start

**Request**:
```json
{
  "job_title": "Software Engineer",
  "seniority": "mid",
  "language": "en",
  "num_questions": 5
}
```

**Internal Flow**:
1. Validate request (Pydantic)
2. Create InterviewSession record
3. Call LLMService.generate_interview_plan()
4. Create InterviewQuestion records (5 questions)
5. Commit to database
6. Return first question

**Response**:
```json
{
  "session_id": "abc-123-def",
  "first_question": {
    "id": 1,
    "idx": 1,
    "type": "technical",
    "competency": "Problem Solving",
    "question_text": "Describe your experience..."
  }
}
```

### POST /interview/answer

**Request**:
```json
{
  "session_id": "abc-123-def",
  "question_id": 1,
  "user_answer_text": "I have extensive experience..."
}
```

**Internal Flow**:
1. Validate session exists and is active
2. Validate question belongs to session
3. Check answer not already submitted
4. Call LLMService.evaluate_answer()
5. Create InterviewAnswer record
6. Determine if last question
7. If not last, get next question

**Response**:
```json
{
  "score_overall": 78,
  "dimension_scores": {
    "relevance": 80,
    "clarity": 78,
    "structure": 75,
    "impact": 79
  },
  "coach_notes": "Your answer demonstrates...",
  "is_last_question": false,
  "next_question": { /* Question 2 */ }
}
```

### POST /interview/finish

**Request**:
```json
{
  "session_id": "abc-123-def"
}
```

**Internal Flow**:
1. Validate session exists
2. Check if already completed (return existing)
3. Load all questions and answers
4. Verify all answered
5. Call LLMService.summarize_session()
6. Update session: status=completed, summary_json, overall_score
7. Return summary

**Response**:
```json
{
  "session_id": "abc-123-def",
  "summary": {
    "overall_score": 78,
    "strengths": ["...", "..."],
    "weaknesses": ["...", "..."],
    "action_plan": ["...", "..."],
    "suggested_roles": ["...", "..."]
  }
}
```

## State Management

### Frontend State (React Hooks)

```typescript
// Session Page
const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
const [answer, setAnswer] = useState("");
const [feedback, setFeedback] = useState<AnswerSubmitResponse | null>(null);
const [showFeedback, setShowFeedback] = useState(false);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

// Flow
1. Load session → set currentQuestion
2. User types → update answer state
3. Submit → setLoading(true)
4. Response → setFeedback() + setShowFeedback(true)
5. Next → reset states, load next question
```

### Backend State (Database)

```
Session Lifecycle:
1. Created (status: "active")
2. Questions generated and stored
3. User answers questions → answers stored incrementally
4. All answered → status: "completed", summary stored
5. Report generated from stored data
```

## Error Handling

### Frontend
- Form validation (required fields, types)
- API error catching with user-friendly messages
- Loading states during async operations
- Disabled states to prevent double-submission
- Redirect to error pages with recovery options

### Backend
- Pydantic validation on all inputs
- HTTP exceptions with descriptive messages
- Database constraint validation
- Transaction rollback on errors
- 404 for not found, 400 for bad requests, 500 for server errors

## Security Considerations

### Current (Development)
- CORS enabled for localhost
- No authentication required
- SQLite database (file-based)
- Environment variables for config

### Future (Production)
- Restrict CORS to specific origins
- Add JWT authentication
- PostgreSQL with connection pooling
- Rate limiting
- HTTPS only
- Input sanitization
- SQL injection prevention (SQLAlchemy ORM)
- API key management for external services

## Performance Optimizations

### Frontend
- Next.js App Router (automatic code splitting)
- React Server Components where possible
- Client Components only when needed
- Framer Motion (GPU-accelerated animations)
- Lazy loading of heavy components
- Image optimization with Next.js Image

### Backend
- FastAPI async support
- Database connection pooling
- Indexed foreign keys
- Query optimization with SQLAlchemy
- Response caching (future)
- Background tasks for heavy operations (future)

## Deployment Architecture (Future)

```
┌─────────────────────────────────────┐
│           CDN (Vercel/Netlify)      │
│              Frontend               │
└──────────────┬──────────────────────┘
               │
               │ HTTPS
               │
┌──────────────▼──────────────────────┐
│        Load Balancer                │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────┐
│   Backend   │  │   Backend   │
│  Instance 1 │  │  Instance 2 │
└──────┬──────┘  └──────┬──────┘
       │                │
       └───────┬────────┘
               │
┌──────────────▼──────────────────────┐
│      PostgreSQL Database            │
│         (AWS RDS / Supabase)        │
└─────────────────────────────────────┘
```

## Monitoring & Logging (Future)

- Application logs (FastAPI + Next.js)
- Database query logs
- API response times
- Error tracking (Sentry)
- User analytics
- Performance monitoring

---

**This architecture is designed to be modular, scalable, and easy to extend!**

