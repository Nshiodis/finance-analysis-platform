from pydantic import BaseModel


class StockResponse(BaseModel):
    symbol: str
    rows: int
    latest_close: float
    total_return: float
    volatility: float
    sharpe: float
    max_drawdown: float


class StockListResponse(BaseModel):
    symbols: list[str]


class RiskResponse(BaseModel):
    symbol: str
    rows: int
    total_return: float
    volatility: float
    sharpe: float
    max_drawdown: float
    


class IndicatorPoint(BaseModel):
    date: str
    ma: float
    rsi: float
    dif: float
    dea: float
    macd: float


class IndicatorsResponse(BaseModel):
    symbol: str
    window: int
    rows: int
    series: list[IndicatorPoint]