
from fastapi import FastAPI
from app.models.database import database
from app.repository.room import init_redis as redis_room_init
from app.repository.chat import init_redis as redis_chat_init

from fastapi.middleware.cors import CORSMiddleware

from app.api.websocket import router as websocket_router
from app.api.room import router as room_router
from app.api.chat import router as chat_router
from app.api.game import router as game_router

import aioredis
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os 
from app.logger import logger

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")  # Default to localhost if not set

app = FastAPI()

# Handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:5173", "http://localhost:5173", "http://karavan-back.pedro.elelievre.fr", "https://karavan-back.pedro.elelievre.fr"],  # Replace with your domain 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()
    await redis_room_init()
    await redis_chat_init()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Include API routers
app.include_router(websocket_router)
app.include_router(room_router)
app.include_router(chat_router)
app.include_router(game_router)

@app.get("/")
def read_root():
    return {"message": "KaraVan backend is running!"}

