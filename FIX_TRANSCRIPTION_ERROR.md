# Fix Transcription Error - Step by Step

## 🔍 Quick Diagnosis

### Step 1: Test OpenAI Configuration

Open in browser:
```
http://localhost:3000/api/test-whisper
```

**Expected result:**
```json
{
  "success": true,
  "message": "OpenAI configuration looks good!",
  "keyPreview": "sk-proj-...",
  "keyLength": 164
}
```

**If you see error:**
- "OPENAI_API_KEY not found" → Add key to `.env.local`
- "Invalid API key" → Key is wrong/expired
- Other error → See hints in response

---

### Step 2: Check Browser Console

Look for detailed error in console:
```
[Whisper] Error details: {
  message: "...",
  status: ...,
  code: "..."
}
```

Common errors:

| Error Message | Cause | Fix |
|--------------|-------|-----|
| "Invalid API key" | Wrong/expired key | Get new key from OpenAI |
| "Insufficient quota" | No credits | Add credits to OpenAI account |
| "Rate limit exceeded" | Too many requests | Wait a minute, try again |
| "Network error" | Can't reach OpenAI | Check internet connection |
| "File too large" | Audio > 25MB | Shouldn't happen with short recordings |

---

### Step 3: Check Network Tab

1. Open DevTools (F12)
2. Go to **Network** tab
3. Click **Record** to start/stop
4. **Find** `/api/transcribe` request
5. Click it to see details
6. Look at **Response** tab

**Should see:**
```json
{
  "text": "your transcribed text"
}
```

**If error:**
```json
{
  "error": "Transcription failed",
  "details": "..."
}
```

Copy the details and check below.

---

## 🔧 Common Fixes

### Fix 1: API Key Not Loaded

**Check:**
```bash
cd frontend
cat .env.local | grep OPENAI_API_KEY
```

**Should show:**
```
OPENAI_API_KEY=sk-proj-your-key-here
```

**If missing, add it:**
```bash
echo "OPENAI_API_KEY=sk-proj-your-actual-key" >> .env.local
```

**Then restart frontend:**
```bash
npm run dev
```

---

### Fix 2: Invalid API Key

**Symptoms:**
- 401 Unauthorized error
- "Invalid API key" in console

**Fix:**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Update `frontend/.env.local`:
   ```
   OPENAI_API_KEY=sk-proj-NEW-KEY-HERE
   ```
4. Restart frontend: `npm run dev`

---

### Fix 3: No Credits / Quota Exceeded

**Symptoms:**
- "Insufficient quota" error
- 429 status code

**Fix:**
1. Go to https://platform.openai.com/account/billing
2. Add credits (minimum $5)
3. Wait a few minutes for activation
4. Try again

---

### Fix 4: Wrong Environment File

**Problem:** Key is in wrong file

**Check:**
```bash
cd frontend
ls -la | grep env
```

**Should see:**
- `.env.local` ✅ (this is the one that's used)

**NOT:**
- `.env` ❌ (not used in development)
- `.env.development` ❌ (optional, but .env.local takes precedence)

**Fix:**
Make sure key is in `.env.local` specifically!

---

### Fix 5: Key Has Spaces/Newlines

**Problem:** Key was copied with extra spaces

**Check:**
```bash
cd frontend
cat .env.local | grep OPENAI_API_KEY | wc -c
```

**Should be around 175-180 characters total**

**If much longer, you have extra spaces/newlines**

**Fix:**
Edit `.env.local` and make sure it's one line:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

No spaces before/after the `=` sign!

---

## 🧪 Manual Test

### Test Whisper Directly

Create a test file `test-whisper.html`:

```html
<!DOCTYPE html>
<html>
<body>
  <h1>Test OpenAI Whisper</h1>
  <button onclick="testWhisper()">Test Transcription</button>
  <pre id="result"></pre>

  <script>
    async function testWhisper() {
      const result = document.getElementById('result');
      result.textContent = 'Testing...';
      
      try {
        // Test with a tiny audio file (you'd need to create one)
        const response = await fetch('/api/test-whisper');
        const data = await response.json();
        result.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        result.textContent = 'Error: ' + err.message;
      }
    }
  </script>
</body>
</html>
```

---

## 📊 Check OpenAI Status

### Verify OpenAI is Working

Go to: https://status.openai.com/

**If there's an outage:**
- Orange/Red indicators
- Recent incidents

**Wait until it's green, then try again**

---

## 🔍 Advanced Debugging

### Check Frontend Terminal Output

Look at the terminal where `npm run dev` is running.

**Should see:**
```
[Whisper] Transcribing audio: 2913 bytes, type: audio/webm;codecs=opus
[Whisper] Transcription successful: "your text"
```

**If error:**
```
[Whisper] Error details: {
  message: "...",
  status: ...,
  ...
}
```

**This tells you exactly what failed!**

---

### Test with cURL

Test the API directly:

```bash
# First, create a small test audio file (or use an existing one)
# Then:
curl -X POST http://localhost:3000/api/transcribe \
  -F "file=@test-audio.webm" \
  -v
```

**Should return:**
```json
{"text":"transcribed text","success":true}
```

**If error, you'll see the exact response**

---

## ✅ Verification Checklist

Before asking for help, verify:

- [ ] Frontend is running (`npm run dev`)
- [ ] `.env.local` exists in `frontend/` directory
- [ ] `OPENAI_API_KEY=sk-proj-...` is in `.env.local`
- [ ] Key is valid (test at https://platform.openai.com/playground)
- [ ] You have credits (check https://platform.openai.com/account/billing)
- [ ] Browser console shows `[Whisper] Recording started successfully`
- [ ] Volume bar moves when speaking
- [ ] After stopping, shows `[Whisper] Sending to /api/transcribe`
- [ ] Network tab shows `/api/transcribe` request
- [ ] `/api/test-whisper` returns success

---

## 🆘 Still Not Working?

### Collect This Info:

1. **Test endpoint result:**
   ```
   http://localhost:3000/api/test-whisper
   ```
   Copy the JSON response

2. **Browser console output:**
   - All `[Whisper]` log messages
   - Any errors (red text)

3. **Network tab:**
   - Find `/api/transcribe` request
   - Copy the Response body

4. **Frontend terminal:**
   - Any errors shown where `npm run dev` is running

5. **Environment check:**
   ```bash
   cd frontend
   cat .env.local | grep OPENAI_API_KEY | sed 's/sk-proj.*$/sk-proj-REDACTED/'
   ```

**Send me all of the above!**

---

## 💡 Quick Workaround

If transcription keeps failing, you can **disable voice and use text only**:

In `frontend/app/interview/conversational/[sessionId]/page.tsx`:

```typescript
// Temporarily disable voice
const [voiceEnabled, setVoiceEnabled] = useState(false); // Change to false
```

This lets you **test the conversational AI** while we fix Whisper.

---

## 🎯 Most Common Solution

**90% of the time it's one of these:**

1. ❌ **API key not in `.env.local`** → Add it
2. ❌ **Frontend not restarted** → Restart `npm run dev`
3. ❌ **Invalid API key** → Get new one from OpenAI
4. ❌ **No credits** → Add $5+ to OpenAI account

**Try these first!**

