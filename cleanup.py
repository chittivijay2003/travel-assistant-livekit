#!/usr/bin/env python3
"""Clean up all LiveKit rooms and dispatches."""

import os
import asyncio
from dotenv import load_dotenv
from livekit import api

load_dotenv()


async def cleanup_all():
    """Delete all rooms and dispatches."""
    url = os.environ.get("LIVEKIT_URL")
    api_key = os.environ.get("LIVEKIT_API_KEY")
    api_secret = os.environ.get("LIVEKIT_API_SECRET")

    livekit_api = api.LiveKitAPI(url, api_key, api_secret)

    try:
        # List all rooms
        print("🔍 Listing all rooms...")
        rooms = await livekit_api.room.list_rooms(api.ListRoomsRequest())

        if not rooms.rooms:
            print("✓ No rooms found")
        else:
            print(f"Found {len(rooms.rooms)} room(s)")

            # Delete each room
            for room in rooms.rooms:
                print(f"🗑️  Deleting room: {room.name}")
                await livekit_api.room.delete_room(
                    api.DeleteRoomRequest(room=room.name)
                )
                print(f"✓ Deleted room: {room.name}")

        # List all dispatches
        print("\n🔍 Listing all dispatches...")
        try:
            dispatches = await livekit_api.agent_dispatch.list_dispatch(
                api.ListAgentDispatchRequest()
            )

            if not dispatches.agent_dispatches:
                print("✓ No dispatches found")
            else:
                print(f"Found {len(dispatches.agent_dispatches)} dispatch(es)")

                # Delete each dispatch
                for dispatch in dispatches.agent_dispatches:
                    print(f"🗑️  Deleting dispatch: {dispatch.id}")
                    await livekit_api.agent_dispatch.delete_dispatch(
                        api.DeleteAgentDispatchRequest(
                            dispatch_id=dispatch.id, room=dispatch.room
                        )
                    )
                    print(f"✓ Deleted dispatch: {dispatch.id}")
        except Exception as e:
            print(f"⚠️  Could not list/delete dispatches: {e}")

        print("\n✅ Cleanup complete!")

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        raise
    finally:
        await livekit_api.aclose()


if __name__ == "__main__":
    asyncio.run(cleanup_all())
