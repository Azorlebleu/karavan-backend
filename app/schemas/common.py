from pydantic import BaseModel
from typing import Union

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