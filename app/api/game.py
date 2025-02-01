from fastapi import APIRouter, HTTPException
from app.services.game import get_room, create_room, join_room
from app.schemas.game import Room, ErrorResponse, JoinRoomRequest
from ..logger import logger
router = APIRouter()

@router.get("/room/{room_id}", response_model=Room)
async def get_room_endpoint(room_id: str):
    """Get a game room by room ID"""

    room = await get_room(room_id) 
    return room

@router.put("/room/{player_name}", response_model=Room)
async def create_room_endpoint(player_name: str):
    """Create a new game room"""
    room_id = await create_room(player_name)
    room = await get_room(room_id)

    if not room:
        logger.error(f"Failed to create room for {player_name}")
        raise HTTPException(status_code=400, detail="Failed to create room.")

    # Return the room directly as the response model expects a `Room` object
    return room


@router.post("/room/", response_model=Room)
async def join_room_endpoint(request: JoinRoomRequest):
    """Join an existing room"""

    room = await join_room(request.player_name, request.room_id)
    if "error" in room:
        raise HTTPException(status_code=400, detail=room["reason"])
    return room
