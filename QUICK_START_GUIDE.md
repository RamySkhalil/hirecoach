# 🚀 Quick Start Guide

## Frontend Setup

### 1. Configure Environment Variables

Create `frontend/.env.local` file with:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Clerk Authentication Keys (from clerk.dev dashboard)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

> **Note:** If `NEXT_PUBLIC_API_URL` is not set, it will default to `http://localhost:8000`

### 2. Install Dependencies

```bash
cd frontend
npm install
```

### 3. Start Frontend

```bash
npm run dev
```

Frontend will run on: http://localhost:3000

---

## Backend Setup

### 1. Configure Environment Variables

Create `backend/.env` file with:

```bash
# Database
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# OpenAI
OPENAI_API_KEY=sk-...

# Clerk (for webhook signature verification)
CLERK_WEBHOOK_SECRET=whsec_...

# App Settings
DEBUG=True
LLM_MODEL=gpt-4o
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
python -m app.db
```

### 4. Seed Pricing Data

```bash
python -m app.seed_pricing
```

### 5. Start Backend

```bash
uvicorn app.main:app --reload
```

Backend will run on: http://localhost:8000

---

## ✅ Verify Setup

### 1. Check Backend Health

Open in browser: http://localhost:8000/health

Should return:
```json
{
  "status": "ok",
  "message": "Backend is running",
  "version": "1.0.0"
}
```

### 2. Check Database Connection

Open: http://localhost:8000/health/db

Should return:
```json
{
  "status": "ok",
  "database": "connected",
  "tables": 15
}
```

### 3. Check Pricing Plans

Open: http://localhost:8000/pricing/plans

Should return array of plans:
```json
[
  {
    "code": "free",
    "name": "Free",
    "prices": [...],
    "features": [...]
  },
  ...
]
```

### 4. Test Frontend

1. Open http://localhost:3000
2. Sign in with Clerk
3. Navigate to http://localhost:3000/pricing
4. Should see pricing plans loaded
5. Check navbar for plan badge

---

## 🐛 Troubleshooting

### "Failed to fetch" Error

**Cause:** Backend is not running or wrong API URL

**Solution:**
1. Make sure backend is running: `uvicorn app.main:app --reload`
2. Check `frontend/.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
3. Restart frontend after changing env vars: `npm run dev`

### "No module named 'app'" Error

**Cause:** Running uvicorn from wrong directory

**Solution:**
```bash
cd backend
uvicorn app.main:app --reload
```

### Database Connection Error

**Cause:** Invalid DATABASE_URL or Neon DB not accessible

**Solution:**
1. Check `backend/.env` has correct DATABASE_URL
2. Verify Neon database is running
3. Test connection: `python backend/test_neon_connection.py`

### Pricing Plans Not Loading

**Cause:** Database not seeded

**Solution:**
```bash
cd backend
python -m app.seed_pricing
```

### Clerk Authentication Issues

**Cause:** Missing or incorrect Clerk keys

**Solution:**
1. Go to https://dashboard.clerk.com
2. Get your API keys
3. Add to `frontend/.env.local`
4. Restart frontend

---

## 📦 Complete Startup Commands

### Terminal 1 (Backend)
```bash
cd backend
uvicorn app.main:app --reload
```

### Terminal 2 (Frontend)
```bash
cd frontend
npm run dev
```

---

## 🎯 Common Tasks

### Reset Database
```bash
cd backend
python -m app.db
python -m app.seed_pricing
```

### View All Routes
Open: http://localhost:8000/docs

### Test API Endpoint
```bash
curl http://localhost:8000/pricing/plans
```

### Check Logs
- **Backend:** Check terminal running uvicorn
- **Frontend:** Check browser console (F12)

---

## 🔧 Development Tips

1. **Hot Reload:** Both backend (with `--reload`) and frontend (Next.js) support hot reloading
2. **API Docs:** FastAPI auto-generates docs at http://localhost:8000/docs
3. **Environment Variables:** Restart servers after changing `.env` files
4. **Database Changes:** Run migrations or `python -m app.db` after model changes
5. **Clerk Webhooks:** Use ngrok for local webhook testing

---

## 🎉 You're All Set!

If both servers are running and you can:
- ✅ Visit http://localhost:3000
- ✅ Sign in with Clerk
- ✅ See pricing plans
- ✅ See plan badge in navbar

Then you're ready to develop! 🚀

