from pydantic import BaseModel
from typing import List, Optional, Union, Any, Literal
import asyncio

class Song(BaseModel):
    id: int
    title: str
    artist: str
    lyrics: Optional[str] = None

class Turn(BaseModel):
    player_id: str
    song: Optional[Song] = None #TODO: hide or store somewhere else
    song_choices: Optional[List[Song]] = [] #TODO: hide or store somewhere else
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

class PickSongRequest(BaseModel):
    room_id: str
    song_id: int

class ChangeGamePhaseMessage(BaseModel):
    phase: Literal["picking_song", "guessing_song", "scoreboard"]

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