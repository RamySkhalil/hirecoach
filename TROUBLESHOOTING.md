# 🔧 Troubleshooting Guide

Common issues and their solutions for Interviewly.

---

## SSL Certificate Error (Windows)

### Error Message
```
FileNotFoundError: [Errno 2] No such file or directory
SSL_CERT_FILE error when calling OpenAI
```

### Solution

**Option 1: Install certifi (Recommended)**
```bash
cd backend
pip install certifi
```

The code automatically uses certifi certificates when available.

**Option 2: Update requirements**
```bash
pip install -r requirements.txt
```

This installs `certifi` which fixes SSL issues on Windows.

**Option 3: Set environment variable manually**
```bash
# Find certifi path
python -c "import certifi; print(certifi.where())"

# Set it (Windows PowerShell)
$env:SSL_CERT_FILE = "C:\path\to\certifi\cacert.pem"

# Or add to .env
SSL_CERT_FILE=C:\path\to\certifi\cacert.pem
```

### Why This Happens
Windows doesn't always have SSL certificates in the expected location. The `certifi` package provides a bundle of trusted CA certificates.

---

## Backend Won't Start

### Issue: "Module not found"

**Solution**:
```bash
cd backend
# Make sure virtual environment is activated
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"

**Solution**:
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### Issue: "Database locked"

**Solution**:
```bash
# Stop all backend instances
# Delete database file
rm backend/interviewly.db  # or del on Windows
# Restart backend (will recreate DB)
```

---

## API Key Issues

### Issue: "Invalid API key"

**Symptoms**:
- LLM returns dummy responses
- TTS/STT not working
- No error messages

**Check**:
1. `.env` file exists in `backend/` directory
2. API keys have no extra spaces
3. Keys start with correct prefix:
   - OpenAI: `sk-...`
   - ElevenLabs: alphanumeric
   - Deepgram: alphanumeric
4. Keys are active in provider dashboards

**Solution**:
```bash
# Verify .env file
cat backend/.env  # Mac/Linux
type backend\.env  # Windows

# Should show:
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
DEEPGRAM_API_KEY=...

# Restart backend after changing .env
```

### Issue: "Rate limit exceeded"

**Solution**:
1. Check usage in provider dashboard
2. Upgrade plan if needed
3. Wait a few minutes and retry
4. Implement caching (future enhancement)

---

## Frontend Issues

### Issue: Voice recording not working

**Symptoms**:
- Microphone button doesn't work
- Permission denied errors
- No audio captured

**Solutions**:

1. **Browser Compatibility**
   - Use Chrome, Edge, or Firefox (latest versions)
   - Safari has limited support

2. **Permissions**
   - Allow microphone access when prompted
   - Check browser settings: chrome://settings/content/microphone

3. **HTTPS Required** (Production)
   - Mic access requires HTTPS in production
   - Use `localhost` for development (works without HTTPS)

4. **Check Console**
   - Open DevTools (F12)
   - Look for error messages
   - Check if MediaRecorder is supported

### Issue: Audio not playing (TTS)

**Symptoms**:
- Speaker button doesn't work
- "Audio not available" message
- No sound

**Solutions**:

1. **Check API Key**
   ```bash
   # Verify ELEVENLABS_API_KEY in backend/.env
   ```

2. **Test Endpoint**
   ```bash
   curl -X POST http://localhost:8000/media/tts \
     -H "Content-Type: application/json" \
     -d '{"text":"Hello world"}'
   ```

3. **Check Browser Console**
   - F12 → Console tab
   - Look for failed requests
   - Check Network tab for 503 errors

4. **Verify Backend Running**
   ```bash
   curl http://localhost:8000/health
   ```

### Issue: "Cannot connect to backend"

**Symptoms**:
- "Failed to start interview"
- "Network error"
- CORS errors

**Solutions**:

1. **Verify Backend Running**
   - Check http://localhost:8000
   - Should see health check response

2. **Check Frontend .env.local**
   ```bash
   # Should contain:
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **CORS Issues**
   - Backend CORS should allow all origins in dev
   - Check `backend/app/main.py` CORS settings

4. **Port Mismatch**
   - Backend: 8000
   - Frontend: 3000
   - Update env if using different ports

