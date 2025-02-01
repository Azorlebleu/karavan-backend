from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from ..repository.game import create_room, get_room
from ..repository.chat import get_chat   
from ..schemas.game import Room
from ..logger import logger
from ..settings import MAX_PLAYERS

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
