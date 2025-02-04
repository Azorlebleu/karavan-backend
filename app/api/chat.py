from fastapi import APIRouter, HTTPException

from app.services.chat import get_ordered_chat, handle_send_message

from app.schemas.chat import Chat, NewMessageRequest
from app.schemas.common import SuccessMessage

from ..logger import logger

router = APIRouter()

@router.get("/chat/{room_id}", response_model=Chat)
async def get_chat_endpoint(room_id: str):

    logger.debug(f"Getting chat for room {room_id}")
    
    chat = await get_ordered_chat(room_id) 
    

    return chat

@router.post("/chat", response_model=SuccessMessage)
async def send_message_endpoint(request: NewMessageRequest):

    logger.debug(f"Sending message to room {request.room_id} from {request.message.sender} with content: {request.message.content}")
    await handle_send_message(request)  

    return SuccessMessage(success="Message sent successfully!")
