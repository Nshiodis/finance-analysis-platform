import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from finance_analysis.database.manager import DatabaseManager


def make_stock_df(symbol: str = "600519", n: int = 3) -> pd.DataFrame:
    """造一个小 DataFrame（列与数据库一致）"""
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
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
def manager(tmp_path: Path) -> DatabaseManager:
    """每个测试一个独立临时库"""
    return DatabaseManager(tmp_path / "manager.db")


def test_read_dataframe_roundtrip(manager: DatabaseManager) -> None:
    """写入后整表读回：行数一致、内容原样"""
    df = make_stock_df()
    manager.create_table_from_dataframe(df, "stock_price")
    manager.insert_dataframe(df, "stock_price")

    result = manager.read_dataframe("stock_price")
    assert len(result) == 3
    assert list(result["symbol"]) == ["600519"] * 3


def test_create_stock_price_table_schema(manager: DatabaseManager) -> None:
    """显式建表：11 个字段（表结构由代码定义，不依赖读到的第一个 CSV）"""
    manager.create_stock_price_table()

    assert manager.check_table_columns("stock_price") == [
        "id",
        "date",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
        "outstanding_share",
        "turnover",
    ]


def test_drop_table_removes_table(manager: DatabaseManager) -> None:
    """删表之后字段列表为空（drop_table 幂等，表不存在也不报错）"""
    manager.create_stock_price_table()
    manager.drop_table("stock_price")
    manager.drop_table("stock_price")

    assert manager.check_table_columns("stock_price") == []


def test_connect_failure_is_logged_and_raised(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """目录不存在 → 连接失败：记 ERROR 日志，并原样抛出 sqlite3.Error"""
    manager = DatabaseManager(tmp_path / "no_such_dir" / "finance.db")

    with pytest.raises(sqlite3.Error):
        manager.connect()

    assert "连接数据库失败" in caplog.text
