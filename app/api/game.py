from fastapi import APIRouter

from app.services.game import handle_pick_song, handle_start_game

from app.schemas.game import PickSongRequest, StartGameRequest
from app.schemas.common import SuccessMessage

from ..logger import logger

router = APIRouter()

@router.post("/game", response_model=SuccessMessage)
async def start_game_endpoint(request: StartGameRequest):
    
    response: SuccessMessage = await handle_start_game(request.room_id)

    return response

@router.post("/picksong", response_model=SuccessMessage)
async def pick_song_endpoint(request: PickSongRequest):
    
    response: SuccessMessage = await handle_pick_song(request.room_id, request.song_id)

    return response