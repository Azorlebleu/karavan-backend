
from fastapi import FastAPI
from app.models.database import database
from app.repository.game import init_redis as redis_game_init
from app.repository.chat import init_redis as redis_chat_init

from fastapi.middleware.cors import CORSMiddleware
from app.api.websocket import router as websocket_router
from app.api.game import router as game_router
from app.api.chat import router as chat_router
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
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a Redis client
async def get_redis():
    return await aioredis.from_url(REDIS_URL, decode_responses=True)


@app.on_event("startup")
async def startup():
    await database.connect()
    await redis_game_init()
    await redis_chat_init()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Include API routers
app.include_router(websocket_router)
app.include_router(game_router)
app.include_router(chat_router)

@app.get("/")
def read_root():
    return {"message": "KaraVan backend is running!"}

