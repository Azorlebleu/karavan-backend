from pydantic import BaseModel, Field
from typing import Optional, List


class Message(BaseModel):
    content: str
    sender: str
    timestamp: str

class Chat(BaseModel):
    room_id: str
    messages: List[Message]

class NewMessageRequest(BaseModel):
    room_id: str
    player: str
    content: str