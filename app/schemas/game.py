from pydantic import BaseModel

class CreateRoomRequest(BaseModel):
    player_name: str

class Room(BaseModel):
    room_id: str
    players: list[str]

class JoinRoomRequest(BaseModel):
    player_name: str
    room_id: str