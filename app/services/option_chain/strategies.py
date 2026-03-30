from app.services.option_chain.constants import MCX_SYMBOLS, SPREAD_THRESHOLD_PCT
from app.utils.logger import logger


class NSEBSEStrategy:
    def select(self, processed: list, atm: float, direction: str) -> dict | None:
        try:
            # For BULLISH (CE) → ITM means strike < ATM, go 2 strikes below
            # For BEARISH (PE) → ITM means strike > ATM, go 2 strikes above
            candidates = []
            for item in processed:
                if item.get("strike"):
                    candidates.append(item)

            if not candidates:
                return None

            if direction == "BULLISH":
                itm = [c for c in candidates if c["strike"] < atm]
                itm = sorted(itm, key=lambda x: x["strike"], reverse=True)
            else:
                itm = [c for c in candidates if c["strike"] > atm]
                itm = sorted(itm, key=lambda x: x["strike"])

            # Pick 2nd ITM
            target = itm[1] if len(itm) >= 2 else (itm[0] if itm else None)
            if not target:
                logger.warning("No ITM strike found")
                return None

            # Check spread
            if target["spread"] is None:
                logger.warning(f"No spread data for {target['instrument']}")
                return None

            spread_pct = abs(target["spread"]) * 100
            if spread_pct >= SPREAD_THRESHOLD_PCT:
                logger.warning(f"{target['instrument']} spread {spread_pct:.2f}% too wide, no trade")
                return None

            return target
        except Exception as e:
            logger.error(f"NSEBSEStrategy error: {e}")
            return None


class MCXStrategy:
    def select(self, processed: list, atm: float, direction: str) -> dict | None:
        try:
            for item in processed:
                if item["spread"] is None:
                    continue
                spread_pct = abs(item["spread"]) * 100
                if spread_pct < SPREAD_THRESHOLD_PCT:
                    logger.info(f"MCX selected {item['instrument']} with spread {spread_pct:.2f}%")
                    return item

            logger.warning("No MCX instrument passed spread filter")
            return None
        except Exception as e:
            logger.error(f"MCXStrategy error: {e}")
            return None


class StrategyFactory:
    @staticmethod
    def get(scrip: str):
        if scrip.upper() in MCX_SYMBOLS:
            return MCXStrategy()
        return NSEBSEStrategy()