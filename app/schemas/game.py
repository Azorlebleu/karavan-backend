from pydantic import BaseModel, Field
from typing import Optional, List
from .chat import Chat

class Player(BaseModel):
    name: str
    ready: Optional[bool] = Field(default=False)
    connected: Optional[bool] = Field(default=True)

class Room(BaseModel):
    room_id: str
    players: List[Player] = Field(default=[])
    host: str

class RoomResponse(BaseModel):
    room: Room

class ErrorResponse(BaseModel):
    error: str
    reason: Optional[str] = None

class JoinRoomRequest(BaseModel):
    player_name: str
    room_id: str

class CreateNewRoomRequest(BaseModel):
    host: str

class PlayerReadyRequest(BaseModel):
    player_name: str
    room_id: str
    ready: bool

class PlayerReady(BaseModel):
    player_name: str
    ready: bool