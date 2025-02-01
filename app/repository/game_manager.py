import aioredis
import os
from dotenv import load_dotenv
import json
from ..logger import logger
import uuid

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
redis = None
MAX_PLAYERS_PER_ROOM = 5

async def init_redis():
    global redis
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def create_room(player_name: str):
    game_data = json.dumps({"players": [player_name], "scores": {}})
    room_id = str(uuid.uuid4())  # Generate a unique room ID
    logger.info(f"Creating room {room_id} with player {player_name}")
    await redis.set(room_id, game_data)
    return(room_id)

async def get_room(room_id: str):
    logger.info(f"Getting room {room_id}")
    room = await redis.get(room_id)
    if room is None:
        logger.info(f"Room {room_id} does not exist")
        return None
    return(json.loads(room))

async def join_room(room_id: str, player: str):
    logger.info(f"Joining room {room_id} with player {player}")
    room = await redis.get(room_id)
    if room is None:
        logger.info(f"Room {room_id} does not exist")
        return None
    return(json.loads(room))

async def add_player(player: str, room_id: str):
    logger.info(f"Adding player {player} to room {room_id}")

    redis_room = json.loads(await redis.get(room_id))
    redis_room.append(player)
    
    await redis.set(room_id, json.dumps(redis_room))
    redis_room = json.loads(await redis.get(room_id))
    
    logger.info(f"Current players in room {room_id}: {redis_room}")
    return True

