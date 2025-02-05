from pydantic import BaseModel, Field
from typing import Optional, List, Type, TypeVar, Set
from .chat import Chat
from .game import Game

class Player(BaseModel):
    name: str
    id: str
    ready: Optional[bool] = Field(default=False)
    connected: Optional[bool] = Field(default=True)
    cookie: str
    score: Optional[int] = Field(default=0)

class PlayerSafe(BaseModel):
    name: str
    id: str
    ready: Optional[bool] = Field(default=False)
    connected: Optional[bool] = Field(default=True)
    score: Optional[int] = Field(default=0)


class JoinRoomResponse(BaseModel):
    cookie: str
    player: PlayerSafe


def get_player_safe(player: Player) -> PlayerSafe:
    """Extract specific fields from one Pydantic model to create another."""
    return PlayerSafe(**player.model_dump(exclude=["cookie"]))


class Room(BaseModel):
    room_id: str
    owner: Optional[str] = None
    players: List[Player] = Field(default=[])
    game: Optional[Game] = None

class RoomSafe(BaseModel):
    room_id: str
    owner: Optional[str] = None
    players_safe: List[PlayerSafe] = Field(default=[])

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