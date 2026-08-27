from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from finance_analysis.exceptions import InvalidPortfolioError, PortfolioNotFoundError
from finance_analysis.services.portfolio_service import PortfolioService


@pytest.fixture
def service() -> PortfolioService:
    """每个测试拿到一个"假仓库"的 service"""
    svc = PortfolioService(db_path=":memory:")
    svc.repository = cast(Any, MagicMock())
    return svc


@pytest.fixture
def mock_repo(service: PortfolioService) -> Any:
    """以 Any 视角访问假仓库"""
    return cast(Any, service.repository)


def test_create_portfolio_ok(service: PortfolioService, mock_repo: Any) -> None:
    """创建成功：返回 id + weights，且确实调用了仓库"""
    mock_repo.create_portfolio.return_value = 1
    result = service.create_portfolio({"600519": 0.5, "000858": 0.5})
    assert result == {"id": 1, "weights": {"600519": 0.5, "000858": 0.5}}
    mock_repo.create_portfolio.assert_called_once_with({"600519": 0.5, "000858": 0.5})


def test_create_portfolio_empty(service: PortfolioService, mock_repo: Any) -> None:
    """空权重 → 422"""
    with pytest.raises(InvalidPortfolioError):
        service.create_portfolio({})


def test_create_portfolio_invalid_weights(service: PortfolioService, mock_repo: Any) -> None:
    """负权重 / 权重和不为 1 → 422"""
    with pytest.raises(InvalidPortfolioError):
        service.create_portfolio({"600519": -0.5, "000858": 1.5})
    with pytest.raises(InvalidPortfolioError):
        service.create_portfolio({"600519": 0.2})


def test_get_portfolio_performance_not_found(service: PortfolioService, mock_repo: Any) -> None:
    """查不到组合 → 404"""
    mock_repo.get_portfolio.return_value = None
    with pytest.raises(PortfolioNotFoundError):
        service.get_portfolio_performance(999)