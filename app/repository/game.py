
import os
from dotenv import load_dotenv
import json
from ..logger import logger
import uuid
from fastapi import HTTPException, FastAPI
from ..schemas.room import Room, Player, PlayerSafe, get_player_safe
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


async def create_room():
    
    room_id = str(uuid.uuid4())  # Generate a unique room ID
    room = Room(room_id=room_id, players=[]).model_dump_json()
    chat = Chat(room_id=room_id, messages=[]).model_dump_json()
    
    await redis.set(f"{room_id}:room", room)
    await redis.set(f"{room_id}:chat", chat)
    logger.info(f"Created room {room_id}")
    return(room_id)

