from datetime import date
from fastapi import FastAPI, HTTPException

from finance_analysis.exceptions import StockNoDataError, StockNotFoundError
from finance_analysis.utils.logger import setup_logging
from finance_analysis.models.stock import StockData
from finance_analysis.api.schemas import StockResponse

setup_logging()

app = FastAPI()

@app.get("/stock/{symbol}", response_model=StockResponse)
def get_stock(symbol: str, start: date | None = None, end: date | None = None):
    """获取股票数据"""
    try:
        stock = StockData.from_database(
            symbol=symbol,
            start=start,
            end=end
        )
        stock.calculate_return()
        return {
            "symbol": symbol,
            "rows": len(stock.df),
            "latest_close": float(stock.df["close"].iloc[-1]),
            "total_return": float(stock.calculate_total_return()),
            "volatility": float(stock.calculate_volatility()),
            "sharpe": float(stock.calculate_sharpe_ratio()),
            "max_drawdown": float(stock.calculate_max_drawdown())
        }
    except StockNotFoundError:
        raise HTTPException(status_code=404, detail=f"股票{symbol}不存在")
    except StockNoDataError:
        raise HTTPException(status_code=404, detail=f"股票{symbol}在指定日期范围内没有数据")