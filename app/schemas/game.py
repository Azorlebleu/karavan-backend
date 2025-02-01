from pydantic import BaseModel, Field
from typing import Optional, List
from .chat import Chat

class Room(BaseModel):
    room_id: str
    players: List[str] = Field(default=[])
    host: str

class RoomResponse(BaseModel):
    room: Room

class ErrorResponse(BaseModel):
    error: str
    reason: Optional[str] = None

class JoinRoomRequest(BaseModel):
    player_name: str
    room_id: str
