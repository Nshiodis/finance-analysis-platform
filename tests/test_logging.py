import logging
import sqlite3
from typing import Any, cast
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi.testclient import TestClient

from finance_analysis.api.app import app
from finance_analysis.exceptions import DatabaseError
from finance_analysis.repository.portfolio_repository import PortfolioRepository
from finance_analysis.repository.stock_repository import StockRepository
from finance_analysis.utils.logger import RequestIdFormatter, request_id_var


@pytest.fixture(scope="module")
def client() -> httpx.Client:
    """每个测试模块只创建一次测试客户端"""
    return TestClient(app)


def test_middleware_logs_request_line(client: httpx.Client, caplog: pytest.LogCaptureFixture) -> None:
    """中间件：method / path / status / 耗时 一行记录"""
    caplog.set_level(logging.INFO)
    client.get("/stocks/600519")
    assert "请求开始 GET /stocks/600519" in caplog.text
    assert "请求完成 GET /stocks/600519 -> 200" in caplog.text
    assert "耗时" in caplog.text


def test_middleware_logs_query_params(client: httpx.Client, caplog: pytest.LogCaptureFixture) -> None:
    """INFO：查询参数出现在请求行里"""
    caplog.set_level(logging.INFO)
    client.get("/stocks/600519", params={"start": "2022-01-01", "end": "2022-12-31"})
    assert "GET /stocks/600519?start=2022-01-01&end=2022-12-31" in caplog.text


def test_middleware_logs_not_found(client: httpx.Client, caplog: pytest.LogCaptureFixture) -> None:
    """WARNING：股票未命中 + 中间件记录 404"""
    caplog.set_level(logging.INFO)
    client.get("/stocks/999999")
    assert "-> 404" in caplog.text
    assert "股票 999999 未找到" in caplog.text


def test_middleware_logs_no_data(client: httpx.Client, caplog: pytest.LogCaptureFixture) -> None:
    """WARNING：区间无数据（区别于不存在）"""
    caplog.set_level(logging.INFO)
    client.get("/stocks/600519", params={"start": "2000-01-01", "end": "2000-12-31"})
    assert "在指定日期范围内没有数据" in caplog.text


def test_middleware_logs_validation_error(client: httpx.Client, caplog: pytest.LogCaptureFixture) -> None:
    """校验失败：422 进日志"""
    caplog.set_level(logging.INFO)
    client.get("/stocks/600519", params={"start": "abc"})
    assert "-> 422" in caplog.text


def test_middleware_does_not_log_post_body(client: httpx.Client, caplog: pytest.LogCaptureFixture) -> None:
    """不记录敏感信息：组合权重不进日志"""
    caplog.set_level(logging.INFO)
    client.post("/portfolios", json={"weights": {"600519": 0.5, "000858": 0.5}})
    assert "POST /portfolios" in caplog.text
    assert "组合已创建" in caplog.text
    assert "600519" not in caplog.text
    assert "000858" not in caplog.text


def test_request_id_formatter() -> None:
    """格式化器：把 ContextVar 里的 request_id 写进日志行"""
    formatter = RequestIdFormatter("%(request_id)s %(message)s")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    token = request_id_var.set("abc12345")
    try:
        assert formatter.format(record) == "abc12345 hello"
    finally:
        request_id_var.reset(token)


def test_request_id_shared_across_layers(client: httpx.Client, caplog: pytest.LogCaptureFixture) -> None:
    """可观测性核心：中间件与 Service 的日志共享同一个 request_id"""
    caplog.set_level(logging.INFO)
    caplog.handler.setFormatter(RequestIdFormatter("%(request_id)s|%(name)s|%(message)s"))
    client.get("/stocks/600519")

    middleware_records = [
        r for r in caplog.records if r.name == "finance_analysis.api.middleware"
    ]
    service_records = [
        r for r in caplog.records if r.name == "finance_analysis.services.stock_service"
    ]
    assert middleware_records
    assert service_records

    request_ids = {getattr(r, "request_id") for r in middleware_records + service_records}
    assert len(request_ids) == 1
    assert request_ids != {"-"}


def test_stock_repository_logs_database_error(caplog: pytest.LogCaptureFixture) -> None:
    """ERROR：数据库失败在 Repository 层记录根因"""
    caplog.set_level(logging.ERROR)
    repo = StockRepository(db_path=":memory:")
    repo.db = cast(Any, MagicMock())
    repo.db.query_stock.side_effect = sqlite3.OperationalError("table not found")

    with pytest.raises(DatabaseError):
        repo.get_stock("600519")

    assert "查询股票 600519 失败：table not found" in caplog.text


def test_portfolio_repository_logs_database_error(caplog: pytest.LogCaptureFixture) -> None:
    """ERROR：组合查询数据库失败同样记录"""
    caplog.set_level(logging.ERROR)
    repo = PortfolioRepository(db_path=":memory:")
    repo.db = cast(Any, MagicMock())
    repo.db.query_portfolio.side_effect = sqlite3.OperationalError("table not found")

    with pytest.raises(DatabaseError):
        repo.get_portfolio(1)

    assert "查询组合 1 失败：table not found" in caplog.text