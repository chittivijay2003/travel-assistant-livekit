# LiveKit Voice Agent Assignment

## Introduction

"""
Welcome to the LiveKit Voice Agent assignment! In this assignment, you will build a **voice-to-voice conversational AI agent** using LiveKit's real-time communication infrastructure, integrating the **LangGraph agent you built in your previous assignment**.
"""

### What is LiveKit?
"""
LiveKit is an open-source platform for building real-time audio/video applications. It uses:
- **Rooms**: Virtual spaces where participants connect
- **WebSocket connections**: For signaling and real-time communication
- **Tokens**: JWT-based authentication for secure room access
"""
### Assignment Objectives
"""
By completing this assignment, you will:
1. Set up a LiveKit development environment
2. Create a voice agent that connects to LiveKit rooms
3. **Integrate your LangGraph agent via the LLM adapter**
4. Implement voice-to-voice interaction
5. Test your implementation using pytest
6. Record a demo of your working agent with the LiveKit Playground

---
"""
## Part 1: Environment Setup

### Prerequisites
"""
- Python 3.9+
- Docker (for running LiveKit server locally) OR LiveKit Cloud account
- Your LangGraph agent from the previous assignment
- Google Cloud account (for STT/TTS services)
"""
### Step 1: Install Dependencies
"""
Run the following command to install all required packages:

```bash
pip install livekit \
    livekit-agents \
    livekit-plugins-google \
    livekit-plugins-silero \
    livekit-plugins-langgraph
    langgraph \
    langchain \
    langchain-google-genai \
    python-dotenv \
    pytest \
    pytest-asyncio
```
"""

### Step 2: Configure Environment Variables
"""
Create a `.env` file in your submission directory with the following variables:

```bash
"""
# LiveKit Configuration
# For local: ws://localhost:7880
# For cloud: wss://your-project.livekit.cloud
"""
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
"""
# Google Cloud Configuration (for STT/TTS)
"""
GOOGLE_API_KEY=your_google_api_key
```
"""
"""
**Important Notes:**
- For local development, run LiveKit server using Docker:
  ```bash
  docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp \
      -e LIVEKIT_KEYS="devkey: secret" \
      livekit/livekit-server \
      --dev --bind 0.0.0.0
  ```
- For cloud deployment, sign up at [LiveKit Cloud](https://cloud.livekit.io)
- Get your Google API key from [Google AI Studio](https://aistudio.google.com/)

---
"""
## Part 2: Assignment Requirements

### Your Task
"""
Create a **voice agent** that:

1. **Connects to a LiveKit room** via WebSocket URL and Token
2. **Listens to user speech** using Voice Activity Detection (VAD)
3. **Transcribes speech to text** using Speech-to-Text (STT)
4. **Processes the text using your LangGraph agent** via the LLM adapter
5. **Converts responses to speech** using Text-to-Speech (TTS)
6. **Plays audio back** to the user in real-time

---
"""
## Part 3: Directory Structure (IMPORTANT)
"""
**You MUST maintain the following directory structure exactly:**

```
your_submission/
├── agent.py              # Main agent implementation (REQUIRED)
├── langgraph_agent.py    # Your LangGraph agent from previous assignment (REQUIRED)
├── requirements.txt      # Dependencies list (REQUIRED)
├── .env                  # Environment variables (REQUIRED - will be replaced during testing)
├── .env.example          # Template showing required env vars (REQUIRED)
└── demo.mp4              # Screen recording of your working agent (REQUIRED)
```

**Failure to maintain this structure will result in test failures!**

---
"""
## Part 4: Required Components

### Components in agent.py
"""
Your `agent.py` must implement:

| Function/Class | Description |
|----------------|-------------|
| `get_livekit_url()` | Returns the WebSocket URL for LiveKit from environment |
| `generate_token(room_name, participant_name)` | Generates a valid JWT token for room access |
| `LangGraphLLMAdapter` class | LLM adapter class that wraps your LangGraph agent |
| `create_langgraph_adapter()` | Creates an instance of the LLM adapter |
| `create_voice_agent()` | Creates and returns a configured VoicePipelineAgent |
| `entrypoint(ctx)` | Async function - main entry point for the agent |
"""
### LangGraph LLM Adapter Pattern
"""
You must use the **LLM adapter pattern** to integrate your LangGraph agent:

# TEMPLATE CODE BELOW - SEE PART 5 FOR ACTUAL IMPLEMENTATION
"""
# ```python
# from livekit.agents import llm
#
#
# class LangGraphLLMAdapter(llm.LLM):
#     """Adapter to use LangGraph agent as an LLM in the voice pipeline."""
#
#     def __init__(self, langgraph_agent):
#         super().__init__()
#         self.agent = langgraph_agent
#
#     async def chat(
#         self,
#         chat_ctx: llm.ChatContext,
#         fnc_ctx: llm.FunctionContext | None = None,
#         temperature: float | None = None,
#         n: int | None = None,
#         parallel_tool_calls: bool | None = None,
#     ) -> llm.LLMStream:
#         # TODO Extract user message from chat_ctx
#         # TODO Process through your LangGraph agent
#         # TODO Return response wrapped in LLMStream
#         pass
# ```
"""

This pattern allows your existing LangGraph agent to be used seamlessly in the LiveKit voice pipeline.
This pattern allows your existing LangGraph agent to be used seamlessly in the LiveKit voice pipeline.

---
"""
## Part 5: Code Template
"""
Here's a skeleton to get you started:

```python
"""
# ============================================================================
# ACTUAL IMPLEMENTATION - LiveKit Voice Agent
# ============================================================================

