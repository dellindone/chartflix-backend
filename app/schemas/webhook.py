from pydantic import BaseModel


class WebhookRequest(BaseModel):
    secret: str
    stocks: str
    trigger_prices: str
    category: str = "INDEX"
