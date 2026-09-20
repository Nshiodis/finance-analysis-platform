from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from finance_analysis.database.manager import DatabaseManager
from finance_analysis.exceptions import DatabaseError
from finance_analysis.repository.stock_repository import StockRepository


def make_stock_df(symbol: str = "600519", n: int = 5) -> pd.DataFrame:
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
def db_path(tmp_path: Path) -> str:
    """临时库里建好 stock_price 表并插入两只股票"""
    path = str(tmp_path / "stock.db")
    db = DatabaseManager(path)
    df = pd.concat(
        [make_stock_df("600519"), make_stock_df("000858")],
        ignore_index=True,
    )
    db.create_table_from_dataframe(df, "stock_price")
    db.insert_dataframe(df, "stock_price")
    return path


def test_get_stock(db_path: str) -> None:
    """正常查询：返回该股票全部行"""
    repo = StockRepository(db_path)
    df = repo.get_stock("600519")
    assert len(df) == 5
    assert df["symbol"].iloc[0] == "600519"


def test_get_stock_empty(db_path: str) -> None:
    """不存在的 symbol → 空表（注意：仓库不判空，这是 Service 的事）"""
    repo = StockRepository(db_path)
    assert repo.get_stock("999999").empty


def test_get_stock_date_range(db_path: str) -> None:
    """start/end 过滤：1月2日到1月3日 → 2 行"""
    repo = StockRepository(db_path)
    df = repo.get_stock("600519", start=date(2024, 1, 2), end=date(2024, 1, 3))
    assert len(df) == 2


def test_get_all_symbols(db_path: str) -> None:
    """符号列表去重且排序"""
    repo = StockRepository(db_path)
    assert repo.get_all_symbols() == ["000858", "600519"]


def test_database_error_wrapped(db_path: str) -> None:
    """表被删后查询 → sqlite3.Error 被包装成 DatabaseError（Day26 的纪律）"""
    repo = StockRepository(db_path)
    repo.db.drop_table("stock_price")
    with pytest.raises(DatabaseError):
        repo.get_stock("600519")


def test_get_all_symbols_database_error_wrapped(db_path: str) -> None:
    """取符号列表同样翻译异常：表被删 → DatabaseError"""
    repo = StockRepository(db_path)
    repo.db.drop_table("stock_price")
    with pytest.raises(DatabaseError):
        repo.get_all_symbols()
