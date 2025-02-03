from fastapi import APIRouter, HTTPException, Request, Response
from app.services.game import get_room_safe, create_room, join_room, handle_player_ready, get_player_safe_by_id, get_player_safe_by_cookie
from app.schemas.game import Room, ErrorResponse, JoinRoomRequest, PlayerReadyRequest, Player, PlayerSafe
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


@router.post("/room/join", response_model=PlayerSafe)
async def join_room_endpoint(request: JoinRoomRequest, response: Response) -> Response:
    """Join an existing room. Sets the player's cookie"""

    data = await join_room(request)
    logger.debug(f"Data: {data}")
    response.set_cookie(key="player_cookie", value=data.cookie, httponly=True, secure=True, samesite="none")

    return data.player

@router.post("/room/ready", response_model=SuccessMessage)
async def set_ready_endpoint(request: PlayerReadyRequest):
    """Set a player as ready"""
    await handle_player_ready(request)
    return SuccessMessage(success="Player ready state stored successfully!")

@router.get("/player/{room_id}/{player_id}", response_model=PlayerSafe)
async def get_player_by_id_endpoint(room_id: str, player_id: str):
    """Get player data by player ID"""
    player_safe = await get_player_safe_by_id(room_id, player_id)
    return player_safe

@router.get("/player/{room_id}", response_model=PlayerSafe)
async def get_player_by_cookie_endpoint(room_id: str, request: Request):
    """Get player data by player ID"""
    player_cookie = request.cookies.get("player_cookie")
    player_safe = await get_player_safe_by_cookie(room_id, player_cookie)
    return player_safe