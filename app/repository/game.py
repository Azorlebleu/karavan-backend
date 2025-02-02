
import os
from dotenv import load_dotenv
import json
from ..logger import logger
import uuid
from fastapi import HTTPException, FastAPI
from ..schemas.game import Room, CreateNewRoomRequest, Player
from ..schemas.chat import Chat
import aioredis
from typing import Dict, List

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
redis = None
MAX_PLAYERS_PER_ROOM = 5

async def init_redis():
    global redis
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def create_room(request: CreateNewRoomRequest):
    
    room_id = str(uuid.uuid4())  # Generate a unique room ID
    room = Room(room_id=room_id, players=[Player(name=request.host)], host=request.host).model_dump_json()
    chat = Chat(room_id=room_id, messages=[]).model_dump_json()
    
    await redis.set(f"{room_id}:room", room)
    await redis.set(f"{room_id}:chat", chat)
    logger.info(f"Creating room {room_id} with player {request.host}")
    return(room_id)

async def get_room(room_id: str):

    logger.info(f"Getting room {room_id}")
    room = await redis.get(f"{room_id}:room")
    
    if room is None:
        error_message = f"Room {room_id} does not exist"
        logger.info(error_message)
        raise HTTPException(status_code=404, detail=error_message)
    logger.debug(f"Room {room_id} retrieved successfully: {room}")

    return(Room.model_validate_json(room))

async def add_player(player_name: str, room_id: str):
    logger.info(f"Adding player {player_name} to room {room_id}")

    room = Room.model_validate_json(await redis.get(f"{room_id}:room"))
    room.players.append(Player(name=player_name))
    await redis.set(f"{room_id}:room", room.model_dump_json())
    
    logger.debug(f"Current players in room {room_id}: {room.players}")
    return(True)

async def get_chat(room_id: str):
    pass

async def update_players(room_id: str, players: List[Player]):
    logger.debug(f"Updating players in room {room_id} with {players}")
    
    room = Room.model_validate_json(await redis.get(f"{room_id}:room"))
    room.players = players
    await redis.set(f"{room_id}:room", room.model_dump_json())
    
    logger.debug(f"Players updated successfully in room {room_id}: {room.players}")
    return(True)