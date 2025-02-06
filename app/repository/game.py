
import os
from dotenv import load_dotenv

from ..logger import logger

from ..schemas.room import Room
from ..schemas.game import Game, GameStatus

from .room import get_room, update_room
from random import shuffle

import aioredis
from typing import Dict, List

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
redis = None
MAX_PLAYERS_PER_ROOM = 5

async def init_redis():
    global redis
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)



async def setup_new_game(room_id: str):
    room: Room = await get_room(room_id)

    player_ids = [player.id for player in room.players]
    shuffle(player_ids)

    room.game.turns = player_ids
    room.room_state = "playing"
    
    await update_room(room)
    
