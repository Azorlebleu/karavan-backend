from fastapi import WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks

from app.services.song import retrieve_lyrics
from ..repository.room import create_room, get_room
from ..repository.chat import get_chat, add_message
from ..repository.game import *

from .websocket import active_rooms_websockets,  broadcast_event
from ..schemas.room import Room
from ..schemas.chat import Message, NewMessageRequest
from ..schemas.common import BroadcastMessageRequest, SuccessMessage, Text
from ..schemas.game import GameTasks, Turn

from ..logger import logger
from ..settings import MESSAGE_TYPE_GAME_START, MESSAGE_TYPE_PHASE_ENDED_PREMATURELY
import asyncio
import copy
import random

all_game_tasks = {}
turn_cancellations = {}

async def handle_start_game(room_id: str):
    logger.info(f"Received request to start game for room {room_id}")

    # Conditions
    room = await get_room(room_id)

    logger.debug(f"Retrieved room: {room}, type: {type(room)}, is None: {room is None}")
    # If room does not exist
    if room is None:
        error_message = f"Error starting the game: room {room_id} does not exist"
        logger.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)
    
    # If all players are ready
    if not(room.are_all_players_ready()):
        error_message = f"Not all players are ready in room {room_id}"
        logger.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)

    # Initialize the room and the game state
    await setup_new_game(room_id)

    # Run the game loop
    task: asyncio.Task = asyncio.create_task(start_game(room_id))
    game_tasks = GameTasks(main=task, round=None)
    all_game_tasks[room_id] = game_tasks

    return SuccessMessage(success=f"Game started in room {room_id}")

async def handle_cancellation_event_registration(room_id):
    # Register or reset the cancellation event for this room

    if room_id not in turn_cancellations:
        turn_cancellations[room_id] = asyncio.Event()
    else:
        turn_cancellations[room_id].clear()

async def start_phase_pick_song(room_id: str, round_number: int, turn_number: int):
    logger.info(f"Picking song for round {round_number} - turn {turn_number} in room {room_id}")

    # Broadcast phase change event
    await broadcast_event(
        BroadcastMessageRequest(room_id=room_id, type="phase_change"),
        Phase(phase="picking_song"),
        debug=True
    )

    # Register or reset the cancellation event for this round
    await handle_cancellation_event_registration(room_id)

    # Retrieve the room for further processing
    room: Room = await get_room(room_id)

    # Retrieve possible songs
    songs: List[Song] = await retrieve_songs()
    logger.debug(f"Got songs for round {round_number}: {songs}")

    # Update song choices in room
    room.game.rounds[round_number][turn_number].song_choices = songs[:]

    # Update game phase in room
    room.game.status = GameStatus(type=GAME_PHASE_PICKING_SONG, detail=None)

    # Update room with new data
    await update_room(room)
    
    # Send the possible songs to the player currently playing
    turn: Turn = room.game.rounds[round_number][turn_number]
    await broadcast_event(
        BroadcastMessageRequest(room_id=room_id, type="pick_song"),
        songs,
        player_id=turn.player_id,
        debug=True
    )

    # Countdown timer
    for timer in range(GAME_CONFIG_PICK_SONG_DURATION, -1, -1):

        # Broadcast the timer event
        try:
            await broadcast_event(
                BroadcastMessageRequest(room_id=room_id, type="timer"),
                TimerMessage(round=round_number, turn=turn_number, remaining_time=timer, current_phase=GAME_PHASE_PICKING_SONG),
                debug=False
            )
        except Exception as e:
            logger.error(f"Error broadcasting timer for room {room_id}: {str(e)}")

        # Wait for 1 second, but exit early if cancellation is triggered
        try:
            await asyncio.wait_for(turn_cancellations[room_id].wait(), timeout=1)

            # Turn was canceled, broadcast the premature turn end message
            logger.info(f"Turn {turn_number} in room {room_id} ended prematurely.")
            await broadcast_event(
                BroadcastMessageRequest(room_id=room.room_id, type=MESSAGE_TYPE_PHASE_ENDED_PREMATURELY),
                Text(content="Picking song phase ended prematurely"),
                debug=True
            )
            return  
        except asyncio.TimeoutError:
            pass  # Continue the countdown if no cancellation
        except Exception as e:
            logger.error(f"Error in start_turn for room {room_id}: {str(e)}")

    # If we reach here, it means the player hasn't chosen any song
    logger.info(f"No song chosen for turn {turn_number} in room {room_id}")
    await broadcast_event(
        BroadcastMessageRequest(room_id=room.room_id, type=MESSAGE_TYPE_NO_SONG_CHOSEN),
        Text(content="No song chosen"),
        debug=True
    )

    # Pick default song choice
    await handle_pick_song(room_id)

    return

    # Cleanup: reset event so next round isn't immediately canceled
    turn_cancellations[room_id].clear()

