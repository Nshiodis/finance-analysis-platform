from pydantic import BaseModel


class StockResponse(BaseModel):
    symbol: str
    rows: int
    latest_close: float
    total_return: float
    volatility: float
    sharpe: float
    max_drawdown: float