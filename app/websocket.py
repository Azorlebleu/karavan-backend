from fastapi import WebSocket, WebSocketDisconnect
from .game_manager import add_player
from typing import Dict, List
from .logger import logger

active_rooms: Dict[str, List[WebSocket]] = {}

async def websocket_endpoint(websocket: WebSocket, room_id: str, player: str):

    await websocket.accept()

    if room_id not in active_rooms:
        logger.info(f"Room {room_id} not found. Creating new room.")
        active_rooms[room_id] = []

    active_rooms[room_id].append(websocket)

    await add_player(room_id, player)


    try:
        while True:
            data = await websocket.receive_text()
            for connection in active_rooms[room_id]:
                await connection.send_text(f"{player}: {data}")

    except WebSocketDisconnect:
        active_rooms[room_id].remove(websocket)


async def websocket_endpoint_test(websocket: WebSocket):
    await websocket.accept()

    logger.info("Test WebSocket connected.")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received data from WebSocket: {data}")
            await websocket.send_text(f"{data} and pong back!")


    except WebSocketDisconnect:
        logger.info("Test WebSocket disconnected.")