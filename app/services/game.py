from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from ..repository.game import create_room, get_room, add_player
from ..schemas.game import Room
from typing import Dict, List
from ..logger import logger
from ..settings import MAX_PLAYERS

async def get_new_room(player_name: str):
    logger.info(f"Received request to create a new room from player {player_name}")
    room_id = await create_room(player_name)
    logger.debug(f"Created new room with ID: {room_id} for player {player_name}")
    return room_id

async def join_room(player_name: str, room_id: str):
    logger.info(f"Received request to join room {room_id} from player {player_name}")
    room: Room = await get_room(room_id)
    logger.debug(f"Room state before adding player {player_name}: {room}")

    # Conditions for joining the room
    if room is None:
        error_message = f"Room {room_id} does not exist."
        logger.info(error_message)
        raise HTTPException(status_code=404, detail=error_message)

    if player_name in room.players:
        error_message = f"Player {player_name} is already in room {room_id}"
        logger.info(error_message)
        raise HTTPException (status_code=400, detail=error_message)
    
    if len(room.players) >= MAX_PLAYERS:
        error_message=f"Room {room_id} is full. Cannot join."
        logger.info(error_message)
        raise HTTPException (status_code=400, detail=error_message)
    
    await add_player(player_name, room_id)


    logger.info(f"Player {player_name} joined room {room_id} successfully")
    return await get_room(room_id)
