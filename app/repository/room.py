
import os
from dotenv import load_dotenv
import json
from ..logger import logger
import uuid
from fastapi import HTTPException, FastAPI
from ..schemas.room import Room, Player, PlayerSafe, get_player_safe
from ..schemas.chat import Chat
from ..schemas.game import Game, GameStatus
import aioredis
from typing import Dict, List
from ..settings import GAME_STATUS_INITIALIZED

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
redis = None

async def init_redis():
    global redis
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def create_room():
    
    room_id = str(uuid.uuid4())  # Generate a unique room ID
    game: Game = Game(status=GameStatus(type=GAME_STATUS_INITIALIZED), current_turn=0, turns=[])
    
    room = Room(room_id=room_id, players=[], game=game).model_dump_json()
    chat = Chat(room_id=room_id, messages=[]).model_dump_json()
    
    await redis.set(f"{room_id}:room", room)
    await redis.set(f"{room_id}:chat", chat)
    logger.info(f"Created room {room_id}")
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

async def set_owner(player_id: str, room_id: str):

    try:
        logger.info(f"Setting owner for room {room_id} to {player_id}")
        tmp_room = await redis.get(f"{room_id}:room")
        logger.debug(f"Temporary room state: {tmp_room} in room {room_id} before setting owner")
        room = Room.model_validate_json(tmp_room)
        room.owner = player_id
        await redis.set(f"{room_id}:room", room.model_dump_json())
        
        logger.info(f"Owner set successfully for room {room_id}")
        return(True)
    
    except Exception as e:
        error_message = f"Error setting owner {player_id} for room {room_id}: {e}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)


async def get_room_safe(room_id: str):
    room = await get_room(room_id)
    players_safe: List[PlayerSafe] = []
    for player in room.players:
        player_safe: PlayerSafe = get_player_safe(player)
        players_safe.append(player_safe)
    room.players = players_safe
    return room

async def add_player(player_name: str, room_id: str):
    logger.info(f"Adding player {player_name} to room {room_id}")

    player_id = str(uuid.uuid4())
    player_cookie = str(uuid.uuid4())
    player = Player(name=player_name, id=player_id, cookie=player_cookie)

    room = Room.model_validate_json(await redis.get(f"{room_id}:room"))
    room.players.append(player)
    await redis.set(f"{room_id}:room", room.model_dump_json())
    
    logger.debug(f"Current players in room {room_id}: {room.players}")
    return(player)

async def get_chat(room_id: str):
    pass

async def update_players(room_id: str, players: List[Player]):
    logger.debug(f"Updating players in room {room_id} with {players}")
    
    room = Room.model_validate_json(await redis.get(f"{room_id}:room"))
    room.players = players
    await redis.set(f"{room_id}:room", room.model_dump_json())
    
    logger.debug(f"Players updated successfully in room {room_id}: {room.players}")
    return(True)

async def update_room(room: Room):
    try:

        logger.debug(f"Updating room {room.room_id} with {room}")

        await redis.set(f"{room.room_id}:room", room.model_dump_json())
        
        logger.debug(f"Room updated successfully in room {room.room_id}")
    
    except Exception as e:
        error_message = f"Error updating room {room.room_id}: {e}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)