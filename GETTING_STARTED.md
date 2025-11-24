# 🚀 Getting Started with Interviewly

This guide will help you get Interviewly up and running on your local machine in minutes.

## Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.9+** installed ([Download](https://www.python.org/downloads/))
- ✅ **Node.js 18+** installed ([Download](https://nodejs.org/))
- ✅ A code editor (VS Code recommended)
- ✅ Terminal/Command Prompt access

### Verify Installation

```bash
# Check Python version
python --version
# or
python3 --version

# Check Node version
node --version

# Check npm version
npm --version
```

## Quick Start (Automated)

### Windows
```bash
# Run the setup script
start.bat
```

### Mac/Linux
```bash
# Make script executable
chmod +x start.sh

# Run the setup script
./start.sh
```

The script will:
1. Create Python virtual environment
2. Install backend dependencies
3. Install frontend dependencies
4. Create environment files

## Manual Setup

If you prefer manual setup or the script doesn't work:

### Step 1: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Windows:
copy env.example .env
# Mac/Linux:
cp env.example .env

# (Optional) Edit .env if you want to use PostgreSQL instead of SQLite
```

### Step 2: Frontend Setup

Open a **new terminal** window and:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local file
# Windows:
copy env.local.example .env.local
# Mac/Linux:
cp env.local.example .env.local
```

### Step 3: Start the Backend

In the **first terminal** (with backend venv activated):

```bash
cd backend
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
🚀 Starting Interviewly backend...
✅ Database initialized
```

**Backend is now running!**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Step 4: Start the Frontend

In the **second terminal**:

```bash
cd frontend
npm run dev
```

You should see:
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
✓ Ready in 2.5s
```

**Frontend is now running!**

## Access the Application

Open your browser and go to:

🌐 **http://localhost:3000**

You should see the Interviewly landing page!

## First Interview

1. Click **"Start Interview"** on the landing page
2. Fill in the form:
   - **Job Title**: e.g., "Software Engineer"
   - **Seniority**: Choose Junior, Mid, or Senior
   - **Language**: English or Arabic
   - **Questions**: Select 3-10 questions
3. Click **"Start Interview"**
4. Answer each question with detailed responses
5. View your comprehensive report!

## Troubleshooting

### Backend Issues

#### "Python not found"
- Install Python from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

#### "Module not found" errors
```bash
cd backend
pip install -r requirements.txt
```

#### Port 8000 already in use
```bash
# Kill the process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9

# Or use a different port:
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues

#### "Node not found"
- Install Node.js from [nodejs.org](https://nodejs.org/)

#### Dependencies won't install
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Port 3000 already in use
```bash
# Kill the process
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:3000 | xargs kill -9

# Or use a different port:
npm run dev -- -p 3001
```

#### Can't connect to backend
1. Ensure backend is running on port 8000
2. Check `.env.local` has correct API URL:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. Check browser console for CORS errors

### Database Issues

#### "Database locked" (SQLite)
- Close any other processes accessing the database
- Delete `backend/interviewly.db` and restart

#### Want to use PostgreSQL instead of SQLite?
1. Install PostgreSQL
2. Create a database:
   ```sql
   CREATE DATABASE interviewly;
   ```
3. Update `backend/.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/interviewly
   ```
4. Restart backend

## Exploring the API

Visit **http://localhost:8000/docs** to see interactive API documentation.

Try these endpoints in the Swagger UI:

1. **GET /** - Health check
2. **POST /interview/start** - Start an interview
3. **POST /interview/answer** - Submit an answer
4. **POST /interview/finish** - Get final report

## Project Structure

```
interviewly/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── routes/   # API endpoints
│   │   ├── services/ # Business logic
│   │   ├── models.py # Database models
│   │   └── main.py   # App entry point
│   └── requirements.txt
├── frontend/         # Next.js frontend
│   ├── app/         # Pages
│   │   ├── page.tsx              # Landing page
│   │   └── interview/
│   │       ├── setup/            # Setup form
│   │       ├── session/[id]/     # Interview room
│   │       └── report/[id]/      # Final report
│   ├── components/  # React components
│   └── lib/         # API client
└── README.md
```

## Development Tips

### Hot Reload

Both backend and frontend support hot reload:
- **Backend**: Edit any Python file and the server auto-restarts
- **Frontend**: Edit any React component and it updates instantly

### Viewing Database

#### SQLite
```bash
cd backend
sqlite3 interviewly.db
.tables
SELECT * FROM interview_sessions;
.quit
```

Or use a GUI tool like [DB Browser for SQLite](https://sqlitebrowser.org/)

#### PostgreSQL
```bash
psql -d interviewly
\dt
SELECT * FROM interview_sessions;
\q
```

### Debugging

#### Backend
Add print statements or use Python debugger:
```python
import pdb; pdb.set_trace()
```

#### Frontend
Use browser DevTools (F12) and check:
- Console for errors
- Network tab for API calls
- React DevTools for component inspection

## Next Steps

- 📚 Read the [full README](README.md) for detailed documentation
- 🎨 Check [DESIGN-SYSTEM.md](DESIGN-SYSTEM.md) for UI guidelines
- 📋 Review [plan.md](plan.md) for project architecture
- 🔧 Customize the LLM service in `backend/app/services/llm_service.py`
- 🎨 Adjust colors and styling in frontend components

## Need Help?

- Check the [README](README.md) for detailed docs
- Review API docs at http://localhost:8000/docs
- Check the [tasks.md](tasks.md) checklist
- Look at code comments for explanations

## What's Next?

Phase 2 will include:
- 🎤 Voice input (Speech-to-Text)
- 🔊 Voice output (Text-to-Speech)
- 👤 AI Avatar interviewer
- 🤖 Real LLM integration (OpenAI/Anthropic)
- 👤 User authentication
- 📄 CV/Resume analysis

---

**Happy Interviewing! 🎉**

