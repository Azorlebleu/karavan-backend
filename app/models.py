from sqlalchemy import Table, Column, Integer, String, ForeignKey
from .database import metadata

games = Table(
    "games",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("room_id", String, unique=True),
    Column("host", String),
)

players = Table(
    "players",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("score", Integer, default=0),
    Column("room_id", String, ForeignKey("games.room_id")),
)
