"""LiveKit Voice Agent with LangGraph Integration

This module implements a voice-enabled AI agent using LiveKit's real-time
communication platform integrated with a LangGraph multi-model orchestration
system. The agent handles voice input/output and routes queries through
multiple LLM models based on query complexity.

Key Components:
    - Voice pipeline with VAD, STT, LLM, and TTS
    - LangGraph adapter for multi-model orchestration
    - SimpleLLMStream for streaming responses
    - LiveKit server setup and room management

Author: Assignment D9 - LiveKit Voice Agent
"""

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

# Import LangGraph agent from previous assignment (D8)
from langgraph_agent import create_graph

# Load environment variables from .env file
load_dotenv()


def get_livekit_url() -> str:
    """Retrieve LiveKit WebSocket URL from environment variables.

    Returns:
        str: LiveKit server WebSocket URL (wss://...)

    Raises:
        ValueError: If LIVEKIT_URL environment variable is not set
    """
    url = os.environ.get("LIVEKIT_URL")
    if not url:
        raise ValueError("LIVEKIT_URL environment variable is required")
    return url


def generate_token(room_name: str, participant_name: str) -> str:
    """Generate a JWT access token for LiveKit room authentication.

    Creates a signed JWT token with room access permissions including
    audio/video publishing and subscribing capabilities. Token is valid
    for 1 hour.

    Args:
        room_name: Name of the LiveKit room to grant access to
        participant_name: Unique identifier for the participant

    Returns:
        str: JWT token string for room authentication

    Note:
        Requires LIVEKIT_API_KEY and LIVEKIT_API_SECRET environment variables
    """
    # Retrieve API credentials from environment
    api_key = os.environ.get("LIVEKIT_API_KEY")
    api_secret = os.environ.get("LIVEKIT_API_SECRET")

    # Create access token with API credentials
    token = api.AccessToken(api_key, api_secret)

    # Set participant identity and display name
    token.with_identity(participant_name)
    token.with_name(participant_name)

    # Grant room access permissions
    token.with_grants(
        api.VideoGrants(
            room_join=True,  # Allow joining the room
            room=room_name,  # Specific room name
            can_publish=True,  # Allow publishing audio/video
            can_subscribe=True,  # Allow subscribing to other participants
        )
    )

    # Set token expiration to 1 hour
    token.with_ttl(timedelta(hours=1))

    return token.to_jwt()


class SimpleLLMStream(llm.LLMStream):
    """Custom LLM stream adapter for LangGraph responses.

    This class wraps pre-generated text from LangGraph into a streaming
    format compatible with LiveKit's voice pipeline. It handles the conversion
    of LangGraph responses (which may be strings or lists) into proper
    ChatChunk objects for the TTS system.

    Attributes:
        _text: The pre-generated response text from LangGraph
    """

    def __init__(
        self,
        text: str,
        llm_instance: llm.LLM,
        chat_ctx: llm.ChatContext,
        tools: list | None = None,
        conn_options: dict | None = None,
    ):
        """Initialize the stream with pre-generated text.

        Args:
            text: Response text from LangGraph (string or list)
            llm_instance: Parent LLM instance (LangGraphLLMAdapter)
            chat_ctx: Chat context with conversation history
            tools: Optional tool definitions (unused in this implementation)
            conn_options: Optional connection options
        """
        # Initialize parent LLMStream with required parameters
        super().__init__(
            llm=llm_instance, chat_ctx=chat_ctx, tools=tools, conn_options=conn_options
        )
        # Store the response text for streaming
        self._text = text

    async def _run(self) -> None:
        """Generate and send chat chunks through the event channel.

        This is the required abstract method from LLMStream. It converts
        the pre-generated LangGraph response into a ChatChunk object and
        sends it through the event channel for TTS processing.

        The method handles:
        - List-to-string conversion for LangGraph list responses
        - UUID generation for chunk identification
        - Proper ChatChunk structure with ChoiceDelta
        """
        import uuid

        # Convert text to string format (handle various response types from LangGraph)
        text_content = self._text
        if isinstance(text_content, list):
            # LangGraph sometimes returns lists - join them into a string
            text_content = " ".join(str(item) for item in text_content)
        elif not isinstance(text_content, str):
            # Convert any other type to string
            text_content = str(text_content)

        # Send the response as a single ChatChunk through the event channel
        # This will be picked up by the TTS system for voice synthesis
        self._event_ch.send_nowait(
            llm.ChatChunk(
                id=str(uuid.uuid4()),  # Unique identifier for this chunk
                delta=llm.ChoiceDelta(content=text_content, role="assistant"),
            )
        )

    async def aclose(self) -> None:
        """Close the stream."""
        await super().aclose()


