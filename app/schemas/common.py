from fastapi import WebSocket
from pydantic import BaseModel
from typing import Union, Any, Literal

class SuccessMessage(BaseModel):
    success: str

class BroadcastMessage(BaseModel):
    type: str
    content: str

class BroadcastMessageRequest(BaseModel):
    room_id: str
    type: Literal["waiting_for_players","all_players_ready","new_message","player_ready","room_state","game_start","turn_ended_prematurely","no_song_chosen","round_change","turn_change","phase_change","pick_song","timer","singer_song_data"]

class Text(BaseModel):
    content: Union[str,int]

class PlayerWebsocket(BaseModel):
    websocket: Any
    player_id: str