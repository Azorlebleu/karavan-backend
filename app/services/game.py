from fastapi import WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from ..repository.room import create_room, get_room
from ..repository.chat import get_chat, add_message
from .websocket import active_rooms,  broadcast_event
from ..schemas.room import Room
from ..schemas.chat import Message, NewMessageRequest
from ..schemas.common import BroadcastMessageRequest, SuccessMessage, Text
from ..logger import logger
from ..settings import MAX_PLAYERS, TYPE_NEW_MESSAGE, TYPE_GAME_START
import asyncio

async def handle_start_game(room_id: str):
    logger.info(f"Received request to start game for room {room_id}")

    # Conditions
    room = await get_room(room_id)

    if room is None:
        error_message = f"Room {room_id} does not exist"
        logger.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)
    
    # If all players are ready
    if not(all(player.ready for player in room.players)):
        error_message = f"Not all players are ready in room {room_id}"
        logger.info(error_message)
        raise HTTPException(status_code=400, detail=error_message)

    asyncio.create_task(start_game(room_id))

    return SuccessMessage(success=f"Game started in room {room_id}")
async def start_game(room_id: str):
    logger.info(f"Starting game for room {room_id}")
    
    if room_id in active_rooms:
        await broadcast_event(BroadcastMessageRequest(room_id=room_id, type=TYPE_GAME_START), Text(content="Game started!"))
    else:
        error_message = f"No active websocket for room {room_id} found"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)


async def get_new_room(player_name: str):
    logger.info(f"Received request to create a new room from player {player_name}")
    room_id = await create_room(player_name)
    logger.debug(f"Created new room with ID: {room_id} for player {player_name}")
    return room_id

async def get_ordered_chat(room_id: str):
    logger.info(f"Received request to get chat for room {room_id}")

    room = await get_room(room_id)
    logger.debug(f"Room {room_id} retrieved successfully")
    
    if room is None:
        error_message = f"Room {room_id} does not exist"
        logger.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)

    logger.debug(f"Retrieving chat for room {room_id}")
    chat = await get_chat(room_id)

    return(chat)

