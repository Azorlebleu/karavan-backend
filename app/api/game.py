from fastapi import APIRouter
from ..repository.game_manager import create_room, get_room
from ..services.game import join_room
from ..schemas.game import *
router = APIRouter()

@router.get("/test")
def do_test():
    return {"message": "/test endpoint working!"}


@router.get("/new-room/{player_name}")
async def create_room_endpoint(player_name: str):
    room_id = await create_room(player_name)
    return({"room_id": room_id} if room_id else {"error": "Failed to create room."} )

@router.post("/game/")
async def join_game_endpoint(request: JoinRoomRequest):
    room = await join_room(request.player_name, request.room_id)
    return(room if room else {"error": f"Failed to find room {game_id}"} )