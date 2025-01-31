from fastapi import FastAPI, WebSocket
from .database import database
from .game_manager import init_redis
from .websocket import websocket_endpoint, websocket_endpoint_test
from .logger import logger

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()
    await init_redis()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.websocket("/ws/{room_id}/{player}")
async def websocket_route(websocket: WebSocket, room_id: str, player: str):
    await websocket_endpoint(websocket, room_id, player)


@app.websocket("/ws/test")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint_test(websocket)

@app.get("/")
def read_root():
    return {"message": "Karaoke Game Backend Running!"}
