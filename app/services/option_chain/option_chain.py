import gc
import pickle
import requests
import pandas as pd
from io import StringIO
from datetime import datetime, date

import redis.asyncio as aioredis

from app.core.config import settings
from app.services.option_chain.fyers_client import fyers_client
from app.services.option_chain.constants import (
    NSE_FO_CSV_URL, BSE_FO_CSV_URL,
    CSV_CACHE_KEY, CSV_CACHE_TTL,
    NSE_INDEX_SYMBOLS, BSE_INDEX_SYMBOLS
)
from app.utils.logger import logger


class OptionChainService:

    def _get_redis(self):
        return aioredis.from_url(settings.REDIS_URL, decode_responses=False, ssl_cert_reqs=None)

    def _get_csv_url(self, scrip: str) -> str:
        if scrip.upper() in BSE_INDEX_SYMBOLS:
            return BSE_FO_CSV_URL
        return NSE_FO_CSV_URL

    async def _fetch_csv(self, scrip: str) -> pd.DataFrame | None:
        cache_key = f"{CSV_CACHE_KEY}:{scrip.upper()}"
        redis = self._get_redis()

        try:
            cached = await redis.get(cache_key)
            if cached:
                logger.info(f"CSV cache hit for {scrip}")
                return pickle.loads(cached)

            logger.info(f"CSV cache miss for {scrip}, fetching...")
            url = self._get_csv_url(scrip)
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()

            content = resp.content.decode("utf-8", errors="ignore")
            df = pd.read_csv(StringIO(content), header=None, names=range(21), low_memory=False)

            # Filter for this scrip only before caching — keeps size small
            df = df[df[1].str.split().str[0] == scrip.strip().upper()]
            if df.empty:
                logger.warning(f"No option data found for {scrip}")
                return None

            await redis.set(cache_key, pickle.dumps(df), ex=CSV_CACHE_TTL)
            logger.info(f"CSV fetched, filtered and cached for {scrip} with {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"CSV fetch failed for {scrip}: {e}")
            return None
        finally:
            await redis.aclose()

    def _filter_scrip(self, df: pd.DataFrame, scrip: str) -> pd.DataFrame | None:
        scrip = scrip.strip().upper()
        df = df[df[1].str.split().str[0] == scrip]
        if df.empty:
            logger.warning(f"No option data found for {scrip}")
            return None
        logger.info(f"Found {len(df)} rows for {scrip}")
        return df

    def _extract_expiry_dates(self, df: pd.DataFrame) -> pd.DataFrame | None:
        def extract_date(v):
            parts = str(v).split()
            if len(parts) < 4:
                return pd.NaT
            try:
                return datetime.strptime(" ".join(parts[1:4]), "%d %b %y")
            except ValueError:
                return pd.NaT
        try:
            # df = df.copy()
            df["date"] = df[1].apply(extract_date)
            return df.dropna(subset=["date"])
        except Exception as e:
            logger.error(f"Date extraction error: {e}")
            return None

    def _select_expiry(self, scrip: str, df: pd.DataFrame) -> tuple:
        try:
            expiry_dates = sorted(df["date"].dt.date.unique())
            today = date.today()

            weekly_symbols = NSE_INDEX_SYMBOLS | BSE_INDEX_SYMBOLS
            is_weekly = any(scrip.upper() in sym or sym in scrip.upper() for sym in weekly_symbols)

            if is_weekly:
                for e in expiry_dates:
                    delta = (e - today).days
                    if delta > 0:
                        return e, delta
            else:
                for e in expiry_dates:
                    delta = (e - today).days
                    if delta > 3:
                        return e, delta

            logger.warning(f"No suitable expiry found for {scrip}")
            return None, None
        except Exception as e:
            logger.error(f"Expiry selection error: {e}")
            return None, None

    def _build_strike_chain(self, df: pd.DataFrame, scrip: str, direction: str) -> tuple:
        try:
            option_type = "CE" if direction == "BULLISH" else "PE"
            df = df[df[1].str.endswith(option_type)].copy()
            df["strike"] = df[1].str.split().str[4].astype(float)

            strikes = sorted(df["strike"].unique())
            if len(strikes) < 2:
                logger.warning(f"Not enough strikes for {scrip}")
                return None, None, None

            diff = min(b - a for a, b in zip(strikes, strikes[1:]))
            session = fyers_client.get_session()
            if not session:
                logger.error("Fyers session unavailable")
                return None, None, None

            ltp = self._fetch_ltp(scrip, session)
            if not ltp:
                return None, None, None

            atm = round(ltp / diff) * diff
            chain = [atm - i * diff for i in range(3, 0, -1)] + [atm] + [atm + i * diff for i in range(1, 6)]
            return df[df["strike"].isin(chain)].copy(), atm, ltp
        except Exception as e:
            logger.error(f"Strike chain build error: {e}")
            return None, None, None

    def _fetch_ltp(self, scrip: str, session) -> float | None:
        try:
            normalized = self._normalize_symbol(scrip)
            data = session.quotes({"symbols": normalized})
            return data["d"][0]["v"]["lp"]
        except Exception as e:
            logger.error(f"LTP fetch failed for {scrip}: {e}")
            return None

    def _normalize_symbol(self, symbol: str) -> str:
        mapping = {
            "NIFTY": "NSE:NIFTY50-INDEX",
            "BANKNIFTY": "NSE:NIFTYBANK-INDEX",
            "MIDCPNIFTY": "NSE:MIDCPNIFTY-INDEX",
            "FINNIFTY": "NSE:FINNIFTY-INDEX",
            "SENSEX": "BSE:SENSEX-INDEX",
            "BANKEX": "BSE:BANKEX-INDEX",
        }
        symbol = symbol.upper()
        exchange = "BSE" if symbol in {"SENSEX", "BANKEX"} else "NSE"
        return mapping.get(symbol, f"{exchange}:{symbol}-EQ")

    def _fetch_quotes(self, symbols: list, session) -> list:
        try:
            syms = ",".join(symbols)
            return session.quotes({"symbols": syms}).get("d", [])
        except Exception as e:
            logger.error(f"Quotes fetch failed: {e}")
            return []

    def _process_quotes(self, df: pd.DataFrame, session) -> list:
        try:
            syms = df[9].head(15).tolist()
            quotes = self._fetch_quotes(syms, session)
            details = {r[9]: {"lot": r[3], "strike": r[15]} for _, r in df.iterrows()}
            processed = []

            for q in sorted(quotes, key=lambda x: x["v"]["volume"], reverse=True):
                v = q["v"]
                name = q["n"]
                lot = details.get(name, {}).get("lot", 0)
                strike = details.get(name, {}).get("strike", 0)
                lp = v["lp"]
                vol = v["volume"]
                net_value = lot * lp

                if net_value >= 40000:
                    continue

                bid = v["bid"][0][0] if isinstance(v.get("bid"), list) and v["bid"] else v.get("bid")
                ask = v["ask"][0][0] if isinstance(v.get("ask"), list) and v["ask"] else v.get("ask")
                spread = (bid - ask) / bid if bid and ask and bid != 0 else None

                processed.append({
                    "instrument": name.replace("NSE:", "").replace("BSE:", ""),
                    "lp": lp,
                    "lot_size": int(lot),
                    "strike": float(strike) if strike else 0.0,
                    "volume": vol,
                    "net_value": net_value,
                    "spread": spread
                })
            return processed
        except Exception as e:
            logger.error(f"Quote processing error: {e}")
            return []

    async def get_best_instrument(self, scrip: str, direction: str) -> dict | None:
        try:
            df = await self._fetch_csv(scrip)
            if df is None:
                return None
            df = self._filter_scrip(df, scrip)
            df = self._extract_expiry_dates(df)
            if df is None:
                return None

            expiry, days_to_expiry = self._select_expiry(scrip, df)
            if not expiry:
                return None

            df = df[df["date"].dt.date == expiry]
            session = fyers_client.get_session()

            df, atm, stock_ltp = self._build_strike_chain(df, scrip, direction)
            if df is None:
                return None

            processed = self._process_quotes(df, session)
            del df
            gc.collect()

            if not processed:
                logger.warning(f"No instruments passed for {scrip}")
                return None

            return {
                "processed": processed,
                "atm": atm,
                "stock_ltp": stock_ltp,
                "expiry": expiry,
                "days_to_expiry": days_to_expiry
            }
        except Exception as e:
            logger.error(f"Option chain error for {scrip}: {e}")
            return None


option_chain_service = OptionChainService()
