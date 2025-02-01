
import os
from dotenv import load_dotenv
import json
from ..logger import logger
import uuid
from fastapi import HTTPException, FastAPI
from ..schemas.game import Room
from ..schemas.chat import Chat
import aioredis

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
redis = None
MAX_PLAYERS_PER_ROOM = 5

async def init_redis():
    global redis
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def create_room(player_name: str):
    room_id = str(uuid.uuid4())  # Generate a unique room ID
    room = Room(room_id=room_id, players=[player_name], host=player_name).model_dump_json()
    chat = Chat(room_id=room_id, messages=[]).model_dump_json()
    
    await redis.set(f"{room_id}:room", room)
    await redis.set(f"{room_id}:chat", chat)
    logger.info(f"Creating room {room_id} with player {player_name}")
    return(room_id)

async def get_room(room_id: str):

    logger.info(f"Getting room {room_id}")
    room = await redis.get(f"{room_id}:room")
    
    if room is None:
        error_message = f"Room {room_id} does not exist"
        logger.info(error_message)
        raise HTTPException(status_code=404, detail=error_message)
    
    return(Room.model_validate_json(room))

async def add_player(player: str, room_id: str):
    logger.info(f"Adding player {player} to room {room_id}")

    room = Room.model_validate_json(await redis.get(f"{room_id}:room"))
    room.players.append(player)
    await redis.set(f"{room_id}:room", room.model_dump_json())
    
    logger.info(f"Current players in room {room_id}: {room.players}")


async def get_chat(room_id: str):
    pass