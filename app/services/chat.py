from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from ..repository.game import create_room, get_room
from ..repository.chat import get_chat, add_message
from .websocket import active_rooms,  broadcast_event
from ..schemas.game import Room
from ..schemas.chat import Message, NewMessageRequest
from ..logger import logger
from ..settings import MAX_PLAYERS
from datetime import datetime


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

async def handle_send_message(request: NewMessageRequest):
    
    logger.info(f"Received message from {request.message.sender} in room {request.room_id}")

    # Conditions
    room = await get_room(request.room_id)

    if room is None:
        error_message = f"Room {request.room_id} does not exist"
        logger.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)

    if request.message.sender not in room.players:
        error_message = f"Player {request.message.sender} is not in room {request.room_id}"
        logger.error(error_message)
        raise HTTPException(status_code=403, detail=error_message)
    
    # Compute the timestamp here for consistency
    request.message.timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add the message to Redis for further storage
    message_stored_redis = await add_message(request)
    if message_stored_redis:
        logger.debug(f"Message from {request.message.sender} in room {request.room_id} has been stored in Redis")

    # Send the message to all connected clients in the room
    message_brodcast_websocket = await broadcast_event(request.room_id, request.message)
    if message_brodcast_websocket:
        logger.debug(f"Message from {request.message.sender} in room {request.room_id} has been broadcasted to all clients")

    if message_stored_redis and message_brodcast_websocket:
        return True