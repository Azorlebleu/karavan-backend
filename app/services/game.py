from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from ..repository.game_manager import create_room, get_room, add_player
from ..schemas.game import *
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
    
    if room is None:
        logger.info(f"Room {room_id} does not exist.")
        raise HTTPException(status_code=404, detail="Room does not exist")

    logger.debug(f"Room state: {room}")
    if player_name in room.get("players"):
        logger.info(f"Player {player_name} is already in room {room_id}")
        raise HTTPException (status_code=400, detail="Player already exists in room")
    
    if len(room.get("players")) >= MAX_PLAYERS:
        logger.info(f"Room {room_id} is full. Cannot join.")
        raise HTTPException (status_code=400, detail="Room is full")
    
    player_added = await add_player(player_name, room_id)

    if player_added:
        logger.info(f"Player {player_name} joined room {room_id}")
        return await get_room(room_id)
    else:
        error_message = f"Failed to add player {player_name} to room {room_id}"
        logger.info(error_message)
        return HTTPException (status_code=400, detail=error_message)