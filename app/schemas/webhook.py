from pydantic import BaseModel


class WebhookRequest(BaseModel):
    stocks: str
    trigger_prices: str
    category: str = "INDEX"
