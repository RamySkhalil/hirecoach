# 🚀 Quick Start: Phases 3 & 4

## Try the New CV Analyzer in 3 Minutes!

### Step 1: Install New Dependencies (30 seconds)

```bash
cd backend
pip install PyPDF2==3.0.1 python-docx==1.1.0
```

### Step 2: Start Backend (30 seconds)

```bash
# Still in backend/
uvicorn app.main:app --reload
```

You should see:
```
🚀 Starting Interviewly backend...
📊 Database: sqlite:///./interviewly.db
🔑 API Keys Status:
  OpenAI: ✅ Configured (or ❌ Not set)
  ElevenLabs: ✅ Configured
  ...
✅ Database initialized
```

### Step 3: Start Frontend (30 seconds)

```bash
# New terminal
cd frontend
npm run dev
```

### Step 4: Test CV Analyzer (1 minute)

1. **Open** [http://localhost:3000/cv](http://localhost:3000/cv)

2. **Sign in** (if not already signed in)

3. **Upload a CV**:
   - Drag & drop or click to upload
   - Supports: PDF, DOCX, TXT
   - Max 10MB

4. **Optional**: Add target job and seniority

5. **Click "Analyze CV"**

6. **View Results**:
   - Overall score
   - ATS compatibility score
   - Detailed breakdown
   - Strengths
   - Weaknesses
   - Suggestions
   - Keywords

---

## 🎯 What Works

### CV Analyzer (`/cv`)
- ✅ Upload PDF, DOCX, TXT
- ✅ Automatic text extraction
- ✅ AI-powered analysis (with OpenAI)
- ✅ ATS compatibility scoring
- ✅ Detailed feedback
- ✅ Keyword optimization
- ✅ Beautiful results display

### Interview Coach (`/interview/setup`)
- ✅ Voice-enabled interviews
- ✅ AI evaluation
- ✅ Comprehensive reports

### Authentication
- ✅ Secure sign up/in
- ✅ Protected routes
- ✅ User profiles

---

## 🔑 For Better Results

### Configure OpenAI (Optional but Recommended)

Add to `backend/.env`:
```env
OPENAI_API_KEY=sk-...
```

**Without OpenAI**:
- Basic text extraction works
- Dummy analysis provided
- Scores based on length

**With OpenAI**:
- Intelligent parsing
- Contextual analysis
- Specific suggestions
- Keyword matching
- Target job alignment

---

## 📊 API Endpoints

### CV Analysis

**Upload CV**:
```bash
POST http://localhost:8000/cv/upload
Content-Type: multipart/form-data

file: [your_cv.pdf]
target_job_title: "Software Engineer"  # optional
target_seniority: "mid"  # optional
```

**Get Analysis**:
```bash
GET http://localhost:8000/cv/{analysis_id}
```

**List Analyses**:
```bash
GET http://localhost:8000/cv/?user_id={user_id}&limit=20
```

**Delete Analysis**:
```bash
DELETE http://localhost:8000/cv/{analysis_id}
```

### Interactive API Docs

Visit [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🗄️ Database

### New Tables Created

When you start the backend, these tables are auto-created:

1. ✅ `cv_analyses` - CV analysis results
2. ✅ `users` - User profiles
3. ✅ `subscriptions` - Subscription tiers
4. ✅ `job_postings` - Job listings
5. ✅ `applications` - Job applications

### View Database

```bash
# SQLite (development)
cd backend
sqlite3 interviewly.db
.tables
.schema cv_analyses
```

---

## 🎨 UI Features

### CV Analyzer Page

**Upload Section** (Left):
```
┌─────────────────────────────────┐
│  Upload Your CV                  │
│                                  │
│  [📄 Drop file here]            │
│  PDF, DOCX, TXT (Max 10MB)      │
│                                  │
│  Target Job: [____________]      │
│  Seniority: [Junior|Mid|Senior]  │
│                                  │
│  [Analyze CV →]                  │
└─────────────────────────────────┘
```

**Results Section** (Right):
```
┌─────────────────────────────────┐
│  Analysis Results         [×]    │
│                                  │
│  ┌──────┐ ┌──────┐             │
│  │  85  │ │  82  │             │
│  │ Overall│ │ ATS  │            │
│  └──────┘ └──────┘             │
│                                  │
│  Content     ████████ 85%       │
│  Formatting  ██████░░ 78%       │
│  Keywords    ████░░░░ 65%       │
│  ...                             │
│                                  │
│  ✓ Strengths                     │
│  • Strong technical background   │
│  • Clear experience progression  │
│                                  │
│  ⚠ Areas for Improvement        │
│  • Add more metrics              │
│  • Include certifications        │
│                                  │
│  💡 Suggestions                  │
│  1. Quantify achievements        │
│  2. Add keywords...              │
└─────────────────────────────────┘
```

---

## 📝 Sample Test

### Create Test CV (test.txt)

```
John Doe
Software Engineer
john@example.com | (555) 123-4567

EXPERIENCE

Senior Software Engineer at Tech Corp (2020-Present)
- Led development of microservices architecture
- Improved system performance by 40%
- Mentored junior developers

Software Engineer at StartupCo (2018-2020)
- Built RESTful APIs using Python and FastAPI
- Implemented CI/CD pipelines
- Collaborated with cross-functional teams

EDUCATION

B.S. Computer Science, University (2014-2018)

SKILLS

Python, JavaScript, React, FastAPI, Docker, AWS, PostgreSQL
```

### Test It

1. Save above as `test.txt`
2. Visit [http://localhost:3000/cv](http://localhost:3000/cv)
3. Upload `test.txt`
4. Add target job: "Senior Software Engineer"
5. Select seniority: "Senior"
6. Click "Analyze CV"
7. View results!

---

## 🐛 Troubleshooting

### "PyPDF2 not installed"
```bash
cd backend
pip install PyPDF2==3.0.1
```

### "python-docx not installed"
```bash
cd backend
pip install python-docx==1.1.0
```

### "File upload failed"
- Check file size < 10MB
- Verify file type: PDF, DOCX, or TXT
- Check backend console for errors

### "Database errors"
```bash
# Delete old database and restart
cd backend
rm interviewly.db
uvicorn app.main:app --reload
```

### Frontend errors
```bash
cd frontend
rm -rf .next
npm run dev
```

---

## 📚 More Info

- **Full Details**: See `PHASE_3_4_COMPLETE_SUMMARY.md`
- **Implementation**: See `FUTURE_PHASES_IMPLEMENTATION.md`
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ✨ That's It!

You now have a working CV analyzer with:
- ✅ File upload
- ✅ Text extraction
- ✅ AI analysis
- ✅ ATS scoring
- ✅ Actionable feedback
- ✅ Beautiful UI

**Enjoy testing!** 🎉

