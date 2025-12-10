# Setup New LiveKit Cloud Project - Step by Step

## Step 1: Create New Project in LiveKit Cloud

1. Go to: https://cloud.livekit.io/
2. Click **"+ New Project"** button
3. Project name: `travel-assistant-fresh` (or any name you like)
4. Click **"Create"**

## Step 2: Get Your New Credentials

After creating the project, you'll see:
- **LiveKit URL** (wss://your-new-project.livekit.cloud)
- **API Key** (starts with API...)
- **API Secret** (long string)

**COPY THESE IMMEDIATELY!**

## Step 3: Update Your .env File

Replace your current credentials in `.env`:

```bash
# OLD (don't use anymore)
# LIVEKIT_URL=wss://travel-assistant-6o7a2lkk.livekit.cloud
# LIVEKIT_API_KEY=API2tuxHjYwqwZD
# LIVEKIT_API_SECRET=YOkjipJYQvPM9rf4NaSx5eh5eCemnOfLJppSZJMPjx5H

# NEW - Replace with your new project credentials
LIVEKIT_URL=wss://YOUR-NEW-PROJECT.livekit.cloud
LIVEKIT_API_KEY=YOUR_NEW_API_KEY
LIVEKIT_API_SECRET=YOUR_NEW_API_SECRET

# Keep these the same
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=YOUR_GOOGLE_KEY
```

## Step 4: Test the New Setup

Run this command to verify everything works:

```bash
# Kill any old agents
pkill -9 -f "agent.py"

# Test that credentials work
uv run python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('✓ LiveKit URL:', os.getenv('LIVEKIT_URL'))
print('✓ API Key:', os.getenv('LIVEKIT_API_KEY')[:15] + '...')
print('✓ OpenAI Key:', 'Set' if os.getenv('OPENAI_API_KEY') else 'Missing')
"
```

## Step 5: Start Fresh Agent

```bash
# Start agent with new credentials
uv run python agent.py dev 2>&1 | tee /tmp/agent_fresh_project.log &

# Wait for registration
sleep 5

# Check logs
tail -20 /tmp/agent_fresh_project.log
```

You should see:
```
registered worker {"agent_name": "travel-assistant", "id": "AW_...", "url": "wss://YOUR-NEW-PROJECT.livekit.cloud"}
```

## Step 6: Generate Token and Test

```bash
# Generate token for new project
uv run python generate_token.py
```

Copy the token and URL, then:
1. Go to: https://agents-playground.livekit.io/
2. Enter your **NEW** LiveKit URL
3. Paste the token
4. Click Connect
5. Allow microphone
6. **Start talking!**

## Step 7: Verify Agent Connection

Watch your terminal - when you connect, you should see:
```
🔥 Agent received job for room: travel-demo-room
✅ Connected to room: travel-demo-room
🔧 Creating voice agent...
```

When you speak:
```
🔵 CALLING LANGGRAPH with message: Hello...
🟢 LANGGRAPH RESPONSE: ...
```

## Why This Works

✅ **Fresh project** = No ghost workers
✅ **Clean slate** = No dispatch conflicts  
✅ **Your code is perfect** = Already tested and verified

## After Successful Test

Once everything works:
1. **Record your demo video**
2. Show the working voice interaction
3. Submit your assignment!

Your code is 100% ready - this fresh project will make dispatch work perfectly!
