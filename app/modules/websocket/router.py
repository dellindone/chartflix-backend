from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import select

from app.core.database import AsyncSessionFactory
from app.core.websocket import manager
from app.core.security import decode_token
from app.models.user import User

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/alerts")
async def alerts_websocket(websocket: WebSocket, token: str = Query(...)):
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001)
        return

    async with AsyncSessionFactory() as db:
        result = await db.execute(select(User).where(User.id == payload.get("sub")))
        user = result.scalar_one_or_none()

    if not user or (user.role != "admin" and not user.is_approved):
        await websocket.close(code=4003)
        return

    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
