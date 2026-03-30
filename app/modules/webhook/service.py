from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionFactory
from app.models.alert import AlertStatus, AlertCategory, AlertDirection
from app.modules.webhook.repository import webhook_repo
from app.services.option_chain.option_chain import option_chain_service
from app.services.option_chain.strategies import StrategyFactory
from app.services.option_chain.constants import LOT_SIZES
from app.utils.logger import logger


class WebhookService:

    async def process_alert(self, db: AsyncSession, symbol: str, price: float, direction: str, category: str):
        try:
            analyst_id = await webhook_repo.get_system_analyst_id(db)
            if not analyst_id:
                logger.error("System analyst account not found in DB")
                return

            result = await option_chain_service.get_best_instrument(symbol, direction)
            if not result:
                logger.warning(f"No instrument found for {symbol}, skipping alert")
                return

            strategy = StrategyFactory.get(symbol)
            best = strategy.select(result["processed"], result["atm"], direction)
            if not best:
                logger.warning(f"Strategy returned no trade for {symbol}")
                return

            lot_size = best["lot_size"] or LOT_SIZES.get(symbol.upper(), 1)
            investment = round(best["lp"] * lot_size, 2)

            data = {
                "category": AlertCategory[category.upper()],
                "direction": AlertDirection[direction.upper()],
                "exchange": "MCX" if category.upper() == "COMMODITY" else "NSE",
                "contract": best["instrument"],
                "symbol": symbol.upper(),
                "ltp": result["stock_ltp"],
                "strike": best.get("strike"),
                "option_ltp": best["lp"],
                "lot_size": lot_size,
                "investment": investment,
                "status": AlertStatus.ACTIVE,
                "published_at": datetime.now(timezone.utc),
            }

            alert = await webhook_repo.create_alert(db, analyst_id=analyst_id, data=data)
            logger.info(f"Alert created for {symbol}: {best['instrument']}")
            return alert

        except Exception as e:
            logger.error(f"WebhookService.process_alert failed for {symbol}: {e}")

    async def process_bulk(self, stocks: list[str], prices: list[float], direction: str, category: str):
        async with AsyncSessionFactory() as db:
            for symbol, price in zip(stocks, prices):
                await self.process_alert(db, symbol.strip(), price, direction, category)


webhook_service = WebhookService()