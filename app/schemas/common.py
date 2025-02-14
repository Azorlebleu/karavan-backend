from fastapi import WebSocket
from pydantic import BaseModel
from typing import Union, Any

class SuccessMessage(BaseModel):
    success: str

class BroadcastMessage(BaseModel):
    type: str
    content: str

class BroadcastMessageRequest(BaseModel):
    room_id: str
    type: str

class Text(BaseModel):
    content: Union[str,int]

class PlayerWebsocket(BaseModel):
    websocket: Any
    player_id: str