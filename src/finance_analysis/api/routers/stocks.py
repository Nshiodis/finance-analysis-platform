from datetime import date

from fastapi import APIRouter, Depends

from finance_analysis.api.schemas import StockListResponse, StockResponse
from finance_analysis.api.dependencies import get_stock_service
from finance_analysis.services.stock_service import StockService


router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("", response_model=StockListResponse)
def list_stocks(
    service: StockService = Depends(get_stock_service)
):
    """获取所有股票代码"""
    return {"symbols": service.list_stocks()}


@router.get("/{symbol}", response_model=StockResponse)
def get_stock(
    symbol: str,
    start: date | None = None,
    end: date | None = None,
    service: StockService = Depends(get_stock_service)
):
    """获取股票数据(可选日期范围)"""
    return service.get_stock_metrics(symbol, start, end)
