# How to Clean Up LiveKit Workers

## Option 1: Via LiveKit Cloud Dashboard (RECOMMENDED)

1. Go to: https://cloud.livekit.io/
2. Sign in to your account
3. Select your project: **travel-assistant-6o7a2lkk**
4. Click on **"Agents"** in the left sidebar
5. You'll see all registered workers (including old ones)
6. **Deactivate or delete old workers** that are no longer running

## Option 2: Kill Local Processes

Kill all local agent processes on your machine:

```bash
# Kill all Python agent processes
pkill -9 -f "agent.py"

# Kill all uv processes running agent
pkill -9 -f "uv run python agent.py"

# Verify everything is killed
ps aux | grep agent.py | grep -v grep
```

## Option 3: Restart with Unique Agent Name

Modify your agent to use a unique name each time:

```python
# In agent.py, change:
@server.rtc_session(agent_name="travel-assistant")

# To:
import time
agent_name = f"travel-assistant-{int(time.time())}"
@server.rtc_session(agent_name=agent_name)
```

## Current Situation

Your workers showing in LiveKit Cloud:
- These are "ghost" registrations from previous runs
- They appear "ready" but aren't actually running
- LiveKit Cloud tries to dispatch to them first
- This causes dispatch failures

## Solution for Demo

**For your demo, use the LiveKit Cloud dashboard to:**
1. Delete/deactivate ALL old workers
2. Then start ONE fresh agent
3. Immediately generate token and connect

This ensures LiveKit dispatches to your ONLY active worker.

## Quick Commands

```bash
# 1. Kill everything local
pkill -9 -f "agent.py"

# 2. Clean up old log files
rm -f /tmp/agent*.log

# 3. Start fresh agent
uv run python agent.py dev 2>&1 | tee /tmp/agent_new.log &

# 4. Wait 5 seconds for registration
sleep 5

# 5. Generate token
uv run python generate_token.py

# 6. Connect immediately in playground
```
