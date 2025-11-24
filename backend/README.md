# Interviewly Backend

FastAPI backend for the Interviewly AI Interview Coach platform.

## Features

- **Interview Session Management**: Create and manage mock interview sessions
- **AI Question Generation**: Generate interview questions based on job role and seniority
- **Answer Evaluation**: Evaluate answers with detailed scoring and feedback
- **Session Summarization**: Comprehensive interview reports with strengths, weaknesses, and action plans
- **Media Services**: STT/TTS endpoints (ready for integration)

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (SQLite for development)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration and settings
│   ├── db.py                # Database setup and session management
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── interview.py     # Interview endpoints
│   │   └── media.py         # STT/TTS endpoints
│   └── services/
│       ├── __init__.py
│       ├── llm_service.py   # LLM abstraction (currently dummy)
│       ├── stt_service.py   # Speech-to-Text service
│       ├── tts_service.py   # Text-to-Speech service
│       └── avatar_service.py # Avatar service (placeholder)
├── requirements.txt
└── env.example
```

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file (or copy from `env.example`):

```bash
# Windows
copy env.example .env

# Mac/Linux
cp env.example .env
```

Edit `.env` with your configuration:

```env
DATABASE_URL=sqlite:///./interviewly.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/interviewly

OPENAI_API_KEY=your_key_here
DEBUG=True
```

### 4. Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Or using Python
python -m app.main
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

- `GET /` - Health check
- `GET /health` - Alternative health check

### Interview Endpoints

- `POST /interview/start` - Start a new interview session
- `POST /interview/answer` - Submit an answer
- `POST /interview/finish` - Finish interview and get report
- `GET /interview/session/{session_id}` - Get session details

### Media Endpoints

- `POST /media/stt` - Speech-to-Text (audio to text)
- `POST /media/tts` - Text-to-Speech (text to audio)

## Example API Usage

### Start Interview

```bash
curl -X POST "http://localhost:8000/interview/start" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Software Engineer",
    "seniority": "mid",
    "language": "en",
    "num_questions": 5
  }'
```

Response:
```json
{
  "session_id": "abc-123-def",
  "first_question": {
    "id": 1,
    "idx": 1,
    "type": "technical",
    "competency": "Problem Solving",
    "question_text": "Describe your experience with key technologies..."
  }
}
```

### Submit Answer

```bash
curl -X POST "http://localhost:8000/interview/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123-def",
    "question_id": 1,
    "user_answer_text": "I have extensive experience with Python..."
  }'
```

### Finish Interview

```bash
curl -X POST "http://localhost:8000/interview/finish" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123-def"
  }'
```

## Database Models

### InterviewSession
- Stores interview configuration and results
- Fields: id, job_title, seniority, language, num_questions, status, overall_score, summary_json

### InterviewQuestion
- Individual questions in a session
- Fields: id, session_id, idx, type, competency, question_text

### InterviewAnswer
- User answers with evaluation scores
- Fields: id, session_id, question_id, user_answer_text, scores (overall, relevance, clarity, structure, impact), coach_notes

## Service Architecture

The backend uses a service layer pattern for external integrations:

- **LLMService**: Handles question generation, answer evaluation, and summarization
- **STTService**: Speech-to-Text conversion (ready for Deepgram/Whisper integration)
- **TTSService**: Text-to-Speech synthesis (ready for ElevenLabs/Google TTS integration)
- **AvatarService**: Avatar video generation (placeholder for D-ID/Synthesia integration)

Currently, services use dummy implementations for testing. Replace with real API calls when ready.

## Development

### Database Migrations

The application uses SQLAlchemy with automatic table creation on startup. For production, consider using Alembic for proper migrations.

### Adding New Endpoints

1. Create/update route file in `app/routes/`
2. Define Pydantic schemas in `app/schemas.py`
3. Include router in `app/main.py`

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when implemented)
pytest
```

## Production Deployment

1. **Set up PostgreSQL database**
2. **Update DATABASE_URL** in environment
3. **Add API keys** for LLM, STT, TTS services
4. **Configure CORS** origins in `main.py`
5. **Use production ASGI server**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`

## Future Enhancements

- [ ] Real LLM integration (OpenAI, Anthropic)
- [ ] Speech-to-Text integration (Deepgram, Whisper)
- [ ] Text-to-Speech integration (ElevenLabs)
- [ ] AI Avatar integration (D-ID, HeyGen)
- [ ] User authentication and authorization
- [ ] CV/Resume analysis
- [ ] ATS integration
- [ ] Video recording and analysis
- [ ] Advanced analytics and insights

## License

Proprietary - All rights reserved

