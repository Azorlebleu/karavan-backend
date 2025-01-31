import aioredis
import os
from dotenv import load_dotenv
import json
from .logger import logger

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
redis = None
MAX_PLAYERS_PER_ROOM = 5

async def init_redis():
    global redis
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def create_game(room_id: str):
    game_data = json.dumps({"players": [], "scores": {}})
    await redis.set(room_id, game_data)

async def add_player(room_id: str, player: str):
    logger.info(f"Adding player {player} to room {room_id}")

    redis_room = await redis.get(room_id)

    if redis_room is None:
        logger.info(f"Room does not exist. Creating a new one with ID: {room_id}")
        await redis.set(room_id, json.dumps([]))

    if player in redis_room:
        logger.error(f"Player {player} already exists in the room.")
        return(-1)
    
    if len(redis_room) >= MAX_PLAYERS_PER_ROOM:
        logger.error(f"Room {room_id} is full. Cannot add more players.")
        return(-1)
    
    redis_room = json.loads(await redis.get(room_id))
    redis_room.append(player)
    
    await redis.set(room_id, json.dumps(redis_room))
    redis_room = json.loads(await redis.get(room_id))
    
    logger.info(f"Current players in room {room_id}: {redis_room}")

