import pytest
import httpx
from fastapi.testclient import TestClient
from finance_analysis.api.app import app


@pytest.fixture(scope="module")
def client() -> httpx.Client:
    """每个测试模块只创建一次测试客户端"""
    return TestClient(app)


def test_stock_normal(client: httpx.Client) -> None:
    """正常请求：200，字段齐全"""
    r = client.get("/stocks/600519")
    assert r.status_code == 200
    data = r.json()
    assert data["rows"] == 1455
    assert set(data) == {"symbol", "rows", "latest_close", "total_return",
                         "volatility", "sharpe", "max_drawdown"}


def test_stock_with_date_range(client: httpx.Client) -> None:
    """日期区间筛选：rows 应变为 242"""
    r = client.get("/stocks/600519",
                   params={"start": "2022-01-01", "end": "2022-12-31"})
    assert r.status_code == 200
    assert r.json()["rows"] == 242


def test_stock_list(client: httpx.Client) -> None:
    """股票列表：200，symbols 包含 600519"""
    r = client.get("/stocks")
    assert r.status_code == 200
    data = r.json()
    assert set(data) == {"symbols"}
    assert "600519" in data["symbols"]


def test_stock_legacy_path(client: httpx.Client) -> None:
    """旧路径 /stock/{symbol} 仍可用（v1.0 前兼容）"""
    r = client.get("/stock/600519")
    assert r.status_code == 200
    assert r.json()["rows"] == 1455


def test_stock_risk(client: httpx.Client) -> None:
    """股票风险指标：200，字段齐全"""
    r = client.get("/stocks/600519/risk")
    assert r.status_code == 200
    data = r.json()
    assert set(data) == {"symbol", "rows", "total_return", "volatility", "sharpe", "max_drawdown"}


def test_stock_indicators(client: httpx.Client) -> None:
    """股票指标：200，字段齐全"""
    r = client.get("/stocks/600519/indicators", params={"window": 20})
    assert r.status_code == 200
    data = r.json()
    assert set(data) == {"symbol", "window", "rows","series"}


def test_stock_risk_not_found(client: httpx.Client) -> None:
    """风险接口：不存在的股票返回 404"""
    r = client.get("/stocks/999999/risk")
    assert r.status_code == 404
    assert r.json()["code"] == "STOCK_NOT_FOUND"


def test_stock_indicators_not_found(client: httpx.Client) -> None:
    """指标接口：不存在的股票返回 404"""
    r = client.get("/stocks/999999/indicators")
    assert r.status_code == 404
    assert r.json()["code"] == "STOCK_NOT_FOUND"


def test_stock_indicators_series(client: httpx.Client) -> None:
    """指标序列：window=20 时有效行数 1436，字段齐全，RSI 在 0~100"""
    r = client.get("/stocks/600519/indicators", params={"window": 20})
    data = r.json()
    assert data["rows"] == 1436
    assert len(data["series"]) == 1436
    assert set(data["series"][0]) == {"date", "ma", "rsi", "dif", "dea", "macd"}
    assert all(0 <= p["rsi"] <= 100 for p in data["series"])


def test_stock_indicators_window(client: httpx.Client) -> None:
    """window=5 时 MA 预热期变短，有效行数 1451"""
    r = client.get("/stocks/600519/indicators", params={"window": 5})
    assert r.json()["rows"] == 1451


@pytest.mark.parametrize(
    "path, params, expected_status, expected_code, expected_messages",
    [
        ("/stocks/600519", {"start": "2000-01-01", "end": "2000-12-31"}, 404, "STOCK_NO_DATA", "没有数据"),
        ("/stocks/600519", {"start": "abc"}, 422, "VALIDATION_ERROR", None),
        ("/stocks/999999", None, 404, "STOCK_NOT_FOUND", "不存在"),
        ("/stocks/600519", {"start": "2022-01-02", "end": "2022-01-01"}, 422, "INVALID_DATE_RANGE", "不能晚于")
    ],
)
def test_stock_error_cases(
    client: httpx.Client,
    path: str,
    params: dict[str, str] | None,
    expected_status: int,
    expected_code: str,
    expected_messages: str | None,
) -> None:
    """四个错误场景共用一套断言"""
    r = client.get(path, params=params)
    assert r.status_code == expected_status
    data = r.json()
    assert data["code"] == expected_code
    if expected_messages is not None:
        assert expected_messages in data["message"]


def test_create_portfolio(client: httpx.Client) -> None:
    """创建组合：201，id + weights 返回"""
    r = client.post("/portfolios", json={"weights": {"600519": 0.5, "000858": 0.5}})
    assert r.status_code == 201
    data = r.json()
    assert isinstance(data["id"], int)
    assert data["weights"] == {"600519": 0.5, "000858": 0.5}


def test_portfolio_performance(client: httpx.Client) -> None:
    """创建后查绩效：能查出来本身就证明"已入库"""
    r = client.post("/portfolios", json={"weights": {"600519": 0.5, "000858": 0.5}})
    portfolio_id = r.json()["id"]

    r2 = client.get(f"/portfolios/{portfolio_id}/performance")
    assert r2.status_code == 200
    assert set(r2.json()) == {"id", "portfolio_total_return", "annualized_return",
                              "volatility", "sharpe", "benchmark_total_return",
                              "excess_total_return"}


def test_portfolio_not_found(client: httpx.Client) -> None:
    """不存在的组合：404"""
    r = client.get("/portfolios/999999/performance")
    assert r.status_code == 404
    assert r.json()["code"] == "PORTFOLIO_NOT_FOUND"


def test_portfolio_invalid_empty(client: httpx.Client) -> None:
    """空权重：422"""
    r = client.post("/portfolios", json={"weights": {}})
    assert r.status_code == 422
    assert r.json()["code"] == "INVALID_PORTFOLIO"


def test_portfolio_invalid_weight_sum(client: httpx.Client) -> None:
    """权重和不为 1：422"""
    r = client.post("/portfolios", json={"weights": {"600519": 0.2}})
    assert r.status_code == 422
    assert r.json()["code"] == "INVALID_PORTFOLIO"
