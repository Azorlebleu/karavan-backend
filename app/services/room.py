from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from ..repository.room import create_room, get_room, get_room_safe, add_player, update_players, set_owner, update_room
from ..schemas.room import Room, RoomSafe, JoinRoomRequest, PlayerReadyRequest, PlayerReady, Player, PlayerSafe, get_player_safe, JoinRoomResponse
from ..schemas.common import BroadcastMessage, BroadcastMessageRequest, Text
from ..schemas.game import GameStatus
from .websocket import broadcast_event
from typing import Dict, List
from ..logger import logger
from ..settings import MAX_PLAYERS, MSG_ALL_PLAYERS_READY, MESSAGE_TYPE_ALL_PLAYERS_READY, MESSAGE_TYPE_PLAYER_READY, MESSAGE_TYPE_ROOM_STATE, GAME_STATUS_WAITING_OWNER, GAME_STATUS_WAITING_PLAYERS, MESSAGE_TYPE_WAITING_FOR_PLAYERS
import json

async def get_new_room(player_name: str):
    logger.info(f"Received request to create a new room from player {player_name}")
    room_id = await create_room(player_name)
    logger.debug(f"Created new room with ID: {room_id} for player {player_name}")
    return room_id

async def join_room(request: JoinRoomRequest):
    """Add a new player to a room. Broadcast the updated room state to all connected clients. Return the new user id."""
    logger.info(f"Received request to join room {request.room_id} from player {request.player_name}")

    try: 
        room: Room = await get_room(request.room_id)
        logger.debug(f"Room state before adding player {request.player_name}: {room}")

        # Conditions for joining the room
        if room is None:
            error_message = f"Room {request.room_id} does not exist."
            logger.info(error_message)
            raise HTTPException(status_code=404, detail=error_message)

        if request.player_name in [player.name for player in room.players]:
            error_message = f"Player {request.player_name} is already in room {request.room_id}"
            logger.info(error_message)
            raise HTTPException (status_code=400, detail=error_message)
        
        if len(room.players) >= MAX_PLAYERS:
            error_message=f"Room {request.room_id} is full. Cannot join."
            logger.info(error_message)
            raise HTTPException (status_code=400, detail=error_message)
        
        # Add player to the room and store it in the Redis database
        player: Player = await add_player(request.player_name, request.room_id)

        # If the room has no owner, set the player as the owner
        if not room.owner:
            await set_owner(player.id, request.room_id)

        # Set the game status to WAITING_PLAYERS
        # room.game.status = GameStatus(type=GAME_STATUS_WAITING_PLAYERS)
        room = await get_room(room.room_id)
        room = await handle_players_not_ready(room)
        await update_room(room)
        
        # Send updated room state to all connected clients
        room_safe = await get_room_safe(request.room_id)
        await broadcast_event(BroadcastMessageRequest(room_id=request.room_id, type=MESSAGE_TYPE_ROOM_STATE), room_safe)

        # Retrieve the player safe and its cookie
        player_safe: PlayerSafe = get_player_safe(player)
        cookie: str = player.cookie
        
        logger.info(f"Player {request.player_name} joined room {request.room_id} successfully")
        logger.debug(f"Cookie for player {request.player_name}: {cookie} retrieved successfully")
        return JoinRoomResponse(player=player_safe, cookie=cookie)
    
    except Exception as e:
        logger.error(f"Error joining room: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while joining the room: {e}")

async def handle_player_ready(request: PlayerReadyRequest):
    logger.info(f"Player {request.player_name} is {'ready' if request.ready else 'not ready'} in room {request.room_id}")
    try:
        players = (await get_room(request.room_id)).players
        
        # Conditions for player ready status change
        if request.player_name not in [player.name for player in players]:
            error_message = f"Player {request.player_name} is not in room {request.room_id}"
            logger.info(error_message)
            raise HTTPException(status_code=404, detail=error_message)
        
        # Update player ready status in the room and store it in the Redis database
        player = next((p for p in players if p.name == request.player_name), None)
        if player:
            player.ready = request.ready

        players_updated = await update_players(request.room_id, players)

        if not players_updated:
            error_message = f"Failed to update player {request.player_name}'s ready status in room {request.room_id}"
            logger.info(error_message)
            raise HTTPException(status_code=500, detail=error_message)

        # Retrieve the room for further processing
        room: Room = await get_room(request.room_id)
        

        # Broadast that a player is ready
        await broadcast_event(BroadcastMessageRequest(room_id=request.room_id, type=MESSAGE_TYPE_PLAYER_READY), PlayerReady(player_name=request.player_name, ready=request.ready))


        # If all players are ready, broadcast a "all players ready" event and change the game's state
        players = (await get_room(request.room_id)).players
        if all(player.ready for player in players):
            await broadcast_event(BroadcastMessageRequest(room_id=request.room_id, type=MESSAGE_TYPE_ALL_PLAYERS_READY), "")
            room.game.status = GameStatus(type=GAME_STATUS_WAITING_OWNER)
            logger.info(f"All players in room {request.room_id} are ready")
        
        # If at least one player is not ready, change the game's state to waiting for players
        else:
            room: Room = await handle_players_not_ready(room)
        await update_room(room)

    except Exception as e:
        error_message = f"Error handling player ready status in room {request.room_id}: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)
    
async def get_player_safe_by_id(room_id: str, player_id: str):
    """Get a player from a room safely, without exposing sensitive information."""
    try: 

        room_safe: RoomSafe = await get_room_safe(room_id)
        player_safe = next((p for p in room_safe.players if p.id == player_id), None)
        if not player_safe:
            error_message = f"Player with ID {player_id} not found in room {room_id}"
            logger.info(error_message)
            raise HTTPException(status_code=404, detail=error_message)

        return player_safe

    except Exception as e:
        error_message = f"Error getting player safe information: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)
    

async def get_player_safe_by_cookie(room_id: str, cookie: str):
    """Get a player from a room safely, without exposing sensitive information."""
    try: 

        room: Room = await get_room(room_id)
        player: Player = next((p for p in room.players if p.cookie == cookie), None)
        if not player:
            error_message = f"Player with cookie {cookie} not found in room {room_id}"
            logger.info(error_message)
            raise HTTPException(status_code=404, detail=error_message)

        return player

    except Exception as e:
        error_message = f"Error getting player information: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)
    

async def handle_players_not_ready(room: Room):
    logger.info(f"Not all players in room {room.room_id} are ready")
    waiting_for_players = [player.id for player in room.players if not player.ready]
    room.game.status = GameStatus(type=GAME_STATUS_WAITING_PLAYERS, detail=waiting_for_players)
    await broadcast_event(BroadcastMessageRequest(room_id=room.room_id, type=MESSAGE_TYPE_WAITING_FOR_PLAYERS), json.dumps(waiting_for_players))
    return(room)