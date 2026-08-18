from datetime import date
from fastapi import FastAPI, HTTPException

from finance_analysis.exceptions import StockNoDataError, StockNotFoundError
from finance_analysis.utils.logger import setup_logging
from finance_analysis.api.schemas import StockResponse
from finance_analysis.services.stock_service import StockService


setup_logging()

app = FastAPI()

service = StockService()

@app.get("/stock/{symbol}", response_model=StockResponse)
def get_stock(symbol: str, start: date | None = None, end: date | None = None):
    """获取股票数据"""
    try:
        return service.get_stock_metrics(symbol, start, end)
    except StockNotFoundError:
        raise HTTPException(status_code=404, detail=f"股票{symbol}不存在")
    except StockNoDataError:
        raise HTTPException(status_code=404, detail=f"股票{symbol}在指定日期范围内没有数据")