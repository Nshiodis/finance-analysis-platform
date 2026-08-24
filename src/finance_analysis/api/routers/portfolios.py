from fastapi import APIRouter, Depends

from finance_analysis.api.dependencies import get_portfolio_service
from finance_analysis.api.schemas import (
    PortfolioCreate,
    PortfolioPerformanceResponse,
    PortfolioResponse,
)
from finance_analysis.services.portfolio_service import PortfolioService


router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.post("", response_model=PortfolioResponse, status_code=201)
def create_portfolio(
    payload: PortfolioCreate,
    service: PortfolioService = Depends(get_portfolio_service),
) -> dict[str, int | dict[str, float]]:
    """创建投资组合"""
    return service.create_portfolio(payload.weights)


@router.get("/{portfolio_id}/performance", response_model=PortfolioPerformanceResponse)
def get_portfolio_performance(
    portfolio_id: int,
    service: PortfolioService = Depends(get_portfolio_service),
) -> dict[str, int | float]:
    """获取投资组合绩效"""
    return service.get_portfolio_performance(portfolio_id)