import os
from dotenv import load_dotenv
from datetime import timedelta
from livekit import api
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    AgentServer,
    cli,
    llm,
)
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import openai, silero

# Import your LangGraph agent from previous assignment
from langgraph_agent import create_graph, invoke_graph

load_dotenv()


def get_livekit_url() -> str:
    """Return the LiveKit WebSocket URL from environment."""
    url = os.environ.get("LIVEKIT_URL")
    if not url:
        raise ValueError("LIVEKIT_URL environment variable is required")
    return url


def generate_token(room_name: str, participant_name: str) -> str:
    """Generate a JWT token for room access."""
    api_key = os.environ.get("LIVEKIT_API_KEY")
    api_secret = os.environ.get("LIVEKIT_API_SECRET")

    token = api.AccessToken(api_key, api_secret)
    token.with_identity(participant_name)
    token.with_name(participant_name)
    token.with_grants(
        api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        )
    )
    token.with_ttl(timedelta(hours=1))

    return token.to_jwt()


class LangGraphLLMAdapter(llm.LLM):
    """Adapter to use LangGraph agent as LLM in voice pipeline."""

    def __init__(self, graph):
        super().__init__()
        self.graph = graph

    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        tools: list | None = None,
        tool_choice: str | None = None,
        **kwargs,
    ) -> llm.LLMStream:
        """Process chat through LangGraph and return LLMStream."""
        # TESTING: Return static response to test TTS
        static_response = "Hello! I am your travel assistant. I can hear you and I am working fine. How can I help you plan your trip today?"

        # Update context with static response (content must be a list)
        chat_ctx.items.append(
            llm.ChatMessage(
                role="assistant", content=[{"type": "text", "text": static_response}]
            )
        )

        # Return OpenAI LLM stream to speak the response
        return openai.LLM(model="gpt-4o-mini").chat(
            chat_ctx=chat_ctx, tools=tools, tool_choice=tool_choice, **kwargs
        )


def create_langgraph_adapter():
    """Create the LangGraph LLM adapter."""
    graph = create_graph()
    return LangGraphLLMAdapter(graph)


def create_voice_agent() -> Agent:
    """Create and configure the voice pipeline agent."""
    # TESTING: Use OpenAI directly to test TTS
    return Agent(
        instructions="You are a helpful travel assistant. Always respond with: 'Hello! I am your travel assistant. I can hear you and I am working fine. How can I help you plan your trip today?' - Say only this exact message every time.",
        vad=silero.VAD.load(),
        stt=openai.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),  # Use OpenAI directly for testing
        tts=openai.TTS(),
    )


# Create AgentServer instance
server = AgentServer()


@server.rtc_session(agent_name="travel-assistant")
async def entrypoint(ctx: JobContext):
    """Main entry point for the agent - registered with agent_name."""
    print(f"🔥 Agent received job for room: {ctx.room.name}")

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    print(f"✅ Connected to room!")

    # Create the agent configuration
    agent = Agent(
        instructions="You are a helpful travel assistant. Respond naturally to questions about travel destinations, planning, and recommendations.",
        vad=silero.VAD.load(),
        stt=openai.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(),
    )

    # Create and start session with the agent
    session = AgentSession()

    print("🚀 Starting agent session...")
    await session.start(agent=agent, room=ctx.room)
    print("✅ Session completed!")


if __name__ == "__main__":
    cli.run_app(server)

# ============================================================================
# END OF IMPLEMENTATION
# ============================================================================
"""    
```

---
"""
## Part 6: Running Your Agent

