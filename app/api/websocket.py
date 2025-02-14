from fastapi import APIRouter, WebSocket
from app.services.websocket import room_websocket, websocket_endpoint_test

router = APIRouter()

@router.websocket("/ws/{room_id}/{player_id}")
async def websocket_route(websocket: WebSocket, room_id: str, player_id: str):
    await room_websocket(websocket, room_id, player_id)

@router.websocket("/ws/test")
async def websocket_test_route(websocket: WebSocket):
    await websocket_endpoint_test(websocket)

