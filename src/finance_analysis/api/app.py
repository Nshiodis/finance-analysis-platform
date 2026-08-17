from fastapi import FastAPI, HTTPException

from finance_analysis.utils.logger import setup_logging
from finance_analysis.models.stock import StockData

setup_logging()

app = FastAPI()

@app.get("/stock/{symbol}")
def get_stock(symbol: str):
    """获取股票数据"""
    try:
        stock = StockData.from_database(symbol=symbol)
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
    except ValueError:
        raise HTTPException(status_code=404, detail=f"股票{symbol}不存在")