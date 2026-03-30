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

            # Try ITM 2 → ITM 1 → ATM until spread passes
            candidates_ordered = []
            if len(itm) >= 2:
                candidates_ordered.append(itm[1])
            if len(itm) >= 1:
                candidates_ordered.append(itm[0])

            # add ATM strike
            atm_candidates = [c for c in candidates if c["strike"] == atm]
            if atm_candidates:
                candidates_ordered.append(atm_candidates[0])

            for target in candidates_ordered:
                if target["spread"] is None:
                    continue
                spread_pct = abs(target["spread"]) * 100
                if spread_pct < SPREAD_THRESHOLD_PCT:
                    logger.info(f"Selected {target['instrument']} with spread {spread_pct:.2f}%")
                    return target
                logger.warning(f"{target['instrument']} spread {spread_pct:.2f}% too wide, trying next")

            # Fallback: no bid/ask data (illiquid exchange) — pick first candidate by ITM order
            if candidates_ordered:
                best = candidates_ordered[0]
                logger.warning(f"No spread data available, falling back to {best['instrument']} by ITM order")
                return best

            logger.warning("No suitable strike found")
            return None
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

            # Fallback: no bid/ask data — pick first item by volume
            if processed:
                best = processed[0]
                logger.warning(f"No spread data available, falling back to {best['instrument']} by volume")
                return best

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