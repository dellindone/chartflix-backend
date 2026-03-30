import asyncio
import redis.asyncio as aioredis
from fastapi import WebSocket
from app.core.config import settings
from app.utils.logger import logger

ALERT_CHANNEL = "chartflix:alerts"


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass


async def start_redis_listener():
    logger.info("Starting Redis Pub/Sub listener...")
    while True:
        redis = None
        pubsub = None
        try:
            redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True, ssl_cert_reqs=None)
            pubsub = redis.pubsub()
            await pubsub.subscribe(ALERT_CHANNEL)
            logger.info(f"Subscribed to Redis channel: {ALERT_CHANNEL}")
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message["type"] == "message":
                    await manager.broadcast(message["data"])
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            logger.info("Redis listener cancelled")
            break
        except Exception as e:
            logger.error(f"Redis listener error: {e}, retrying in 3s...")
            await asyncio.sleep(3)
        finally:
            if pubsub:
                try:
                    await pubsub.unsubscribe(ALERT_CHANNEL)
                    await pubsub.aclose()
                except Exception:
                    pass
            if redis:
                try:
                    await redis.aclose()
                except Exception:
                    pass


manager = ConnectionManager()
