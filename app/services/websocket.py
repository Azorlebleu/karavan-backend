from fastapi import WebSocket, WebSocketDisconnect
from ..repository.room import add_player
from ..schemas.chat import Message, NewMessageRequest
from ..schemas.common import BroadcastMessage, BroadcastMessageRequest, PlayerWebsocket
from typing import Dict, List, TypeVar, Generic, Union
from ..logger import logger
from fastapi import HTTPException
import json
from pydantic import BaseModel

# Dictionnary to store active rooms and their connections. Each room is associated with a list of WebSocket connections.
active_rooms_websockets: Dict[str, List[PlayerWebsocket]] = {"b594d6ed-39d5-422e-8cca-1c14e9eca09a": []}

# Define a generic type for Pydantic models
T = TypeVar("T", bound=BaseModel)

async def websocket_endpoint_test(websocket: WebSocket):
    """Test WebSocket endpoint. Used with tests in tests/test_server.py."""

    await websocket.accept()

    logger.info("Test WebSocket connected.")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received data from WebSocket: {data}")
            await websocket.send_text(f"{data} and pong back!")

    except WebSocketDisconnect:
        logger.info("Test WebSocket disconnected")


async def room_websocket(websocket: WebSocket, room_id: str, player_id: str):

    logger.info(f"Room WebSocket connected to room {room_id} with player {player_id}")
    
    # If the room does not exist, create it
    if room_id not in active_rooms_websockets:
        logger.info(f"Creating new room {room_id}")
        active_rooms_websockets[room_id] = []

    await websocket.accept()

    # Creating the player websocket
    player_websocket: PlayerWebsocket = PlayerWebsocket(websocket=websocket, player_id=player_id)
    active_rooms_websockets[room_id].append(player_websocket)

    try:
        while True:
            data = await websocket.receive_text()
            for player_websocket in active_rooms_websockets[room_id]:
                await player_websocket.websocket.send_text(f"{player_id}: {data}")

    except WebSocketDisconnect:
        disconnected_player_websocket = next((pws for pws in active_rooms_websockets[room_id] if pws.websocket == websocket), None)
        active_rooms_websockets[room_id].remove(disconnected_player_websocket)

async def broadcast_event(request: BroadcastMessageRequest, model: Union[T, str], player_id=False, debug=False) -> bool:
    """Broadcast an event to all the players in the room. If player_id is set, then the message will be broadcast only to that player."""
    
    try:
        if debug and player_id: logger.debug(f"Broadcasting event received to a single player {player_id}")

        # Check if the websocket still exists
        if request.room_id not in active_rooms_websockets:
            error_message = f"No active websocket for room {request.room_id} found"
            logger.error(error_message)
            raise HTTPException(status_code=404, detail=error_message)
        
        # Handle formatting for arrays of models
        if isinstance(model, list):
            model = [json.loads(m.model_dump_json()) for m in model]
            model = json.dumps(model)

        # Handle formatting for simple strings vs typed objects
        elif not isinstance(model, str):
            model = model.model_dump_json()

        else: 
            pass

        # Create a nice message object
        json_data = {"type": request.type, "content": json.loads(model)} 
        json_message = json.dumps(json_data)
        message = json_message
        
        # Send the message to everyone
        if not player_id:

            for player_websocket in active_rooms_websockets[request.room_id]:
                await player_websocket.websocket.send_text(message)

            if debug: logger.debug(f"Message broadcasted successfully in room {request.room_id}")
        

        # Send the message to one player
        else:
            player_websocket = next((wsp for wsp in active_rooms_websockets[request.room_id] if wsp.player_id == player_id), None)
            logger.debug(f"{active_rooms_websockets[request.room_id]}")
            
            # If the player_id is found
            if player_websocket:
                await player_websocket.websocket.send_text(message)
                if debug: logger.debug(f"Message broadcasted successfully to player {player_id} in room {request.room_id}")

            else:
                logger.error(f"No player with ID {player_id} found in room {request.room_id}")

        return(True)

    except Exception as e:
        logger.warning(f"Error while broadcasting {model} in room {request.room_id}: {e}")
        return(False)
    
