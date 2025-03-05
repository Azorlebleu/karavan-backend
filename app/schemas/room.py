from pydantic import BaseModel, Field
from typing import Optional, List, Type, TypeVar, Set, Union, Literal
from .chat import Chat
from .game import Game
from fastapi import HTTPException
from ..logger import logger

class PlayerSafe(BaseModel):
    name: str
    id: str
    ready: Optional[bool] = Field(default=False)
    connected: Optional[bool] = Field(default=True)
    score: Optional[int] = Field(default=0)

class Player(PlayerSafe):
    cookie: str

class JoinRoomResponse(BaseModel):
    cookie: str
    player: PlayerSafe


def get_player_safe(player: Player) -> PlayerSafe:
    """Extract specific fields from one Pydantic model to create another."""
    return PlayerSafe(**player.model_dump(exclude=["cookie"]))


class Room(BaseModel):
    room_id: str
    owner: Optional[str] = None
    players: List[PlayerSafe] = Field(default=[])
    game: Optional[Game] = None
    room_state: Literal["waiting", "playing", "finished"]

    def are_all_players_ready(self):
        if all(player.ready for player in self.players): return True
        return False

class RoomSafe(BaseModel):
    room_id: str
    owner: Optional[str] = None
    players_safe: List[PlayerSafe] = Field(default=[])
    state: str

class RoomResponse(BaseModel):
    room: Room

class ErrorResponse(BaseModel):
    error: str
    reason: Optional[str] = None

class JoinRoomRequest(BaseModel):
    player_name: str
    room_id: str

class PlayerReadyRequest(BaseModel):
    player_name: str
    room_id: str
    ready: bool

class PlayerReady(BaseModel):
    player_name: str
    ready: bool