### Connecting to LiveKit
"""
When running your agent, you need:
1. **WebSocket URL**: The LiveKit server URL (from `.env`)
2. **Token**: Generated JWT token for authentication
"""
### Running Commands
"""
```bash
# Start in development mode
python agent.py dev

# Or connect to a specific room
python agent.py connect --room my-room
```
"""
### Using LiveKit Playground
"""
1. Go to [LiveKit Agents Playground](https://agents-playground.livekit.io/)
2. Enter your LiveKit WebSocket URL
3. Generate or enter a token
4. Connect and start talking to your agent!

---
"""
## Part 7: Demo Recording Requirements
"""
You must submit a **screen recording** demonstrating your voice agent working with the LiveKit Playground.
"""
### Steps to Record
"""
1. **Start your agent:**
   ```bash
   python agent.py dev
   ```

2. **Open LiveKit Playground:**
   - Go to [LiveKit Playground](https://agents-playground.livekit.io/)
   - Enter your LiveKit WebSocket URL
   - Connect to the same room your agent is in

3. **Demonstrate voice interaction:**
   - Speak to the agent
   - Show the agent responding with voice
   - Have at least **3 conversation turns**
   - Show that your LangGraph agent is processing the requests
"""
### Recording Requirements
"""
| Requirement | Details |
|-------------|----------|
| Duration | 1-3 minutes |
| Format | MP4, WebM, or MOV |
| Must Show | Playground UI, terminal running agent, audio working |
| File Name | `demo.mp4` (or appropriate extension) |
"""
### Demo Checklist
"""
- [ ] Agent starts without errors
- [ ] Agent connects to LiveKit room via WebSocket URL
- [ ] Playground shows agent as a participant
- [ ] Voice-to-voice interaction works
- [ ] At least 3 successful conversation turns
- [ ] Terminal shows LangGraph agent processing
- [ ] Token authentication is working

---
"""
## Part 8: Grading Criteria
"""
Your submission will be graded on:

| Criteria | Points | Description |
|----------|--------|-------------|
| **Base Tests Pass** | 30 | All base tests pass |
| **Hidden Tests Pass** | 30 | Additional integration tests (not shared) |
| **LangGraph Integration** | 20 | Properly uses LLM adapter to integrate your LangGraph agent |
| **Working Demo** | 20 | Video demonstrates working voice-to-voice interaction |
| **Total** | **100** | |
"""
### Important Notes
"""
1. **Use LLM Adapter Pattern:**
   - You MUST wrap your LangGraph agent in an LLM adapter class
   - The adapter must extend `livekit.agents.llm.LLM`
   - This allows your graph to be used in the voice pipeline

2. **WebSocket URL & Token:**
   - Your agent must properly read `LIVEKIT_URL` from environment
   - Token generation must use `livekit.api.AccessToken`
   - Tokens must include proper room grants

3. **Hidden Tests:**
   - Will test actual agent behavior
   - Will verify LangGraph adapter implementation
   - Will check voice pipeline configuration

4. **Directory Structure:**
   - Must follow the exact structure specified
   - `langgraph_agent.py` must be importable

---
"""

## Part 9: Submission Checklist
"""
Before submitting, verify:
"""
### Required Files
"""
- [ ] `agent.py` - implements all required functions and LLM adapter class
- [ ] `langgraph_agent.py` - your LangGraph agent from previous assignment
- [ ] `requirements.txt` - lists all dependencies including langgraph
- [ ] `.env.example` - shows required environment variables (without actual values)
- [ ] `demo.mp4` - screen recording of working agent
"""
### Code Requirements
"""
- [ ] `get_livekit_url()` returns WebSocket URL from environment
- [ ] `generate_token()` creates valid JWT with room grants
- [ ] LLM adapter class extends `llm.LLM`
- [ ] Adapter implements `async def chat()` method
- [ ] `create_voice_agent()` returns configured VoicePipelineAgent
- [ ] `entrypoint()` is async and connects to room
- [ ] Uses `python-dotenv` for environment variables
- [ ] No hardcoded API keys or secrets
"""
### Demo Requirements
"""
- [ ] Shows agent starting successfully
- [ ] Shows connection to LiveKit playground
- [ ] Demonstrates at least 3 voice conversation turns
- [ ] Shows LangGraph processing in terminal

---
"""
## Helpful Resources

### Documentation
"""
- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [LiveKit Python SDK](https://github.com/livekit/python-sdks)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text)
"""
### Tools
"""
- [LiveKit Agents Playground](https://agents-playground.livekit.io/)
- [LiveKit Cloud](https://cloud.livekit.io)
- [Google AI Studio](https://aistudio.google.com/)
"""
### Troubleshooting
"""
1. **Agent won't connect:**
   - Verify `LIVEKIT_URL` is correct (ws:// or wss://)
   - Check API key and secret are valid
   - Ensure LiveKit server is running

2. **Token errors:**
   - Verify API key and secret match server configuration
   - Check token has not expired
   - Ensure room grants are properly set

3. **No audio:**
   - Check microphone permissions in browser
   - Verify Google API key for STT/TTS
   - Check VAD is properly configured

4. **LangGraph not responding:**
   - Test LangGraph agent standalone first
   - Check adapter properly extracts user message
   - Verify graph invocation is working

---

**Good luck!**
"""
