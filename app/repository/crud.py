from ..models.database import database
from ..models.room import rooms, players

async def create_room(room_id: str, host: str):
    query = rooms.insert().values(room_id=room_id, host=host)
    await database.execute(query)

async def add_player(room_id: str, player_name: str):
    query = players.insert().values(name=player_name, room_id=room_id)
    await database.execute(query)

async def get_players(room_id: str):
    query = players.select().where(players.c.room_id == room_id)
    return await database.fetch_all(query)
