from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from ..repository.game import create_room, get_room, add_player
from ..schemas.game import Room, JoinRoomRequest
from .websocket import broadcast_event
from typing import Dict, List
from ..logger import logger
from ..settings import MAX_PLAYERS

async def get_new_room(player_name: str):
    logger.info(f"Received request to create a new room from player {player_name}")
    room_id = await create_room(player_name)
    logger.debug(f"Created new room with ID: {room_id} for player {player_name}")
    return room_id

async def join_room(request: JoinRoomRequest):

    logger.info(f"Received request to join room {request.room_id} from player {request.player_name}")
    room: Room = await get_room(request.room_id)
    logger.debug(f"Room state before adding player {request.player_name}: {room}")

    # Conditions for joining the room
    if room is None:
        error_message = f"Room {request.room_id} does not exist."
        logger.info(error_message)
        raise HTTPException(status_code=404, detail=error_message)

    if request.player_name in room.players:
        error_message = f"Player {request.player_name} is already in room {request.room_id}"
        logger.info(error_message)
        raise HTTPException (status_code=400, detail=error_message)
    
    if len(room.players) >= MAX_PLAYERS:
        error_message=f"Room {request.room_id} is full. Cannot join."
        logger.info(error_message)
        raise HTTPException (status_code=400, detail=error_message)
    
    # Add player to the room and store it in the Redis database
    await add_player(request.player_name, request.room_id)
    room = await get_room(request.room_id)

    # Send updated room state to all connected clients
    await broadcast_event(request.room_id, room)

    logger.info(f"Player {request.player_name} joined room {request.room_id} successfully")
    return room
