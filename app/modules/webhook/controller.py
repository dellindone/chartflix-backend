from fastapi import BackgroundTasks

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.modules.webhook.service import webhook_service
from app.utils.response import success


async def handle_webhook(
    background_tasks: BackgroundTasks,
    stocks: list[str],
    prices: list[float],
    direction: str,
    category: str,
    secret: str,
):
    if secret.strip() != settings.WEBHOOK_SECRET.strip():
        raise UnauthorizedException("Invalid webhook secret")

    background_tasks.add_task(
        webhook_service.process_bulk,
        stocks, prices, direction, category
    )

    return success(data=None, message=f"{len(stocks)} alert(s) queued for processing")