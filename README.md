# karavan-backend

## Set up
Creating a Virtual environment
```
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

## Install dependencies
```
pip install requests websockets
pip install fastapi uvicorn
pip install aioredis psycopg2 asyncpg
pip install sqlalchemy databases alembic
pip install python-dotenv
```

## Install PostgreSQL
sudo apt install postgresql postgresql-contrib  # Ubuntu/Debian

## Create a new database
```
psql -U postgres
CREATE DATABASE karaoke_db;
CREATE USER karaoke_user WITH PASSWORD 'karaoke_pass';
ALTER ROLE karaoke_user SET client_encoding TO 'utf8';
ALTER ROLE karaoke_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE karaoke_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE karaoke_db TO karaoke_user;
\q
```

## Run the app
```
uvicorn app.main:app --reload
```

## Infrasctructure

karaoke-backend/
│── app/
│   ├── main.py              # FastAPI main app
│   ├── database.py          # Database setup
│   ├── models.py            # Database models
│   ├── crud.py              # DB operations
│   ├── game_manager.py      # Redis-based room management
│   ├── websocket.py         # WebSocket handling
│── .env                     # Config variables
│── requirements.txt         # Installed packages
│── alembic/                 # Migrations
