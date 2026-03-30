import asyncio
import websockets

url = "ws://localhost:8000/ws/alerts?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkYmNlZmJiZC03ODAyLTRkZGUtODJkMi1iOTVmMjRjYTkyMTUiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NzQ4NzE5MDl9.v6jBRx2UbwQNYcQjpHRsvuN6BAd72JbcEqLoNqgEo6E"

async def listen():
    async with websockets.connect(url) as ws:
        while True:
            msg = await ws.recv()
            print(msg)

asyncio.run(listen())