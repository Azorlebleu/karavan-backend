
import os
from dotenv import load_dotenv

from ..logger import logger

from ..schemas.room import Room
from ..schemas.game import Game, GameStatus, Round

from .room import get_room, update_room
from random import shuffle

import aioredis
from typing import Dict, List

from ..settings import GAME_CONFIG_NUMBER_OF_ROUNDS, GAME_STATUS_PLAYING_ROUND

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
redis = None

async def init_redis():
    global redis
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)



async def setup_new_game(room_id: str):
    room: Room = await get_room(room_id)

    # Randomize player order and assign them to rounds
    player_ids = [player.id for player in room.players]
    shuffle(player_ids)

    rounds: List[Round] = []
    for player_id in player_ids*GAME_CONFIG_NUMBER_OF_ROUNDS:
        round = Round(player_id=player_id)
        rounds.append(round)

    room.game.rounds = rounds
    room.game.status = GameStatus(type=GAME_STATUS_PLAYING_ROUND, detail=None)
    room.room_state = "playing"
    

    
    await update_room(room)
    
