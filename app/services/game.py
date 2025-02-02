from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from ..repository.game import create_room, get_room, add_player, update_players
from ..schemas.game import Room, JoinRoomRequest, PlayerReadyRequest, PlayerReady
from ..schemas.common import BroadcastMessage
from .websocket import broadcast_event
from typing import Dict, List
from ..logger import logger
from ..settings import MAX_PLAYERS, MSG_ALL_PLAYERS_READY

async def get_new_room(player_name: str):
    logger.info(f"Received request to create a new room from player {player_name}")
    room_id = await create_room(player_name)
    logger.debug(f"Created new room with ID: {room_id} for player {player_name}")
    return room_id

async def join_room(request: JoinRoomRequest):

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
        await add_player(request.player_name, request.room_id)

        # Send updated room state to all connected clients
        room = await get_room(request.room_id)
        await broadcast_event(request.room_id, room)

        logger.info(f"Player {request.player_name} joined room {request.room_id} successfully")
        return room
    
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
        
        # Broadast that a player is ready
        await broadcast_event(request.room_id, PlayerReady(player_name=request.player_name, ready=request.ready))

        # If all players are ready, broadcast a "all players ready" event
        players = (await get_room(request.room_id)).players
        if all(player.ready for player in players):
            await broadcast_event(request.room_id, BroadcastMessage(value=MSG_ALL_PLAYERS_READY))
            logger.info(f"All players in room {request.room_id} are ready")

    except Exception as e:
        logger.error(f"Error handling player ready status in room {request.room_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while handling player ready status: {e}")