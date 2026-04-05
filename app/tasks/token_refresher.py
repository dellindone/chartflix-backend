import asyncio
from datetime import datetime, timezone

from app.services.option_chain.fyers_client import fyers_client
from app.utils.logger import logger

# 8:55 AM IST and 3:55 PM IST (8:55 + 7 hours)
REFRESH_TIMES_IST = [(8, 55), (15, 55)]
IST_OFFSET = 5.5 * 3600  # seconds


def _ist_seconds_now():
    now_utc = datetime.now(timezone.utc)
    ist = (now_utc.hour * 3600 + now_utc.minute * 60 + now_utc.second) + IST_OFFSET
    return ist % 86400


def _seconds_until_next_refresh():
    now = _ist_seconds_now()
    targets = [h * 3600 + m * 60 for h, m in REFRESH_TIMES_IST]
    upcoming = [t - now for t in targets if t - now > 0]
    if upcoming:
        return min(upcoming)
    # All times passed today — wait until first one tomorrow
    return 86400 - now + targets[0]


async def start_token_refresher():
    while True:
        wait = _seconds_until_next_refresh()
        h, m = divmod(int(wait // 60), 60)
        logger.info(f"Token refresher: next refresh in {h}h {m}m")
        await asyncio.sleep(wait)
        try:
            logger.info("Token refresher: invalidating Fyers session and re-logging in...")
            fyers_client.invalidate()
            session = await fyers_client.get_session_async()
            if session:
                logger.info("Token refresher: Fyers token refreshed successfully")
            else:
                logger.error("Token refresher: Fyers re-login failed")
        except Exception as e:
            logger.error(f"Token refresher: exception during refresh: {e}")
