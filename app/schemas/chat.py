from pydantic import BaseModel, Field
from typing import Optional, List


class Message(BaseModel):
    content: str
    sender_id: str
    timestamp: Optional[str] = None

class NewMessageRequest(BaseModel):
    message: Message
    room_id: str

class Chat(BaseModel):
    room_id: str
    messages: List[Message]
