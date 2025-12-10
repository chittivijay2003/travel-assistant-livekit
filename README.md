# Travel Assistant - LiveKit Voice Agent

A real-time voice AI agent built with LiveKit that provides travel assistance through natural voice conversations. The agent uses multi-model LLM orchestration with Google Gemini 2.5 Flash and Pro models to intelligently route queries based on complexity.

## 🎯 Features

- **Real-time Voice Communication**: Full-duplex voice conversations using LiveKit's WebRTC infrastructure
- **Multi-Model Intelligence**: Automatic routing between Gemini 2.5 Flash (fast responses) and Gemini 2.5 Pro (complex reasoning)
- **Voice Pipeline**:
  - Voice Activity Detection (VAD) using Silero
  - Speech-to-Text (STT) using OpenAI Whisper
  - Multi-model LLM routing via LangGraph
  - Text-to-Speech (TTS) using OpenAI TTS
- **Travel Domain Expertise**: Specialized for travel-related queries, bookings, and recommendations

## 🏗️ Architecture

```
User Voice Input
    ↓
[Silero VAD] - Detects when user is speaking
    ↓
[OpenAI Whisper STT] - Converts speech to text
    ↓
[LangGraph Multi-Model Router]
    ├─→ Gemini 2.5 Flash (simple queries)
    └─→ Gemini 2.5 Pro (complex queries)
    ↓
[OpenAI TTS] - Converts response to speech
    ↓
User Voice Output
```

## 📋 Prerequisites

- Python 3.13+
- LiveKit Cloud account ([sign up here](https://cloud.livekit.io/))
- Google AI Studio API key ([get key here](https://aistudio.google.com/app/apikey))

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/chittivijay2003/travel-assistant-livekit.git
cd travel-assistant-livekit

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required environment variables:
```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
GOOGLE_API_KEY=your_google_api_key
```

### 3. Run the Agent

```bash
# Start the agent server in development mode
python3 agent.py dev

# In another terminal, generate a connection token
python3 generate_token.py
```

### 4. Connect via Playground

1. Go to [LiveKit Playground](https://agents-playground.livekit.io/)
2. Enter your LiveKit URL
3. Paste the generated token
4. Click "Connect" and start talking!

## 🗣️ Example Queries

### Simple Queries (Gemini 2.5 Flash)
- "What is the currency in Thailand?"
- "What language do they speak in Brazil?"
- "What is the best season to visit Paris?"

### Complex Queries (Gemini 2.5 Pro)
- "Compare traveling to Bali versus Maldives for a honeymoon"
- "Explain step by step how to plan a budget backpacking trip through Europe"
- "Analyze the pros and cons of booking flights early versus last minute"

## 📁 Project Structure

```
travel-assistant-livekit/
├── agent.py                 # Main LiveKit agent with voice pipeline
├── langgraph_agent.py       # Multi-model LLM routing logic
├── generate_token.py        # Token generation and room dispatch
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔧 Development

### Project Dependencies

Core packages:
- `livekit-agents` - LiveKit agents framework
- `livekit-plugins-openai` - OpenAI STT/TTS integration
- `livekit-plugins-silero` - Silero VAD integration
- `langchain-google-genai` - Google Gemini LLM integration
- `python-dotenv` - Environment variable management

### Running in Production

```bash
# Start agent in production mode
python3 agent.py start

# Generate token for specific room
python3 generate_token.py
```

### Code Structure

**agent.py** - Main components:
- `SimpleLLMStream`: Custom stream adapter for LangGraph responses
- `LangGraphLLMAdapter`: Bridges LangGraph with LiveKit LLM interface
- `create_voice_agent()`: Assembles complete voice pipeline
- `entrypoint()`: Handles room connections and agent sessions

**langgraph_agent.py** - Multi-model routing:
- `setup_models()`: Initializes Gemini models
- Query classification functions (simple, complex, technical, creative)
- `route_query()`: Selects optimal model based on query type
- `TravelAssistantGraph`: Main graph interface for LiveKit

## 🐛 Troubleshooting

### Agent not connecting
- Verify LiveKit credentials in `.env`
- Check that agent is running (`python3 agent.py dev`)
- Ensure room is created before connecting

### No voice output
- Check OpenAI API quota/limits
- Verify microphone permissions in browser
- Check browser console for WebRTC errors

### Model routing issues
- Check Google API key is valid
- Verify internet connectivity
- Check logs for model selection (🤖 MODEL ROUTING messages)

## 📝 License

This project is part of Assignment D9 - LiveKit Voice Agent.

## 🤝 Contributing

This is an educational project. For issues or questions, please contact the repository owner.

## 🔗 Resources

- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit Agents SDK](https://docs.livekit.io/agents/)
- [Google Gemini API](https://ai.google.dev/)
- [OpenAI API](https://platform.openai.com/docs/)

---

**Built with ❤️ using LiveKit, LangGraph, and Google Gemini**
