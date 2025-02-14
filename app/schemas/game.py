from pydantic import BaseModel
from typing import List, Optional, Union, Any, Literal
import asyncio

class Song(BaseModel):
    id: int
    title: str
    artist: str

class Turn(BaseModel):
    player_id: str
    song: Optional[Song] = None
    guessers: Optional[List[str]] = []

class Round(BaseModel):
    turns: List[Turn] = []

class GameStatus(BaseModel):
    type: str
    detail: Optional[Union[str, List[str]]] = None

class GameConfig(BaseModel):
    num_rounds: int
    turn_duration: int # in seconds

class Game(BaseModel):
    status: GameStatus
    config: GameConfig
    current_round: int
    current_turn: int
    rounds: List[List[Turn]]

class StartGameRequest(BaseModel):
    room_id: str

class GameTasks(BaseModel):
    main: Any
    round: Any

class TimerMessage(BaseModel):
    round: int
    turn: int
    remaining_time: int
    current_phase: Literal["picking_song", "guessing_song", "scoreboard"]

class RoundAndTurnMessage(BaseModel):
    round: int
    turn: int

