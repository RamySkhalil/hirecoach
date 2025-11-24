⭐ IMPLEMENTATION STATUS: PHASE 1 (MVP) - PILLAR 1 ONLY

**Current Focus:** AI Interview Coaching (PILLAR 1)
- ✅ Landing page → Interview Setup → Interview Session → Report flow
- ✅ Backend: `/interview/start`, `/interview/answer`, `/interview/finish`
- ✅ Frontend: All core interview pages implemented
- ✅ PILLAR 2: CV tools (Analyzer & Rewriter) - Fully Implemented & Featured
- ✅ PILLAR 3: Career Agent - Fully Implemented & Featured
- ⏳ PILLAR 4-5: Job Tracker, Cover Letter Generator exist but are NOT the MVP focus

**What this means:**
The app emphasizes four core AI tools: Interview Coach, CV Analyzer, CV Rewriter, and Career Agent. Other features are planned for future phases.

---

⭐ 1) CORE USER JOURNEY (End-to-End)

This is the exact path a new user takes from landing to becoming a paying customer.

STEP 1 — Landing Page → Awareness

User discovers the app through:

Google search

TikTok/Instagram ad

LinkedIn post

Referral

User action:
They click “Start Interview” or “Try Free”.

Goal: Convert curiosity → trial.

STEP 2 — Setup Interview

They land on a simple setup screen where they select:

Job Title

Seniority (Junior / Mid / Senior)

Interview Mode (Practice / Exam)

Language (English for MVP; Arabic later)

Number of Questions (3/5/10)

User action:
Clicks “Start Interview”.

Goal: Gather parameters and create a session.

STEP 3 — Mock Interview (Core Experience)
Sequence:

Avatar appears (or voice only in MVP).

AI asks Question #1.

User answers (via mic or typing).

AI evaluates answer (in the background).

Next question loads automatically.

Repeat until completion.

User actions:

Start answering

Stop answering

See progress (“Question 3 of 5”)

Goal: Deliver strong value so they upgrade.

STEP 4 — Interview Results

After last question:

AI generates:

Overall score

Skills breakdown

Strengths

Weaknesses

Action plan

Suggested roles

User action:
Sees detailed report.

Goal: Show enough value to convince them to subscribe.

STEP 5 — Call to Action (Upgrade)

User sees limited free features:

"Unlock full interview history"

"Unlock unlimited interviews"

"Unlock CV analyzer"

User action:
Subscribe monthly.

STEP 6 — Career Dashboard (Returning User)

After subscription, user enjoys:

History of interviews

CV Analyzer

ATS Job Tracker

Career Agent Chat

Skill Progress Chart

Goal: Retain them → long-term subscription.

⭐ 2) KEY SCREENS (What your Next.js app needs)

Here are all the essential screens/pages grouped logically.

A. PUBLIC PAGES
1. Landing Page (/)

Hero (headline + CTA)

“How it Works”

Feature overview

Pricing preview

Testimonials (later)

FAQ

B. INTERVIEW EXPERIENCE
2. Interview Setup (/interview/setup)

Fields:

Job title (input)

Seniority (select)

Language (select)

Interview length (select)

Start button

3. Interview Room (/interview/session/[sessionId])

Contains:

Avatar / Video area

Current question text

Progress indicator (e.g., Q3 of 5)

Voice recorder OR text box

Submit button

Loading states while evaluating

Optional transcript

Optional mini-feedback during practice mode

This is the most important screen in the entire SaaS.

4. Interview Report (/interview/report/[sessionId])

Sections:

Overall score

Detailed scoring (clarity, relevance, structure)

Strengths

Weaknesses

Action plan

Suggested roles

CTA: “Practice Again”

CTA: “Upgrade to unlock unlimited interviews”

C. USER ACCOUNT / SAAS
5. Login / Register (/auth/*)

(Phase 2 – optional early)

Email/password login

Social login (Google, later)

6. Career Dashboard (/dashboard)

(Full SaaS feature)

Sections:

Interview history

CV analyzer status

Upcoming skill plan

Subscription status

Quick actions: “Start Interview”, “Analyze CV”, “Talk to Career Agent”

D. CV TOOLS (Phase 2)
7. CV Analyzer (/cv/analyze)

Upload PDF/Word

ATS score

Issues & fixes

Download improved CV

8. CV Builder (/cv/builder)

Select template

Autofill via AI

Export to PDF/Word

E. JOB APPLICATION TOOLS (Phase 3)
9. Job Tracker (/jobs/tracker)

Pipeline with stages:

Applied → Shortlist → Interview → Offer

10. Job Description Analyzer (/jobs/analysis)

Paste job description → AI extracts:

Key skills

Match score

Suggestions to improve CV/interview answers

F. CAREER AGENT (Phase 3–4)
11. AI Career Chat (/career/agent)

Chat-based personal assistant:

Suggest roles

Review job posts

Recommend trainings

⭐ 3) FEATURE LIST (Complete, Organized, Professional)

Organized by pillars for clarity and roadmap planning.

⭐ PILLAR 1: AI Interview Coaching (MVP)
Core Features:

AI Interview Simulation

Avatar or Voice-based interviewer

Dynamic question generation

Real-time scoring

Strengths/Weaknesses feedback

Action plan

Suggested roles

Multi-mode interview:

Practice

Exam

Technical

HR Behavioral

Supporting:

Progress Tracking

Multiple languages (EN/AR in future)

Question database expansion

⭐ PILLAR 2: CV & Resume Toolkit (Phase 2)

CV Analyzer

ATS score

Ability to rewrite CV for specific job

Grammar & clarity checks

CV Template Gallery

Cover Letter Generator

Portfolio builder (optional)

⭐ PILLAR 3: Career Agent (Phase 3)

AI chat assistant

Job suggestions

Skill & course recommendations

Weekly improvement plan

⭐ PILLAR 4: Job Application Tools (Phase 3)

ATS-style job tracker

Auto follow-up email generator

Job description analyzer

Match score calculation

Document attachments per job application

⭐ PILLAR 5: User & Subscription System

Login / Register

Subscription tiers:

Free

Standard

Pro

Elite

Payment integration (Paymob / Stripe)

Profile page

Interview history

Usage analytics

⭐ FINAL OUTPUT SUMMARY (For Clarity)

You now have:

✔ Core User Journey

Clear flow from landing → interview → report → conversion → dashboard

✔ Key Screens

Full list of needed pages for MVP → Phase 2 → Phase 3

✔ Full Feature List

Organized by product pillars and dev phases

If you want, I can now create:

1) A polished UX flowchart
2) A full 12-month roadmap
3) A spec document for Phase 1 (MVP)
4) A ready-to-use Next.js + FastAPI folder structure with all files stubbed
5) A wireframe diagram in ASCII or Figma-like text