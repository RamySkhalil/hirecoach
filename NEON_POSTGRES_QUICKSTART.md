# Neon Postgres Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Get Your Neon Postgres URL

1. Go to your [Neon Console](https://console.neon.tech)
2. Copy your connection string
3. It should look like:
   ```
   postgresql://user:password@ep-xxxx.us-east-2.aws.neon.tech/neondb
   ```

### Step 2: Update `.env` File

Create or update `backend/.env`:

```env
DATABASE_URL=postgresql://user:password@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Your existing API keys...
OPENAI_API_KEY=sk-...
```

⚠️ **Important:** Make sure to add `?sslmode=require` at the end of your Postgres URL!

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs the new `pgvector==0.2.4` dependency.

### Step 4: Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

**Expected output:**
```
[Config] Loaded settings. OPENAI_API_KEY set: True, DB: postgresql://...
[DB] ✅ pgvector extension enabled successfully.
[DB] ✅ Database tables created/verified successfully.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 5: Verify Connection

Open your browser or use curl:

```bash
# Check database health
curl http://localhost:8000/health/db
```

**Expected response:**
```json
{
  "status": "ok",
  "database": "postgres",
  "pgvector_enabled": true,
  "timestamp": "2024-11-24T12:00:00"
}
```

### Step 6: View All Tables

```bash
curl http://localhost:8000/health/db/tables
```

You should see 11 tables including the new `user_message_embeddings` table.

---

## ✅ You're All Set!

Your backend is now connected to Neon Postgres with:
- ✅ SSL/TLS encryption
- ✅ pgvector extension enabled
- ✅ Vector embeddings support for AI memory
- ✅ All tables created automatically
- ✅ Connection pooling configured

---

## 🔧 Environment Variables Reference

### **Required:**
```env
DATABASE_URL=postgresql://...?sslmode=require
OPENAI_API_KEY=sk-...
```

### **Optional:**
```env
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.7
DEBUG=True
```

---

## 🆘 Troubleshooting

### ❌ "SSL connection required"
**Fix:** Add `?sslmode=require` to your DATABASE_URL

### ❌ "Connection refused"
**Fix:** Check your Neon endpoint is accessible and password is correct

### ❌ "pgvector not enabled"
**Fix:** Run this SQL in Neon console:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 📚 Next Steps

1. **Read Full Documentation:** See `NEON_POSTGRES_INTEGRATION_SUMMARY.md`
2. **Implement Embeddings:** Add embedding generation for Career Agent
3. **Test Semantic Search:** Try similarity queries
4. **Deploy to Production:** Use the same DATABASE_URL in production .env

---

**Need help?** Check the full integration summary for detailed documentation.

