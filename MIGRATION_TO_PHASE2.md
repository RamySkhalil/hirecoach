# 🔄 Migration Guide: Phase 1 → Phase 2

Quick guide to upgrade from Phase 1 to Phase 2 with real AI services.

## What's Changing?

### Phase 1 (Baseline)
- ✅ Template-based questions
- ✅ Length-based scoring
- ✅ Text-only answers
- ❌ No voice features
- ❌ Generic feedback

### Phase 2 (AI-Powered)
- ✅ AI-generated questions
- ✅ Intelligent evaluation
- ✅ Voice answers (STT)
- ✅ Audio questions (TTS)
- ✅ Personalized feedback

## Migration Steps

### 1. Update Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `openai` - For GPT-4 LLM
- `anthropic` - For Claude (alternative)
- `elevenlabs` - For text-to-speech
- `deepgram-sdk` - For speech-to-text

### 2. Get API Keys

#### OpenAI (Required for LLM)
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Copy key (starts with `sk-`)

#### ElevenLabs (Required for TTS)
1. Go to https://elevenlabs.io/
2. Sign up for free account (10,000 chars/month free)
3. Go to Profile → API Keys
4. Copy API key

#### Deepgram (Required for STT)
1. Go to https://console.deepgram.com/
2. Sign up ($200 free credit)
3. Create new API key
4. Copy key

### 3. Update Environment File

Edit `backend/.env`:

```env
# === Add these new lines ===

# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7

# Text-to-Speech
ELEVENLABS_API_KEY=your-elevenlabs-key-here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL=eleven_multilingual_v2

# Speech-to-Text
STT_PROVIDER=deepgram
DEEPGRAM_API_KEY=your-deepgram-key-here
```

### 4. Restart Backend

```bash
# Stop the server (Ctrl+C)
# Then restart
uvicorn app.main:app --reload
```

### 5. Test Integration

Visit http://localhost:8000/docs

New endpoints should appear:
- `GET /media/tts/voices` - List TTS voices
- `GET /interview/question/{id}/audio` - Get question audio

### 6. No Frontend Changes Needed!

The frontend already includes voice components. Just refresh the page.

## Verification Checklist

- [ ] Backend restarts without errors
- [ ] API docs show new endpoints
- [ ] Start new interview - questions are unique/intelligent
- [ ] Speaker icon appears in interview room
- [ ] Clicking speaker plays question audio
- [ ] Microphone button appears
- [ ] Recording works and transcribes to text
- [ ] Answer evaluation has specific, personalized feedback
- [ ] Final report has detailed AI-generated insights

## Cost Implications

### Free Tier Limits

| Service | Free Tier | Notes |
|---------|-----------|-------|
| OpenAI | $5 credit | Expires after 3 months |
| ElevenLabs | 10K chars/month | ~50-100 questions |
| Deepgram | $200 credit | ~4,600 minutes |

### Typical Usage

One complete interview (5 questions):
- OpenAI: ~$0.02
- ElevenLabs: ~$0.20
- Deepgram: ~$0.04
- **Total**: ~$0.26

**100 interviews/month** = ~$26

Very affordable for a premium AI experience!

## Rollback Plan

If you need to revert to Phase 1:

### Option 1: Remove API Keys

Remove or comment out API keys in `.env`:
```env
# OPENAI_API_KEY=...
# ELEVENLABS_API_KEY=...
# DEEPGRAM_API_KEY=...
```

System will automatically use dummy implementations.

### Option 2: Downgrade Dependencies

```bash
cd backend
git checkout main  # or your Phase 1 branch
pip install -r requirements.txt
```

## Common Issues

### Issue: "pip install failed"

**Solution**:
```bash
# Update pip
pip install --upgrade pip

# Try again
pip install -r requirements.txt
```

### Issue: "Module not found: openai"

**Solution**:
```bash
# Ensure virtual environment is activated
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Reinstall
pip install openai
```

### Issue: "Invalid API key"

**Solution**:
1. Check key format (OpenAI starts with `sk-`)
2. Verify key is active in provider dashboard
3. Check for extra spaces in `.env` file
4. Restart backend after changing `.env`

### Issue: Voice recording not working

**Solution**:
1. Use Chrome or Edge (best support)
2. Allow microphone permissions
3. Use HTTPS in production (required for mic access)
4. Check browser console for errors

## Testing Without API Keys

You can still test the full flow without keys:

1. **Questions**: Will use templates (like Phase 1)
2. **Evaluation**: Will use length-based scoring
3. **TTS**: Will show "not available" message
4. **STT**: Will show "not configured" message

Text-based interviews work perfectly without any API keys!

## Production Deployment

### Environment Variables

Set these in your hosting platform:

**Heroku**:
```bash
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set ELEVENLABS_API_KEY=...
heroku config:set DEEPGRAM_API_KEY=...
```

**AWS/Docker**:
Use AWS Systems Manager Parameter Store or Docker secrets

**Vercel** (Frontend):
Add in project settings → Environment Variables

### Security

1. **Never commit `.env` files** (already in .gitignore)
2. **Rotate keys** every 90 days
3. **Set up billing alerts** in each provider dashboard
4. **Monitor usage** weekly
5. **Use rate limiting** in production

## Support

**Stuck?** Check:
- [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md) - Full documentation
- [API_REFERENCE.md](API_REFERENCE.md) - Endpoint details
- [backend/README.md](backend/README.md) - Service specifics
- API docs: http://localhost:8000/docs

**Still having issues?**
- Check backend console logs
- Verify all dependencies installed
- Test API keys in provider dashboards
- Try one service at a time (start with LLM only)

---

**Migration should take 10-15 minutes. The upgrade is worth it for the AI-powered experience!** 🚀

