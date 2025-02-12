
import os
from dotenv import load_dotenv

from ..logger import logger

from ..schemas.room import Room
from ..schemas.game import *
from ..schemas.common import *

from .room import get_room, update_room
from random import shuffle
from ..services.websocket import broadcast_event

import aioredis
from typing import Dict, List

from ..settings import *

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
redis = None

async def init_redis():
    global redis
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)



async def setup_new_game(room_id: str):
    logger.debug(f"Setting up new game for room {room_id}")

    room: Room = await get_room(room_id)

    # Randomize player order and assign them to rounds
    player_ids = [player.id for player in room.players]
    shuffle(player_ids)

    rounds: List[List[Turn]] = []
    logger.debug(f"Number of rounds: {GAME_CONFIG_NUMBER_OF_ROUNDS} and player_ids: {player_ids}")

    for round_number in range(GAME_CONFIG_NUMBER_OF_ROUNDS):
        round: List[Turn] = []
        for player_id in player_ids:
            turn = Turn(player_id=player_id)
            logger.debug(f"Creating turn {turn}")
            round.append(turn)
        rounds.append(round)
        
    logger.debug(f"Setting up rounds in room {room_id}: {rounds}")

    room.game.rounds = rounds
    room.game.status = GameStatus(type=GAME_STATUS_PLAYING_ROUND, detail=None)
    room.room_state = "playing"
    

    
    await update_room(room)
    
async def update_turn(room: Room):
    """Updates the current turn in the game and broadcasts the updated state to all connected clients"""
    
    logger.debug(f"Updating turn for room {room.room_id}")

    room.game.current_turn += 1

    if room.game.current_turn >= len(room.players):
        return
    
    try:
        await broadcast_event(BroadcastMessageRequest(room_id=room.room_id, type=MESSAGE_TYPE_TURN_CHANGE), RoundAndTurnMessage(turn=room.game.current_turn, round=room.game.current_round))
        await update_room(room)
    
    except Exception as e:
        logger.error(f"Error in updating turn for room {room.room_id}: {str(e)}")


async def update_round(room: Room):
    """Updates the current turn in the game and broadcasts the updated state to all connected clients"""
    
    logger.debug(f"Updating round for room {room.room_id}")

    room.game.current_round += 1
    room.game.current_turn = 0

    try:
        await broadcast_event(BroadcastMessageRequest(room_id=room.room_id, type=MESSAGE_TYPE_ROUND_CHANGE), RoundAndTurnMessage(turn=room.game.current_turn, round=room.game.current_round))
        await update_room(room)
    
    except Exception as e:
        logger.error(f"Error in updating turn for room {room.room_id}: {str(e)}")