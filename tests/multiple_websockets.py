import asyncio
import websockets
import random as rd

WEBSOCKET_URL = "ws://127.0.0.1:8000/ws"  
room_id = "c708137b-7317-4856-9fa7-673c5a507587"
players = ["Pedro", "Nhien", "Barbara", "Robi", "Jérôme"]

# Function to handle a single WebSocket connection
async def connect_websocket(player):
    try:
        async with websockets.connect(f"{WEBSOCKET_URL}/{room_id}/{player}") as websocket:
            print(f"Connection with player {player} established.")
            
            # Keep the connection alive by sending a message every 10 seconds
            while True:
                
                # Receive the response from the server
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10)
                    print(f"Response to {player}: {response}")
                except asyncio.TimeoutError:
                    pass
                
                # Delay before sending the next message
                await asyncio.sleep(0.1)
                
    except Exception as e:
        print(f"Connection with player {player} failed with error: {e}")

# Main function to establish multiple WebSocket connections simultaneously
async def main():
    tasks = []
    for player in players:  # 5 simultaneous connections
        tasks.append(connect_websocket(player))
    
    await asyncio.gather(*tasks)

# Run the script
if __name__ == "__main__":
    asyncio.run(main())
