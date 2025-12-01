# LiveKit Agent Setup Guide

## Quick Install

### Option 1: Install via pip (Recommended)

```bash
# Navigate to agent directory
cd backend/livekit-voice-agent

# Install dependencies
pip install livekit-agents livekit-plugins-openai livekit-plugins-silero
```

### Option 2: Install from requirements.txt

```bash
cd backend/livekit-voice-agent
pip install -r requirements.txt
```

## Required Packages

- **livekit-agents** - Core agents framework
- **livekit-plugins-openai** - OpenAI Realtime integration
- **livekit-plugins-silero** - Voice Activity Detection (VAD)

## Environment Setup

Create `.env.local` in this directory:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=sk-proj-your-key-here

# LiveKit Credentials (required)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Run the Agent

```bash
# Start the agent
python interview_agent.py start

# Or use the CLI directly
livekit-agents start interview_agent.py
```

## Verify Installation

```bash
python -c "from livekit import agents; print('✅ LiveKit Agents installed successfully')"
```

## Troubleshooting

### Import Error: cannot import name 'agents' from 'livekit'

**Problem:** You have `livekit` installed but not `livekit-agents`

**Solution:**
```bash
pip install livekit-agents
```

### Module not found errors

**Problem:** Missing plugin packages

**Solution:**
```bash
pip install livekit-plugins-openai livekit-plugins-silero
```

### Connection errors

**Problem:** Missing or invalid credentials

**Solution:**
- Check `.env.local` has all required variables
- Verify credentials are correct in LiveKit Cloud dashboard
- Ensure `LIVEKIT_URL` starts with `wss://`

## Alternative: Run Without Agent

**Good News:** The interview system works WITHOUT the agent!

If you don't run the agent:
- ✅ Video still works (candidate camera)
- ✅ Text Q&A works normally
- ✅ All scoring/evaluation works
- ❌ No AI voice interaction

The agent is **optional** for enhanced voice features.

## Production Deployment

For production, deploy the agent using:
- **LiveKit Cloud:** Built-in agent hosting
- **Docker:** Containerized deployment
- **Cloud VM:** AWS, GCP, Azure with public URL
- **Serverless:** AWS Lambda, Cloud Functions

See: https://docs.livekit.io/agents/deployment/

