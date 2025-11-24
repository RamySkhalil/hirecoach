## Overview

Interviewly (AI Interview Coach) will deliver guided mock interviews that feel conversational and insightful. The system pairs a FastAPI backend (LLM-driven interview orchestration) with a Next.js frontend (Interview workspace styled per `DESIGN-SYSTEM.md` and `COLOR-PALETTE-REFERENCE.md`). Phase 1 focuses on a text-based flow while reserving clean service boundaries for future voice/avatar upgrades.

## Goals for Phase 1

- Guided mock interview experience (setup → live session → final report).
- Configurable interview parameters: job title, seniority, language, number of questions.
- Modular FastAPI services for LLM, STT, TTS, Avatar (dummy implementations today).
- Persistent storage of sessions, questions, answers, and reports in PostgreSQL-compatible schema.
- Next.js 14 App Router UI that mirrors the provided design system and palette.
- Reliable API wiring between frontend and backend with clear error handling/loading states.

## Backend Milestones

1. **Project Skeleton**
   - FastAPI app (`app/main.py`) with routers mounted and health check.
   - Settings module with typed environment config (DB URL, service keys, frontend origin).

2. **Database Layer**
   - SQLAlchemy models for `InterviewSession`, `InterviewQuestion`, `InterviewAnswer`.
   - Session/engine helper (`app/db.py`) that supports PostgreSQL + SQLite dev default.
   - Alembic-ready metadata (future migrations).

3. **Domain Schemas & Services**
   - Pydantic schemas for requests/responses.
   - Service abstractions: `LLMService`, `STTService`, `TTSService`, `AvatarService` with mocked logic.

4. **Interview & Media Routes**
   - `/interview/start`, `/interview/answer`, `/interview/finish` orchestrating session lifecycle.
   - `/media/stt`, `/media/tts` placeholder endpoints for future integrations.
   - Dependency-injected DB sessions and services, structured error responses.

5. **Configurable Deployment**
   - `requirements.txt`, `.env.example`, and instructions for running `uvicorn app.main:app --reload`.

## Frontend Milestones

1. **Next.js App Setup**
   - App Router structure under `frontend/` with Tailwind, shared layout, and design tokens referencing the palette docs.

2. **Global UI Elements**
   - `Navbar`, typography, gradients, and button styles aligned with `DESIGN-SYSTEM.md`.

3. **Pages**
   - `/`: Marketing-style landing page with CTA.
   - `/interview/setup`: Controlled form posting to backend `/interview/start`.
   - `/interview/session/[sessionId]`: Question display, answer form, feedback placeholder.
   - `/interview/report/[sessionId]`: Summary view that calls `/interview/finish`.

4. **State & Data Fetching**
   - API client helpers that respect configurable backend base URL.
   - Loading and error states for each step.

5. **Styling System**
   - Tailwind config with custom colors if needed, reusable components (cards, buttons, badges).

## Integration Milestones

1. Define shared TypeScript/Pydantic DTO contracts for interview payloads.
2. Wire form submission to backend start endpoint and handle navigation with returned session/question.
3. Maintain per-session progress state (current index, scores) on the client.
4. Ensure finish endpoint is triggered once per session and results are cached for report display.
5. Document local run steps (backend first, then frontend) and environment variables.

## Future Phases (Implementation Status)

### ✅ Phase 3: CV Analyzer - **COMPLETE**
- ✅ Backend: PDF/DOCX/TXT parsing, AI-powered analysis, scoring endpoints
- ✅ Frontend: Beautiful upload page under `/cv` with results display
- ✅ Features: ATS scoring, strengths/weaknesses, keyword optimization
- 📄 See: `PHASE_3_4_COMPLETE_SUMMARY.md` and `QUICK_START_PHASES_3_4.md`

### ✅ Phase 4: User/Subscription & ATS Models - **COMPLETE**
- ✅ Database models: `User`, `Subscription`, `JobPosting`, `Application`
- ✅ Multi-tenant architecture ready with Clerk integration
- ⏳ Pending: User management routes, job board UI, application tracking
- 📄 See: `FUTURE_PHASES_IMPLEMENTATION.md`

### ✅ Phase 5: Avatar/TTS/STT Enhancements - **COMPLETE**
- ✅ ElevenLabs TTS integration with voice synthesis
- ✅ Deepgram STT integration with transcription
- ✅ Voice-enabled interview room with audio playback
- ✅ Interactive avatar component with animations
- 📄 See: `PHASE2_COMPLETE.md`

### ⏳ Phase 6: Analytics & Admin - **PENDING**
- Planned: Dashboard for user performance trends
- Planned: Session insights and analytics
- Planned: Subscription management dashboard
- Planned: Admin panel for system management

