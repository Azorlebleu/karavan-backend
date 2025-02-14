
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

    logger.debug(f"Current round: {room.game.current_round}")
    logger.debug(f"Current turn: {room.game.current_round}")

    # Randomize player order and assign them to rounds
    player_ids = [player.id for player in room.players]
    shuffle(player_ids)

    rounds: List[List[Turn]] = []
    logger.debug(f"Number of rounds: {GAME_CONFIG_NUMBER_OF_ROUNDS} and player_ids: {player_ids}")

    # Setup the rounds 
    for round_number in range(GAME_CONFIG_NUMBER_OF_ROUNDS):
        round: List[Turn] = []

        # Set up the turn
        for player_id in player_ids:
            turn = Turn(player_id=player_id)
            logger.debug(f"Creating turn {turn}")
            round.append(turn)

        rounds.append(round)
        
    logger.debug(f"Setting up rounds in room {room_id}: {rounds}")

    room.game.current_round = 0
    room.game.current_turn = 0
    room.game.rounds = rounds
    room.game.status = GameStatus(type=GAME_STATUS_PLAYING_ROUND, detail=None)
    room.room_state = "playing"
    
    await update_room(room)
    
async def update_turn(room: Room):
    """Updates the current turn in the game and broadcasts the updated state to all connected clients"""
    
    logger.debug(f"Updating turn for room {room.room_id}")
    
    try:
        room.game.current_turn += 1

        if room.game.current_turn >= len(room.players):
            return
        
        await broadcast_event(BroadcastMessageRequest(room_id=room.room_id, type=MESSAGE_TYPE_TURN_CHANGE), RoundAndTurnMessage(turn=room.game.current_turn, round=room.game.current_round))
        await update_room(room)
        return
    
    except Exception as e:
        logger.error(f"Error in updating turn for room {room.room_id}: {str(e)}")


async def update_round(room: Room):
    """Updates the current round in the game and broadcasts the updated state to all connected clients"""

    try:

        logger.debug(f"Updating round for room {room.room_id}")
        room.game.current_round += 1
        
        if room.game.current_round >= room.game.config.num_rounds:
            return
        
        room.game.current_turn = 0
        await update_room(room)
        await broadcast_event(BroadcastMessageRequest(room_id=room.room_id, type=MESSAGE_TYPE_ROUND_CHANGE), RoundAndTurnMessage(turn=room.game.current_turn, round=room.game.current_round))

    except Exception as e:
        logger.error(f"Error in updating round for room {room.room_id}: {str(e)}")


async def retrieve_songs():
    """Retrieve 3 songs."""

    song_1 = Song(id=1, title="Ma meilleure ennemie", artist="Stromae & Pomme")
    song_2 = Song(id=2, title="La Quête", artist="Orelsan")
    song_3 = Song(id=3, title="Ophelia", artist="The Lumineers")
    
    songs: List[Song] = [song_1, song_2, song_3]

    return songs