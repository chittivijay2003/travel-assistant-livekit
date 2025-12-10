#!/usr/bin/env python3
"""LiveKit Token Generator and Agent Dispatcher

Utility script to:
1. Create or connect to a LiveKit room
2. Dispatch the travel assistant agent to that room
3. Generate an access token for user connection
4. Display instructions for connecting via LiveKit Playground

Usage:
    python3 generate_token.py

The script will:
- Create a room named 'travel-demo-room'
- Dispatch the 'test-assistant-travel' agent
- Generate a 1-hour valid access token
- Print connection instructions for LiveKit Playground

Note:
    Requires LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET
    environment variables to be set in .env file.
"""

import os
import asyncio
from dotenv import load_dotenv
from livekit import api

# Import token generation and URL utilities from agent.py
from agent import generate_token, get_livekit_url

# Load environment variables from .env file
load_dotenv()


async def dispatch_agent_to_room(room_name: str = None):
    """Create room and dispatch agent to handle voice conversations.

    This function:
    1. Creates a new LiveKit room (or uses existing)
    2. Dispatches the travel assistant agent to that room
    3. Returns the room name for token generation

    Args:
        room_name: Optional room name. If None, uses 'travel-demo-room'

    Returns:
        str: The room name where agent was dispatched

    Raises:
        Exception: If room creation or agent dispatch fails

    Note:
        The agent must be running (python agent.py dev) before calling this.
    """
    # Use default room name if not provided
    if room_name is None:
        room_name = "travel-demo-room"

    # Get LiveKit server URL and API credentials
    url = get_livekit_url()
    api_key = os.environ.get("LIVEKIT_API_KEY")
    api_secret = os.environ.get("LIVEKIT_API_SECRET")

    # Create LiveKit API client for room and agent management
    livekit_api = api.LiveKitAPI(url, api_key, api_secret)

    try:
        # Step 1: Create a new room (or use existing room with same name)
        try:
            await livekit_api.room.create_room(api.CreateRoomRequest(name=room_name))
            print(f"✓ Room created: {room_name}")
        except Exception:
            # Room already exists - that's fine, we'll use it
            print(f"✓ Using existing room: {room_name}")

        # Step 2: Dispatch the agent to the room
        # This tells LiveKit to assign our running agent to handle this room
        # The agent_name must match the name registered in agent.py
        await livekit_api.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                room=room_name,
                agent_name="test-assistant-travel",  # Must match @server.rtc_session decorator
            )
        )
        print(f"✓ Agent dispatched to room: {room_name}")

        return room_name  # Return room name for token generation

    except Exception as e:
        print(f"✗ Failed to dispatch agent: {e}")
        raise
    finally:
        # Clean up API client
        await livekit_api.aclose()


def print_playground_instructions(
    room_name: str = None, participant_name: str = "user-1"
):
    """Generate token and display connection instructions for LiveKit Playground.

    This function orchestrates the complete setup process:
    1. Creates/connects to room and dispatches agent
    2. Generates an access token for the user
    3. Prints formatted instructions for connecting via Playground

    Args:
        room_name: Optional room name (default: 'travel-demo-room')
        participant_name: Participant identity (default: 'user-1')

    Returns:
        str: The generated JWT token

    Note:
        The agent server must be running before calling this function.
        Run: python3 agent.py dev
    """
    # Step 1: Create room and dispatch agent
    room_name = asyncio.run(dispatch_agent_to_room(room_name))

    # Step 2: Generate access token for user to join the room
    jwt_token = generate_token(room_name, participant_name)

    # Step 3: Display connection instructions
    print("\n=== LiveKit Playground Configuration ===\n")
    print("1. Go to: https://agents-playground.livekit.io/\n")
    print("2. Enter these details:")
    print(f"   LiveKit URL: {get_livekit_url()}\n")
    print("3. Paste this token:\n")
    print(jwt_token)
    print("\n4. Click 'Connect' and start talking!\n")

    return jwt_token


if __name__ == "__main__":
    print_playground_instructions()
