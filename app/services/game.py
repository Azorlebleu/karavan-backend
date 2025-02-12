from fastapi import WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from ..repository.room import create_room, get_room
from ..repository.chat import get_chat, add_message
from ..repository.game import *

from .websocket import active_rooms,  broadcast_event
from ..schemas.room import Room
from ..schemas.chat import Message, NewMessageRequest
from ..schemas.common import BroadcastMessageRequest, SuccessMessage, Text
from ..schemas.game import GameTasks, Turn

from ..logger import logger
from ..settings import MESSAGE_TYPE_GAME_START, MESSAGE_TYPE_ROUND_ENDED_PREMATURELY
import asyncio

all_game_tasks = {}
turn_cancellations = {}

async def handle_start_game(room_id: str):
    logger.info(f"Received request to start game for room {room_id}")

    # Conditions
    room = await get_room(room_id)

    # If room does not exist
    if room is None:
        error_message = f"Room {room_id} does not exist"
        logger.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)
    
    # If all players are ready
    if not(all(player.ready for player in room.players)):
        error_message = f"Not all players are ready in room {room_id}"
        logger.info(error_message)
        raise HTTPException(status_code=400, detail=error_message)

    # Initialize the room and the game state
    await setup_new_game(room_id)

    # Run the game loop
    task: asyncio.Task = asyncio.create_task(start_game(room_id))
    game_tasks = GameTasks(main=task, round=None)
    all_game_tasks[room_id] = game_tasks

    return SuccessMessage(success=f"Game started in room {room_id}")

async def start_turn(room_id: str, round_number: int, turn_number: int):
    logger.info(f"Starting round {round_number} in room {room_id}")

    # Register cancellation event for this round
    if room_id not in turn_cancellations:
        turn_cancellations[room_id] = asyncio.Event()
    else:
        turn_cancellations[room_id].clear()  # Reset if it was previously set

    # Retrieve the room for further processing
    room: Room = await get_room(room_id)

    # Countdown timer from 10 to 0
    for timer in range(5, -1, -1):
        if turn_cancellations[room_id].is_set():
            logger.info(f"Round {round_number} in room {room_id} ended prematurely.")
            await broadcast_event(
                BroadcastMessageRequest(room_id=room.room_id, type=MESSAGE_TYPE_ROUND_ENDED_PREMATURELY),
                Text(content="Round ended prematurely")
            )
            return 

        await broadcast_event(
            BroadcastMessageRequest(room_id=room_id, type="timer"),
            Text(content=f"Round {round_number} | Turn {turn_number} | Timer {timer}")
        )

        # Wait for 1 second, but stop immediately if the event is set
        try:
            await asyncio.wait_for(turn_cancellations[room_id].wait(), timeout=1)
            logger.info(f"Round {round_number} in room {room_id} was cancelled.")
            await broadcast_event(
                BroadcastMessageRequest(room_id=room.id, type=MESSAGE_TYPE_ROUND_ENDED_PREMATURELY),
                Text(content="Round ended prematurely")
            )
            return  # << Return instead of breaking
        except asyncio.TimeoutError:
            pass  # Timeout just means we continue the loop
        except Exception as e:
            logger.error(f"Error in start_round for room {room_id}: {str(e)}")

    # Cleanup: reset event so next round isn't immediately canceled
    turn_cancellations[room_id].clear()

async def start_game(room_id: str):
    logger.info(f"Starting game for room {room_id}")
    
    if not room_id in active_rooms:
        # The room can only start if there is an active websocket
        error_message = f"Can not start game: no active websocket for room {room_id} found"
        logger.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)

    # Game start
    await broadcast_event(BroadcastMessageRequest(room_id=room_id, type=MESSAGE_TYPE_GAME_START), Text(content="Game started!"))

    # Retrieve the room for further processing
    room: Room = await get_room(room_id)
    logger.debug(f"Game loop started for room {room_id}: {room}")
    logger.debug(f"All game tasks: {all_game_tasks}")

    # Game Loop over the different rounds
    for round in room.game.rounds:
        
        for turn in round:
            # The turn starts
            await start_turn(room_id, room.game.current_round, room.game.current_turn)

            # Update turn
            await update_turn(room)

        # Update round
        await update_round(round)
        
    logger.info(f"Game loop ended for room {room_id} at round {room.game.current_round}")

        
async def handle_guess(room_id: str, message: Message):
    logger.info(f"Received guess from {message.sender_id} in room {room_id} with content {message.content}")

    if message.content == "S3CR3T":
        logger.info(f"Secret word found in room {room_id}")
        turn_cancellations[room_id].set()
        return True
    return(True)