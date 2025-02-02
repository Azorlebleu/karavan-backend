from pydantic import BaseModel

class SuccessMessage(BaseModel):
    success: str

class BroadcastMessage(BaseModel):
    value: str