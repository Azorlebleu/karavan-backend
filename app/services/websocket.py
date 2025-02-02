from fastapi import WebSocket, WebSocketDisconnect
from ..repository.game import add_player
from ..schemas.chat import Message, NewMessageRequest
from typing import Dict, List
from ..logger import logger
from fastapi import HTTPException
import json

# Dictionnary to store active rooms and their connections. Each room is associated with a list of WebSocket connections.
active_rooms: Dict[str, List[WebSocket]] = {"b594d6ed-39d5-422e-8cca-1c14e9eca09a": []}

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


async def game_websocket(websocket: WebSocket, room_id: str, player: str):

    logger.info(f"Game WebSocket connected to room {room_id} with player {player}")
    
    if room_id not in active_rooms:
        logger.info(f"Creating new room {room_id}")
        active_rooms[room_id] = []

    await websocket.accept()
    logger.info(f"Adding player {player} to room {room_id}")
    active_rooms[room_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            for connection in active_rooms[room_id]:
                await connection.send_text(f"{player}: {data}")

    except WebSocketDisconnect:
        active_rooms[room_id].remove(websocket)

async def broadcast_event(room_id: str, request):

    logger.debug(f"Triggering request {request} in room {room_id}")

    if room_id not in active_rooms:
        error_message = f"No active websocket for room {room_id} found"
        logger.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)
    
    logger.debug(f"{len(active_rooms[room_id])} players in room {room_id}")

    for connection in active_rooms[room_id]:
        await connection.send_text(request.model_dump_json())

    logger.debug(f"Message broadcasted successfully in room {room_id}")
    return(True)