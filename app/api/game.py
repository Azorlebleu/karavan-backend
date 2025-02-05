from fastapi import APIRouter

from app.services.game import handle_start_game

from app.schemas.game import StartGameRequest
from app.schemas.common import SuccessMessage

from ..logger import logger

router = APIRouter()

@router.post("/game", response_model=SuccessMessage)
async def start_game_endpoint(request: StartGameRequest):

    logger.debug(f"Starting the game in room {request.room_id}")
    await handle_start_game(request.room_id)

    return SuccessMessage(success="Game was started successfully!  ")