async def start_phase_guess_song(room_id: str, round_number: int, turn_number: int):
    logger.info(f"Starting round {round_number} in room {room_id}")

    # Broadcast phase change event
    await broadcast_event(
        BroadcastMessageRequest(room_id=room_id, type="phase_change"),
        Phase(phase="guessing_song"),
        debug=True
    )
    # Register or reset the cancellation event for this round
    await handle_cancellation_event_registration(room_id)

    # Retrieve the room for further processing
    room: Room = await get_room(room_id)

    # Update room with new game phase
    room.game.status = GameStatus(type=GAME_PHASE_GUESSING_SONG, detail=None)
    await update_room(room)

    # Countdown timer
    for timer in range(room.game.config.turn_duration, -1, -1):

        # Broadcast the timer event
        try:
            await broadcast_event(
                BroadcastMessageRequest(room_id=room_id, type="timer"),
                TimerMessage(round=round_number, turn=turn_number, remaining_time=timer, current_phase=GAME_PHASE_GUESSING_SONG),
                debug=False
            )
        except Exception as e:
            logger.error(f"Error broadcasting timer for room {room_id}: {str(e)}")

        # Wait for 1 second, but exit early if cancellation is triggered
        try:
            await asyncio.wait_for(turn_cancellations[room_id].wait(), timeout=1)

            # Turn was canceled, broadcast the premature turn end message
            logger.info(f"Turn {turn_number} in room {room_id} ended prematurely.")
            await broadcast_event(
                BroadcastMessageRequest(room_id=room.room_id, type=MESSAGE_TYPE_PHASE_ENDED_PREMATURELY),
                Text(content="Guessing song phase ended prematurely"),
                debug=True
            )
            return  
        except asyncio.TimeoutError:
            pass  # Continue the countdown if no cancellation
        except Exception as e:
            logger.error(f"Error in start_turn for room {room_id}: {str(e)}")

    # Cleanup: reset event so next round isn't immediately canceled
    turn_cancellations[room_id].clear()


async def start_game(room_id: str):
    logger.info(f"Starting game for room {room_id}")
    
    if not room_id in active_rooms_websockets:
        # The room can only start if there is an active websocket
        error_message = f"Can not start game: no active websocket for room {room_id} found"
        logger.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)

    # Game start
    await broadcast_event(BroadcastMessageRequest(room_id=room_id, type=MESSAGE_TYPE_GAME_START), Text(content="Game started!"))

    # Retrieve the room for further processing
    room: Room = await get_room(room_id)

    try:
        # Game Loop over the different rounds
        for round in room.game.rounds:

            for turn in round:

                # Pick a song
                await start_phase_pick_song(room_id, room.game.current_round, room.game.current_turn)

                # Guess the song
                await start_phase_guess_song(room_id, room.game.current_round, room.game.current_turn)

                # Update turn
                await update_turn(room)

            # Update round
            await update_round(room)
            
        logger.info(f"Game loop ended for room {room_id} at round {room.game.current_round}")

    except Exception as e:
        logger.error(f"Error in game loop for room {room_id}: {str(e)}")

#TODO: implement logic
async def handle_guess(room_id: str, message: Message):
    logger.info(f"Received guess from {message.sender_id} in room {room_id} with content {message.content}")

    if message.content == "S3CR3T":
        logger.info(f"Secret word found in room {room_id}")
        turn_cancellations[room_id].set()
        return True
    return(False)

#TODO: implement logic
async def handle_pick_song(room_id: str, song_id: int = None):
    logger.info(f"Handling song picked with id {song_id} in room {room_id}")

    # Retrieve the room for further processing
    room: Room = await get_room(room_id)

    # If room does not exist
    if room is None:
        error_message = f"Room {room_id} does not exist"
        logger.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)
    
    current_round = room.game.current_round
    current_turn = room.game.current_turn

    # Retrieve song choices for the current turn
    songs = room.game.rounds[current_round][current_turn].song_choices

    if song_id:
        # Find songs with matching id in the song choices
        matching_songs: List[Song] = [song for song in songs if song.id == song_id]
        
        # Update the turn data with the song picked
        if matching_songs:
            song = copy.copy(matching_songs[0])
        else: 
            logger.info("No song matches this id")

            # Pick a random song if no matching song is found
            rand =  random.randint(0, len(songs)-1)
            song = copy.copy(songs[rand])
    else:
        # Pick a random song if no id is provided
        rand =  random.randint(0, len(songs)-1)
        song = copy.copy(songs[rand])

    room.game.rounds[current_round][current_turn].song = song
    await update_room(room)

    # Retrieve song lyrics
    try:
        lyrics = await retrieve_lyrics(song.title, song.artist)
        song.lyrics = lyrics
    except Exception as e:
        error_message = f"Error retrieving lyrics of song {song.title} by {song.artist} for room {room_id}"
        logger.error(error_message)
        raise HTTPException(status_code=404, detail=error_message)

    # Send song data only to the singer through websocket
    await broadcast_event(
        BroadcastMessageRequest(room_id=room_id, type=MESSAGE_TYPE_SINGER_SONG_DATA),
        song,
        player_id=room.game.rounds[current_round][current_turn].player_id,
        debug=True
    )

    # Force picking_song phase to end
    turn_cancellations[room_id].set()

    return SuccessMessage(success=f"Song with id {song_id} picked by singer in {room_id}")