---

## Database Issues

### Issue: "Database is locked"

**Solution**:
```bash
# Stop all processes accessing DB
# Delete and recreate
cd backend
rm interviewly.db  # or del on Windows
# Restart backend
```

### Issue: "Table doesn't exist"

**Solution**:
```bash
# Delete DB and let it recreate
rm backend/interviewly.db
# Restart backend - tables auto-create
```

### Issue: Want to use PostgreSQL instead of SQLite

**Solution**:
```bash
# 1. Install PostgreSQL
# 2. Create database
createdb interviewly

# 3. Update backend/.env
DATABASE_URL=postgresql://user:password@localhost:5432/interviewly

# 4. Restart backend
```

---

## Dependency Issues

### Issue: "pip install failed"

**Solution**:
```bash
# Update pip
python -m pip install --upgrade pip

# Clear cache
pip cache purge

# Reinstall
pip install -r requirements.txt
```

### Issue: "npm install failed"

**Solution**:
```bash
cd frontend

# Clear cache
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

---

## Performance Issues

### Issue: Slow question generation

**Cause**: OpenAI API can take 3-5 seconds

**Solutions**:
1. Use gpt-4o-mini instead of gpt-4o (faster)
2. Implement caching for common questions
3. Pre-generate questions in background

### Issue: Slow audio generation

**Cause**: ElevenLabs takes 1-2 seconds per question

**Solutions**:
1. Pre-generate audio after session creation
2. Cache audio for identical questions
3. Use streaming mode (future)

---

## Development Tips

### View Database Contents

**SQLite**:
```bash
cd backend
sqlite3 interviewly.db

.tables
SELECT * FROM interview_sessions;
.quit
```

**PostgreSQL**:
```bash
psql -d interviewly

\dt
SELECT * FROM interview_sessions;
\q
```

### Check API Responses

**Use Swagger UI**:
http://localhost:8000/docs

**Or curl**:
```bash
# Health check
curl http://localhost:8000/

# Start interview
curl -X POST http://localhost:8000/interview/start \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Test",
    "seniority": "mid",
    "language": "en",
    "num_questions": 3
  }'
```

### Enable Debug Logging

**Backend**:
```python
# backend/app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend**:
```typescript
// Add console.log in components
console.log('Current state:', state)
```

---

## Getting Help

### Check These First

1. **Backend logs** - Console where uvicorn is running
2. **Frontend logs** - Browser DevTools console (F12)
3. **API docs** - http://localhost:8000/docs
4. **Documentation** - README.md, PHASE2_COMPLETE.md

### Verify Setup

```bash
# Backend health
curl http://localhost:8000/health

# Frontend running
curl http://localhost:3000

# API connection
# Open http://localhost:3000 and check Network tab
```

### Common Fixes

1. **Restart everything**
   ```bash
   # Stop backend (Ctrl+C)
   # Stop frontend (Ctrl+C)
   # Restart both
   ```

2. **Clear caches**
   ```bash
   # Backend: Delete .venv and reinstall
   # Frontend: Delete node_modules and reinstall
   # Database: Delete interviewly.db
   ```

3. **Check versions**
   ```bash
   python --version  # Should be 3.9+
   node --version    # Should be 18+
   pip --version
   npm --version
   ```

### Still Stuck?

1. Check all documentation files
2. Look for similar errors in error messages
3. Verify all environment variables set
4. Try with API keys disabled (dummy mode)
5. Test with minimal setup (no voice features)

---

## Quick Diagnostic Commands

```bash
# Backend health
curl http://localhost:8000/health

# Check if backend is listening
netstat -an | grep 8000  # Mac/Linux
netstat -an | findstr 8000  # Windows

# Check frontend
curl http://localhost:3000

# View backend logs
# (In terminal where uvicorn is running)

# View frontend logs
# Browser DevTools → Console

# Test API key
curl -X POST http://localhost:8000/interview/start \
  -H "Content-Type: application/json" \
  -d '{"job_title":"Test","seniority":"mid","language":"en","num_questions":1}'
```

---

**If you encounter an issue not listed here, check the backend console logs and browser console for detailed error messages.**

