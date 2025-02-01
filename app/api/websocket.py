from fastapi import APIRouter, WebSocket
from app.services.websocket import game_websocket, websocket_endpoint_test, broadcast_event

router = APIRouter()

@router.websocket("/ws/{room_id}/{player}")
async def websocket_route(websocket: WebSocket, room_id: str, player: str):
    await game_websocket(websocket, room_id, player)

@router.websocket("/ws/test")
async def websocket_test_route(websocket: WebSocket):
    await websocket_endpoint_test(websocket)

@router.post("/test/websocket-trigger")
async def trigger_message_endpoint(request: dict):
    """Get a game room by room ID"""
    await broadcast_event(request.get("room_id"), request.get("message"))
