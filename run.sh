#!/bin/bash
echo "Starting LiveKit Agent..."
uv run python agent.py dev > /tmp/livekit.log 2>&1 &
AGENT_PID=$!
echo "Agent PID: $AGENT_PID"
sleep 5

echo ""
echo "Generating token..."
uv run python generate_token.py

echo ""
echo "==================================="
echo "Agent is running (PID: $AGENT_PID)"
echo "Logs: tail -f /tmp/livekit.log"
echo "Stop: kill $AGENT_PID"
echo "==================================="
