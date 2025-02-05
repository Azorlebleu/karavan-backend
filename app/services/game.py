from fastapi import WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from ..repository.room import create_room, get_room
from ..repository.chat import get_chat, add_message
from ..repository.game import setup_new_game

from .websocket import active_rooms,  broadcast_event
from ..schemas.room import Room
from ..schemas.chat import Message, NewMessageRequest
from ..schemas.common import BroadcastMessageRequest, SuccessMessage, Text
from ..logger import logger
from ..settings import MAX_PLAYERS, MESSAGE_TYPE_NEW_MESSAGE, MESSAGE_TYPE_GAME_START
import asyncio

game_tasks = {}

async def handle_start_game(room_id: str):
    logger.info(f"Received request to start game for room {room_id}")

    # Conditions
    room = await get_room(room_id)

    # If room does not exist
    if room is None:
        error_message = f"Room {room_id} does not exist"
        logger.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)
    
    # If all players are ready
    if not(all(player.ready for player in room.players)):
        error_message = f"Not all players are ready in room {room_id}"
        logger.info(error_message)
        raise HTTPException(status_code=400, detail=error_message)

    # Initialize the room and the game state
    await setup_new_game(room_id)

    asyncio.create_task(start_game(room_id))

    return SuccessMessage(success=f"Game started in room {room_id}")

async def start_game(room_id: str):
    logger.info(f"Starting game for room {room_id}")
    
    if room_id in active_rooms:
        await broadcast_event(BroadcastMessageRequest(room_id=room_id, type=MESSAGE_TYPE_GAME_START), Text(content="Game started!"))
    else:
        error_message = f"No active websocket for room {room_id} found"
        logger.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)

