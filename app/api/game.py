from fastapi import APIRouter, HTTPException
from app.services.game import get_room_safe, create_room, join_room, handle_player_ready
from app.schemas.game import Room, ErrorResponse, JoinRoomRequest, PlayerReadyRequest, Player
from app.schemas.common import SuccessMessage

from ..logger import logger
router = APIRouter()

@router.get("/room/{room_id}", response_model=Room)
async def get_room_endpoint(room_id: str):
    """Get a game room by room ID"""

    room = await get_room_safe(room_id) 
    return room

@router.post("/room", response_model=SuccessMessage)
async def create_room_endpoint():
    """Create a new game room"""

    room_id = await create_room()

    return SuccessMessage(success=room_id)


@router.post("/room/join", response_model=Player)
async def join_room_endpoint(request: JoinRoomRequest):
    """Join an existing room. Returns the player data."""

    player = await join_room(request)

    return player

@router.post("/room/ready", response_model=SuccessMessage)
async def set_ready_endpoint(request: PlayerReadyRequest):
    """Set a player as ready"""
    await handle_player_ready(request)
    return SuccessMessage(success="Player ready state stored successfully!")