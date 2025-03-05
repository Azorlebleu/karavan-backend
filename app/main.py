from fastapi import FastAPI
from app.models.database import database
from app.repository.room import init_redis as redis_room_init
from app.repository.chat import init_redis as redis_chat_init

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging

from app.api.websocket import router as websocket_router
from app.api.room import router as room_router
from app.api.chat import router as chat_router
from app.api.game import router as game_router

import redis
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os 
from app.logger import logger

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")  # Default to localhost if not set

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Custom Middleware to log request details
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log the details of the incoming request
        logging.info(f"Request Method: {request.method}")
        logging.info(f"Request URL: {request.url}")
        logging.info(f"Request Headers: {request.headers}")
        
        # If there are query parameters, log them too
        if request.query_params:
            logging.info(f"Query Parameters: {request.query_params}")

        # Log the body if needed (but beware it might be consumed)
        body = await request.body()
        if body:
            logging.info(f"Request Body: {body.decode()}")

        # Proceed with the request
        response = await call_next(request)
        
        # Optionally log the response status code
        logging.info(f"Response Status Code: {response.status_code}")
        
        return response

# Add the middleware to the FastAPI app
app.add_middleware(RequestLoggingMiddleware)

# Handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:5173", "http://localhost:5173", "http://karavan.pedro.elelievre.fr", "https://karavan.pedro.elelievre.fr"],  # Replace with your domain 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # await database.connect()
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
