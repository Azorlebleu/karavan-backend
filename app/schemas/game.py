from pydantic import BaseModel, Field
from typing import Optional, List, Type, TypeVar, Set
from .chat import Chat


T = TypeVar("T", bound=BaseModel)
def get_player_safe(model: BaseModel, target_model: Type[T], fields: Set[str]) -> T:
    """Extract specific fields from one Pydantic model to create another."""
    return target_model(**model.model_dump(exclude=["cookie"]))

class Player(BaseModel):
    name: str
    id: str
    ready: Optional[bool] = Field(default=False)
    connected: Optional[bool] = Field(default=True)
    cookie: str

class PlayerSafe(BaseModel):
    name: str
    id: str
    ready: Optional[bool] = Field(default=False)
    connected: Optional[bool] = Field(default=True)

class Room(BaseModel):
    room_id: str
    owner: Optional[str] = None
    players: List[Player] = Field(default=[])


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