from fastapi import APIRouter, BackgroundTasks, Query

from app.modules.webhook import controller
from app.schemas.webhook import WebhookRequest
from app.utils.logger import logger

router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post("/bullish")
async def bullish_webhook(
    data: WebhookRequest,
    background_tasks: BackgroundTasks,
    secret: str = Query(...),
):
    logger.info(f"Bullish webhook received: {data}")
    stocks = [s.strip() for s in data.stocks.split(",")]
    prices = [float(p.strip()) for p in data.trigger_prices.split(",")]
    return await controller.handle_webhook(
        background_tasks, stocks, prices,
        direction="BULLISH",
        category=data.category,
        secret=secret,
    )


@router.post("/bearish")
async def bearish_webhook(
    data: WebhookRequest,
    background_tasks: BackgroundTasks,
    secret: str = Query(...),
):
    logger.info(f"Bearish webhook received: {data}")
    stocks = [s.strip() for s in data.stocks.split(",")]
    prices = [float(p.strip()) for p in data.trigger_prices.split(",")]
    return await controller.handle_webhook(
        background_tasks, stocks, prices,
        direction="BEARISH",
        category=data.category,
        secret=secret,
    )
