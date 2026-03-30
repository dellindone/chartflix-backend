LOT_SIZES = {
    "NIFTY": 65,
    "BANKNIFTY": 35,
    "FINNIFTY": 40,
    "MIDCPNIFTY": 120,
    "SENSEX": 20,
    "BANKEX": 15,
    "GOLD": 100,
    "SILVER": 30,
    "CRUDEOIL": 100,
    "NATURALGAS": 1250
}

MCX_SYMBOLS = {"GOLD", "SILVER", "CRUDEOIL", "NATURALGAS", "COPPER", "ZINC", "LEAD", "ALUMINIUM"}

NSE_INDEX_SYMBOLS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"}
BSE_INDEX_SYMBOLS = {"SENSEX", "BANKEX"}

def resolve_category(symbol: str) -> str:
    s = symbol.upper()
    if s in MCX_SYMBOLS:
        return "COMMODITY"
    if s in NSE_INDEX_SYMBOLS | BSE_INDEX_SYMBOLS:
        return "INDEX"
    return "STOCK"

SPREAD_THRESHOLD_PCT = 2.0

CSV_CACHE_KEY = "option_chain:nse_fo_csv"
CSV_CACHE_TTL = 21600  # 6 hours in seconds

NSE_FO_CSV_URL = "https://public.fyers.in/sym_details/NSE_FO.csv"
BSE_FO_CSV_URL = "https://public.fyers.in/sym_details/BSE_FO.csv"
MCX_FO_CSV_URL = "https://public.fyers.in/sym_details/MCX_FO.csv"