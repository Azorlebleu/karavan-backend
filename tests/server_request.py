import requests
import websockets
import asyncio
import json

# Variables
room_id = "test_room"
player  = "pedro"

# URL of the server
SERVER_URL = "http://127.0.0.1:8000"
WEBSOCKET_URL = "ws://127.0.0.1:8000/ws/test"

async def test_websocket():
    try:
        # Establish WebSocket connection to the server
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print("WebSocket connection established.")

            # Send a message to the server (you can replace with your own message)
            message = {"type": "ping"}
            await websocket.send(json.dumps(message))
            print("Message sent to the server.")

            # Wait for the server's response
            response = await websocket.recv()
            print(f"Received from WebSocket: {response}")

            # Test if the server responded appropriately (replace 'pong' with expected response)
            if "pong" in response:
                print("WebSocket test passed.")
            else:
                print(f"Unexpected WebSocket response: {response}")

    except Exception as e:
        print(f"Error occurred while testing WebSocket: {e}")

def test_http():
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

async def main():
    # Run both tests (WebSocket test is asynchronous)
    test_http()
    await test_websocket()

if __name__ == "__main__":
    asyncio.run(main())
