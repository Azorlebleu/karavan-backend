import aioredis
import os
from dotenv import load_dotenv
import json

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
redis = None

async def init_redis():
    global redis
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def create_game(room_id: str):
    game_data = json.dumps({"players": [], "scores": {}})
    await redis.set(room_id, game_data)

async def add_player(room_id: str, player: str):
    game = json.loads(await redis.get(room_id))
    game["players"].append(player)
    await redis.set(room_id, json.dumps(game))
