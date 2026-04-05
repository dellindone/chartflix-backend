import asyncio
from datetime import datetime, timezone

from app.services.option_chain.option_chain import option_chain_service
from app.utils.logger import logger

# Symbols to pre-warm every day before market open
WARM_SYMBOLS = [
    "NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY",
    "SENSEX", "BANKEX",
]

WARM_TIME_IST = (9, 0)   # 9:00 AM IST = 3:30 AM UTC
IST_OFFSET = 5.5 * 3600  # seconds


def _seconds_until_next_warm():
    now_utc = datetime.now(timezone.utc)
    now_ist_seconds = (now_utc.hour * 3600 + now_utc.minute * 60 + now_utc.second) + IST_OFFSET
    now_ist_seconds %= 86400  # wrap around midnight

    target_seconds = WARM_TIME_IST[0] * 3600 + WARM_TIME_IST[1] * 60
    wait = target_seconds - now_ist_seconds
    if wait <= 0:
        wait += 86400  # already past 9 AM today, wait for tomorrow
    return wait


async def _warm_cache():
    logger.info("Cache warmer: pre-fetching CSVs for market open...")
    for symbol in WARM_SYMBOLS:
        try:
            await option_chain_service._fetch_csv(symbol)
            logger.info(f"Cache warmer: warmed {symbol}")
        except Exception as e:
            logger.error(f"Cache warmer: failed for {symbol}: {e}")
        await asyncio.sleep(1)  # small gap to avoid hammering Fyers CDN
    logger.info("Cache warmer: all symbols warmed")


async def start_cache_warmer():
    while True:
        wait = _seconds_until_next_warm()
        logger.info(f"Cache warmer: next warm in {wait/3600:.1f} hours (at 9:00 AM IST)")
        await asyncio.sleep(wait)
        await _warm_cache()
