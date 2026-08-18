import pytest
from fastapi.testclient import TestClient
from finance_analysis.api.app import app


@pytest.fixture(scope="module")
def client():
    """每个测试模块只创建一次测试客户端"""
    return TestClient(app)


def test_stock_normal(client):
    """正常请求：200，字段齐全"""
    r = client.get("/stock/600519")
    assert r.status_code == 200
    data = r.json()
    assert data["rows"] == 1455
    assert set(data) == {"symbol", "rows", "latest_close", "total_return",
                         "volatility", "sharpe", "max_drawdown"}


def test_stock_with_date_range(client):
    """日期区间筛选：rows 应变为 242"""
    r = client.get("/stock/600519",
                   params={"start": "2022-01-01", "end": "2022-12-31"})
    assert r.status_code == 200
    assert r.json()["rows"] == 242


@pytest.mark.parametrize(
    "path, params, expected_status, expected_code, expected_messages",
    [
        ("/stock/600519", {"start": "2000-01-01", "end": "2000-12-31"}, 404, "STOCK_NO_DATA", "没有数据"),
        ("/stock/600519", {"start": "abc"}, 422, "VALIDATION_ERROR", None),
        ("/stock/999999", None, 404, "STOCK_NOT_FOUND", "不存在"),
        ("/stock/600519", {"start": "2022-01-02", "end": "2022-01-01"}, 422, "INVALID_DATE_RANGE", "不能晚于")
    ],
)
def test_stock_error_cases(client, path, params, expected_status, expected_code, expected_messages):
    """四个错误场景共用一套断言"""
    r = client.get(path, params=params)
    assert r.status_code == expected_status
    data = r.json()
    assert data["code"] == expected_code
    if expected_messages is not None:
        assert expected_messages in data["message"]
