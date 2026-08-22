from datetime import date

from fastapi import APIRouter, Depends, Query

from finance_analysis.api.schemas import IndicatorsResponse, RiskResponse, StockListResponse, StockResponse
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


@router.get("/{symbol}/risk", response_model=RiskResponse)
def get_stock_risk(
    symbol: str,
    start: date | None = None,
    end: date | None = None,
    service: StockService = Depends(get_stock_service)
):
    """获取股票风险指标"""
    return service.get_stock_risk(symbol, start, end)


@router.get("/{symbol}/indicators", response_model=IndicatorsResponse)
def get_stock_indicators(
    symbol: str,
    window: int = Query(20, ge=1),
    start: date | None = None,
    end: date | None = None,
    service: StockService = Depends(get_stock_service)
):
    """获取股票技术指标序列(MA/RSI/MACD)"""
    return service.get_stock_indicators(symbol, window, start, end)
