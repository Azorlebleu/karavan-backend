from pydantic import BaseModel
from typing import Optional, List

class SuccessMessage(BaseModel):
    success: str
