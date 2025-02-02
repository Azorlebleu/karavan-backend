from fastapi import APIRouter, HTTPException
from app.services.game import get_room, create_room, join_room
from app.schemas.game import Room, ErrorResponse, JoinRoomRequest, CreateNewRoomRequest
from ..logger import logger
router = APIRouter()

@router.get("/room/{room_id}", response_model=Room)
async def get_room_endpoint(room_id: str):
    """Get a game room by room ID"""

    room = await get_room(room_id) 
    return room

@router.post("/room", response_model=Room)
async def create_room_endpoint(request: CreateNewRoomRequest):
    """Create a new game room"""

    room_id = await create_room(request)
    room = await get_room(room_id)

    return room


@router.post("/room/join", response_model=Room)
async def join_room_endpoint(request: JoinRoomRequest):
    """Join an existing room"""

    room = await join_room(request)

    return room
