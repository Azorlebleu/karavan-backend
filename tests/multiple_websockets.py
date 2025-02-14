import asyncio
import websockets
import random as rd
import json

WEBSOCKET_URL = "ws://karavan-back.pedro.elelievre.fr:8000/ws"  
WEBSOCKET_URL = "ws://localhost:8000/ws"  

with open("./room.json") as file:
    room = json.load(file)

room_id = room.get('room_id')

players = room.get('players')



# Function to handle a single WebSocket connection with reconnection logic
async def connect_websocket(player):
    while True:  # Loop to retry on specific error
        try:
            async with websockets.connect(f"{WEBSOCKET_URL}/{room_id}/{player.get('id')}") as websocket:
                print(f"Connection with player {player} established.")
                
                while True:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10)
                        if player == players[0]: print(f"Response to {player.get('name')}: {response}")
                    except asyncio.TimeoutError:
                        pass
                    
                    await asyncio.sleep(0.1)
        
        except websockets.exceptions.ConnectionClosedError as e:
            if e.code == 1012:
                print(f"Service restart detected for player {player.get('name')}. Reconnecting...")
                await asyncio.sleep(5)  # Wait before retrying
            else:
                print(f"Connection with player {player} failed with error code {e.code}: {e.reason}")
                break  # Exit loop for other errors
        except Exception as e:
            print(f"Unexpected error with player {player}: {e}")
            break  # Exit loop on unexpected errors

# Main function to establish multiple WebSocket connections simultaneously
async def main():
    tasks = [connect_websocket(player) for player in players]  # 5 simultaneous connections
    await asyncio.gather(*tasks)

# Run the script
if __name__ == "__main__":
    asyncio.run(main())
