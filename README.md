# karavan-backend

## Run the app
```
cd /KaraVan/karavan-backend
source /venv/bin/activate

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


## Set up
Creating a Virtual environment
```
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```


### Install PostgreSQL
sudo apt install postgresql postgresql-contrib  # Ubuntu/Debian

### Create a new database
```
psql -U postgres
CREATE DATABASE karaoke_db;
CREATE USER karaoke_user WITH PASSWORD 'redacted';
ALTER ROLE karaoke_user SET client_encoding TO 'utf8';
ALTER ROLE karaoke_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE karaoke_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE karaoke_db TO karaoke_user;
\q
```


### Install dependencies
```
# Necessary for psycopg2 on Debian/Ubuntu
sudo apt install python3-dev
sudo apt install libpq-dev 


pip3 install -r requirements.txt
```