class LangGraphLLMAdapter(llm.LLM):
    """Adapter connecting LangGraph multi-model system to LiveKit voice pipeline.

    This adapter bridges the gap between LiveKit's LLM interface and our
    LangGraph-based multi-model orchestration system. It receives chat contexts
    from the voice pipeline, extracts user messages, routes them through
    LangGraph's model selection logic, and returns streaming responses.

    The adapter ensures compatibility between:
    - LiveKit's expected LLM interface (chat method returning LLMStream)
    - LangGraph's graph-based invoke pattern
    - Multi-model routing (Gemini Flash/Pro selection)

    Attributes:
        graph: TravelAssistantGraph instance for multi-model orchestration
    """

    def __init__(self, graph):
        """Initialize adapter with a LangGraph instance.

        Args:
            graph: TravelAssistantGraph instance from langgraph_agent.py
        """
        super().__init__()
        self.graph = graph

    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        tools: list | None = None,
        tool_choice: str | None = None,
        conn_options: dict | None = None,
        **kwargs,
    ) -> llm.LLMStream:
        """Process user input through LangGraph and return response stream.

        This is the main method called by LiveKit's voice pipeline. It:
        1. Extracts the user's message from the chat context
        2. Routes it through LangGraph's multi-model system
        3. Returns a SimpleLLMStream for TTS processing

        Args:
            chat_ctx: Conversation context containing message history
            tools: Optional tool definitions (not used in this implementation)
            tool_choice: Optional tool selection (not used)
            conn_options: Optional connection options
            **kwargs: Additional arguments (unused)

        Returns:
            SimpleLLMStream: Stream object containing LangGraph's response
        """
        # Extract the most recent user message from chat context
        # We search in reverse order to get the latest message
        user_message = ""
        for item in reversed(chat_ctx.items):
            if item.role == "user":
                # Handle different content formats from LiveKit
                if isinstance(item.content, str):
                    # Simple string content
                    user_message = item.content
                elif isinstance(item.content, list):
                    # Content as list of parts (multimodal format)
                    for part in item.content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            # Extract text from dictionary format
                            user_message = part.get("text", "")
                            break
                        elif isinstance(part, str):
                            # Direct string in list
                            user_message = part
                            break
                    if not user_message:
                        # Fallback: join all string parts
                        user_message = " ".join(
                            str(p) for p in item.content if isinstance(p, str)
                        )
                else:
                    # Fallback: convert to string
                    user_message = str(item.content)
                break

        # Fallback if no user message found in context
        if not user_message:
            user_message = "Hello"

        # Ensure message is a string
        user_message = str(user_message)

        # Route the message through LangGraph for multi-model processing
        # LangGraph will select Gemini Flash or Pro based on query complexity
        print(f"\n🔵 CALLING LANGGRAPH with message: {user_message[:100]}...")
        langgraph_response = self.graph.invoke(user_message)
        print(
            f"🟢 LANGGRAPH RESPONSE (length={len(langgraph_response)}): {langgraph_response[:200]}...\n"
        )

        # Wrap the LangGraph response in a SimpleLLMStream for voice output
        # This stream will be processed by the TTS system
        print("🎤 Creating SimpleLLMStream with LangGraph response...")
        return SimpleLLMStream(langgraph_response, self, chat_ctx, tools, conn_options)


def create_langgraph_adapter():
    """Create and initialize the LangGraph LLM adapter.

    Factory function that creates a TravelAssistantGraph instance
    and wraps it in a LangGraphLLMAdapter for use in the voice pipeline.

    Returns:
        LangGraphLLMAdapter: Configured adapter ready for voice agent
    """
    # Create LangGraph instance with multi-model routing
    graph = create_graph()
    # Wrap in adapter for LiveKit compatibility
    return LangGraphLLMAdapter(graph)


def create_voice_agent() -> Agent:
    """Create and configure the complete voice pipeline agent.

    Assembles the full voice agent with:
    - VAD (Voice Activity Detection): Detects when user is speaking
    - STT (Speech-to-Text): Converts speech to text using OpenAI Whisper
    - LLM: Routes queries through LangGraph multi-model system
    - TTS (Text-to-Speech): Converts responses to speech using OpenAI TTS

    Returns:
        Agent: Configured LiveKit voice agent ready for sessions
    """
    # Create LangGraph adapter for multi-model LLM routing
    langgraph_llm = create_langgraph_adapter()

    # Assemble complete voice pipeline
    return Agent(
        vad=silero.VAD.load(),  # Silero VAD for voice activity detection
        stt=openai.STT(),  # OpenAI Whisper for speech recognition
        llm=langgraph_llm,  # LangGraph multi-model system
        tts=openai.TTS(),  # OpenAI TTS for voice synthesis
        instructions="You are a travel assistant. Keep responses brief and conversational.",
    )


# ============================================================================
# Server Setup and Entry Point
# ============================================================================

# Create the LiveKit AgentServer instance
# This server handles incoming connections and job assignments
server = AgentServer()


@server.rtc_session(agent_name="test-assistant-travel")
async def entrypoint(ctx: JobContext):
    """Main entry point when agent is assigned to a room.

    This function is called by LiveKit when an agent dispatch is created
    for a room. It sets up the voice pipeline and handles the conversation.

    The agent_name "test-assistant-travel" must match the name used when
    dispatching the agent to rooms via the LiveKit API.

    Args:
        ctx: Job context containing room information and connection details
    """
    print(f"🔥 Agent received job for room: {ctx.room.name}")

    # Connect to the LiveKit room (audio only, no video)
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    print(f"✅ Connected to room: {ctx.room.name}")

    # Create the voice agent with full pipeline (VAD -> STT -> LLM -> TTS)
    print("🔧 Creating voice agent...")
    assistant = create_voice_agent()
    print("✓ Voice agent created")

    # Start the agent session to begin handling voice interactions
    session = AgentSession()
    print("🚀 Starting session...")
    await session.start(assistant, room=ctx.room)
    print("✓ Session started")


if __name__ == "__main__":
    # Run the agent server using LiveKit's CLI
    # This handles command line arguments and server lifecycle
    # Usage: python agent.py dev (for development with auto-reload)
    #        python agent.py start (for production)
    cli.run_app(server)
