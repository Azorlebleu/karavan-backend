from fastapi import FastAPI
from app.models.database import database
from app.repository.game_manager import init_redis
from app.api.websocket import router as websocket_router
from app.api.game import router as game_router

from app.logger import logger

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()
    await init_redis()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Include API routers
app.include_router(websocket_router)
app.include_router(game_router)

@app.get("/")
def read_root():
    return {"message": "Karaoke Game Backend Running!"}
