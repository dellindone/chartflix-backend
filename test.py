import asyncio
import websockets

async def listen():
    async with websockets.connect("ws://localhost:8000/ws/alerts") as ws:
        while True:
            msg = await ws.recv()
            print(msg)

asyncio.run(listen())