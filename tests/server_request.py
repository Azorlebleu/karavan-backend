import requests
import websockets
import asyncio
import json
import time

# Variables
room_id = "test_room"
player = "pedro"

# URL of the server
SERVER_URL = "http://127.0.0.1:8000"
WEBSOCKET_URL = "ws://127.0.0.1:8000/ws/test"

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
        async with websockets.connect(WEBSOCKET_URL) as websocket:
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
                if "pong" in response:
                    print("WebSocket test passed.")
                else:
                    print(f"Unexpected WebSocket response: {response}")
                
                # Wait for 1 second before sending the next ping
                await asyncio.sleep(1)

    except Exception as e:
        print(f"Error occurred while testing WebSocket: {e}")

# Main function to run both tests asynchronously
async def main():
    # Run both tests (WebSocket test is asynchronous)
    await asyncio.gather(test_http(), test_websocket())

if __name__ == "__main__":
    asyncio.run(main())
