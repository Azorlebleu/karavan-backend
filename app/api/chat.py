from fastapi import APIRouter, HTTPException
from app.services.chat import get_ordered_chat, handle_send_message
from app.schemas.chat import Chat, NewMessageRequest
from app.schemas.common import SuccessMessage
from app.repository.chat import add_message
from ..logger import logger
router = APIRouter()

@router.get("/chat/{room_id}", response_model=Chat)
async def get_chat_endpoint(room_id: str):

    logger.debug(f"Getting chat for room {room_id}")
    
    chat = await get_ordered_chat(room_id) 
    
    logger.debug(f"Chat retrieved successfully for room {room_id}: {chat}")

    return chat

@router.post("/chat", response_model=SuccessMessage)
async def send_message_endpoint(request: NewMessageRequest):

    message_sent = await handle_send_message(request)  
    
    if not message_sent:
        raise HTTPException(status_code=400, detail="Failed to send message")

    return SuccessMessage(success="Message sent successfully!")
