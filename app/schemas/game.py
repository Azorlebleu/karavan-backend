from pydantic import BaseModel
from typing import List, Optional, Union, Any
import asyncio

class Song(BaseModel):
    id: str
    title: str
    artist: str

class Round(BaseModel):
    player_id: str
    song: Optional[Song] = None
    guessers: Optional[List[str]] = []


class GameStatus(BaseModel):
    type: str
    detail: Optional[Union[str, List[str]]] = None

class GameConfig(BaseModel):
    num_rounds: int
    round_duration: int # in seconds

class Game(BaseModel):
    status: GameStatus
    config: GameConfig
    current_round: int
    rounds: List[Round]

class StartGameRequest(BaseModel):
    room_id: str

class GameTasks(BaseModel):
    main: Any
    round: Any