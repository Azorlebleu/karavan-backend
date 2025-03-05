import requests
import websockets
import asyncio
import json
import time



# URL of the server
SERVER_URL = "http://127.0.0.1:8000"
WEBSOCKET_URL = "wss://karavan-back.pedro.elelievre.fr/ws"



# Function to test the HTTP server
async def test_http():
    try:
        # Send a GET request to the server API (root URL, change as needed)
        response = requests.get(SERVER_URL)
        
        # Check if the status code is 200 (OK)
        if response.status_code == 200:
            print("HTTP server is running and responded successfully.")
        else:
            print(f"HTTP server responded with status code {response.status_code}.")
    
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while testing HTTP server: {e}")

# Function to test WebSocket connection
async def test_websocket():
    try:
        # Establish WebSocket connection to the server
        async with websockets.connect(f"{WEBSOCKET_URL}/test") as websocket:
            print("WebSocket connection established.")

            # Continuously send ping every 1 second and wait for response
            for _ in range(3):  # Send 10 pings (you can change this count as needed)
                message = {"type": f"Ping... {_}"}
                await websocket.send(json.dumps(message))
                print(f"Ping sent to the server: {message}", end="")

                # Wait for the server's response
                response = await websocket.recv()
                print(f"Received from WebSocket: {response}")

                # Test if the server responded appropriately
                if "pong" in response:
                    print("WebSocket test passed.")
                else:
                    print(f"Unexpected WebSocket response: {response}")
                
                # Wait for 1 second before sending the next ping
                await asyncio.sleep(1)

    except Exception as e:
        print(f"Error occurred while testing WebSocket: {e}")


async def test_room_player():
    try:
        # Variables
        room_id = "123"
        player = "pedro"
        test_pass = True

        # Establish WebSocket connection to the server
        url = f"{WEBSOCKET_URL}/{room_id}/{player}"
        print(url)
        async with websockets.connect(url) as websocket:
            print("WebSocket connection established.")

            # Continuously send ping every 1 second and wait for response
            for _ in range(3):  # Send 10 pings (you can change this count as needed)
                message = {"type": f"Ping... {_}"}
                await websocket.send(json.dumps(message))
                print(f"Ping sent to the server: {message}")

                # Wait for the server's response
                response = await websocket.recv()
                print(f"Received from WebSocket: {response}")

                # Test if the server responded appropriately
                if player in response:
                    pass
                else:
                    print(f"Unexpected WebSocket response: {response}")
                    test_pass = False
                
                # Wait for 1 second before sending the next ping
                await asyncio.sleep(1)
        if test_pass:
            print("WebSocket test passed.")

    except Exception as e:
        print(f"Error occurred while testing WebSocket: {e}")


# Main function to run tests
async def main():
    # Run tests simultaneously
    # await asyncio.gather(test_http(), test_websocket(), test_room_player())

    # Run tests sequentially
    # await test_http()
    await test_websocket()
    # await test_room_player()
    
if __name__ == "__main__":
    asyncio.run(main())
