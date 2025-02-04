from fastapi import APIRouter, WebSocket
from app.services.websocket import room_websocket, websocket_endpoint_test

router = APIRouter()

@router.websocket("/ws/{room_id}/{player}")
async def websocket_route(websocket: WebSocket, room_id: str, player: str):
    await room_websocket(websocket, room_id, player)

@router.websocket("/ws/test")
async def websocket_test_route(websocket: WebSocket):
    await websocket_endpoint_test(websocket)

