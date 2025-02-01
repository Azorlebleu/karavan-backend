
import os
from dotenv import load_dotenv
import json
from ..logger import logger
import uuid
from fastapi import HTTPException, FastAPI
from ..schemas.game import Room
from ..schemas.chat import Chat, Message
import aioredis
from datetime import datetime

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
redis = None
MAX_PLAYERS_PER_ROOM = 5

async def init_redis():
    global redis
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def get_chat(room_id: str):
    logger.info(f"Getting chat for room {room_id}")

    chat = await redis.get(f"{room_id}:chat")

    if chat is None:
        error_message = f"No chat found for room {room_id}"
        logger.info(error_message)
        raise HTTPException(status_code=404, detail=error_message)
    chat = Chat.model_validate_json(chat)
    logger.debug(f"Chat retrieved successfully for room {room_id}: {chat}")
    return(chat)

async def send_message(room_id: str, content: str, sender: str):
    chat = await get_chat(room_id)

    message = Message(content=content, sender=sender, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    chat.messages.append(message)

    await redis.set(f"{room_id}:chat", chat.model_dump_json())
    logger.info(f"Message sent successfully to room {room_id} with content: {message}")
    return(True)