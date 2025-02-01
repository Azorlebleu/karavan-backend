from fastapi import APIRouter
from app.services.chat import get_ordered_chat
from app.schemas.chat import Chat, NewMessageRequest
from app.schemas.common import SuccessMessage
from app.repository.chat import send_message
from ..logger import logger
router = APIRouter()

@router.get("/chat/{room_id}", response_model=Chat)
async def get_chat_endpoint(room_id: str):

    logger.debug(f"Getting chat for room {room_id}")
    
    chat = await get_ordered_chat(room_id) 
    
    logger.debug(f"Chat retrieved successfully for room {room_id}: {chat}")

    return chat

@router.post("/chat/", response_model=SuccessMessage)
async def send_message_endpoint(request: NewMessageRequest):

    logger.info(f"Sending a chat to {request.room_id} from {request.player} with content: {request.content}")
    
    message_sent = await send_message(request.room_id, request.player, request.content)  
    
    if message_sent:
        logger.debug(f"Message was sent successfully for room {request.room_id}: {request.content}")

    return {"success": "Message sent successfully!"}
