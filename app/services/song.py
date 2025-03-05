import requests
import json

from app.settings import LYRICS_API_URL
from ..logger import logger

async def retrieve_lyrics(title: str, artist: str):
  try:
    response = requests.get(f'{LYRICS_API_URL}/{artist}/{title}')
    response.raise_for_status()
    data = response.text
    lyrics = json.loads(data)['lyrics']
    return lyrics
  except requests.exceptions.HTTPError as errh: 
    logger.error(f'Error while fetching lyrics: {errh.args[0]}')
    raise errh