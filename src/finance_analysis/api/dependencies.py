from finance_analysis.services.stock_service import StockService
from finance_analysis.services.portfolio_service import PortfolioService


def get_stock_service() -> StockService:
    return StockService()


def get_portfolio_service() -> PortfolioService:
    return PortfolioService()
