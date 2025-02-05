from pydantic import BaseModel
from typing import List, Optional, Union


class GameStatus(BaseModel):
    type: str
    detail: Optional[Union[str, List[str]]] = None


class Game(BaseModel):
    status: GameStatus
    current_turn: int
    turns: List[str]

class StartGameRequest(BaseModel):
    room_id: str

