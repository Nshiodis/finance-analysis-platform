from datetime import date
from typing import Any, cast
from unittest.mock import MagicMock

import pandas as pd
import pytest

from finance_analysis.exceptions import (
    InvalidDateRangeError,
    StockNoDataError,
    StockNotFoundError,
)
from finance_analysis.services.stock_service import StockService


def make_stock_df(
    n: int = 30, start: str = "2024-01-01", symbol: str = "600519"
) -> pd.DataFrame:
    """造一只股票的 DataFrame（列与数据库一致）"""
    dates = pd.date_range(start, periods=n, freq="B")
    close = pd.Series(range(10, 10 + n), dtype=float)
    return pd.DataFrame({
        "symbol": [symbol] * n,
        "date": dates.strftime("%Y-%m-%d"),
        "open": close,
        "high": close + 1,
        "low": close - 1,
        "close": close,
        "volume": [1000] * n,
    })    


@pytest.fixture
def service() -> StockService:
    """每个测试拿到一个"假仓库"的 service，不碰数据库"""
    svc = StockService(db_path=":memory:")   # 构造不连库，所以放心
    svc.repository = cast(Any, MagicMock())  # 替换成假仓库
    return svc


@pytest.fixture
def mock_repo(service: StockService) -> Any:
    """以 Any 视角访问假仓库——绕开"属性读出来仍是 StockRepository"""
    return cast(Any, service.repository)


def test_get_stock_metrics_normal(service: StockService, mock_repo: Any) -> None:
    """正常：mock 返回数据，断言编排结果"""
    mock_repo.get_stock.return_value = make_stock_df()
    result = service.get_stock_metrics("600519")
    assert result["rows"] == 30
    assert set(result) == {"symbol", "rows", "latest_close", "total_return",
                           "volatility", "sharpe", "max_drawdown"}


def test_get_stock_metrics_stock_not_found(service: StockService, mock_repo: Any) -> None:
    """全量查询也空 → 股票不存在"""
    mock_repo.get_stock.return_value = pd.DataFrame()
    with pytest.raises(StockNotFoundError):
        service.get_stock_metrics("999999")


def test_get_stock_metrics_not_found_with_date_range(
    service: StockService, mock_repo: Any
) -> None:
    """带了日期区间、但全量也空 → 依然判"股票不存在"（不是"区间无数据"）"""
    mock_repo.get_stock.return_value = pd.DataFrame()
    with pytest.raises(StockNotFoundError):
        service.get_stock_metrics(
            "999999", start=date(2024, 1, 1), end=date(2024, 12, 31)
        )


def test_get_stock_metrics_no_data_in_range(service: StockService, mock_repo: Any) -> None:
    """区间空、全量有 → 区间无数据（side_effect 依次返回）"""
    mock_repo.get_stock.side_effect = [pd.DataFrame(), make_stock_df()]
    with pytest.raises(StockNoDataError):
        service.get_stock_metrics("600519", start=date(2020, 1, 1), end=date(2020, 1, 31))


def test_get_stock_metrics_invalid_date_range(service: StockService) -> None:
    """倒挂日期 → 422 异常（不用 mock）"""
    with pytest.raises(InvalidDateRangeError):
        service.get_stock_metrics("600519", start=date(2022, 1, 2), end=date(2022, 1, 1))


def test_list_stocks(service: StockService, mock_repo: Any) -> None:
    """列表：返回 mock 的符号，并断言确实调用了仓库"""
    mock_repo.get_all_symbols.return_value = ["000858", "300750", "600519"]
    assert service.list_stocks() == ["000858", "300750", "600519"]
    mock_repo.get_all_symbols.assert_called_once()
