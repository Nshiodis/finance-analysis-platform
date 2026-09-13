"""回归测试：容器启动时的建表逻辑不能依赖 CSV 的读取顺序。

背景（Day33 踩的坑）：
``data/000300.csv`` 只有 7 列（没有 outstanding_share / turnover），
另外三个 CSV 有 9 列。旧逻辑是"拿读到的第一个 CSV 建表"，
而 ``init_database()`` 按文件名排序读 CSV，容器里第一个恰好是 000300.csv，
于是表被建成 7 列，再灌 600519.csv 就抛：

    sqlite3.OperationalError: table stock_price has no column named outstanding_share

本机之所以一直没炸，是因为 ``tests/conftest.py`` 只灌 600519.csv / 000858.csv
（都是 9 列）——典型的"依赖巧合"。这个文件把"表结构由代码显式定义"焊死。
"""

from pathlib import Path

import pytest

from finance_analysis.config import settings
from finance_analysis.database.init_db import init_database
from finance_analysis.database.manager import DatabaseManager


def count_rows(manager: DatabaseManager, sql: str) -> int:
    """跑一条 COUNT 查询并返回整数（断言里不出现 DataFrame 取值细节）"""
    df = manager.execute_query(sql)
    return int(df["n"].iloc[0])


def test_schema_does_not_depend_on_csv_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """000300.csv（7 列）排在最前，表结构依然完整"""
    db_path = tmp_path / "finance.db"
    monkeypatch.setattr(settings, "database_path", db_path)

    init_database()

    manager = DatabaseManager(db_path)
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

    # 列少的 CSV 也能灌：缺的列在库里是 NULL
    rows_000300 = count_rows(
        manager,
        "SELECT COUNT(*) AS n FROM stock_price WHERE symbol = '000300'",
    )
    assert rows_000300 > 0
    assert (
        count_rows(
            manager,
            "SELECT COUNT(*) AS n FROM stock_price "
            "WHERE symbol = '000300' AND outstanding_share IS NULL",
        )
        == rows_000300
    )

    # 列多的 CSV 数据完整，不是被静默丢成 NULL
    rows_600519 = count_rows(
        manager,
        "SELECT COUNT(*) AS n FROM stock_price WHERE symbol = '600519'",
    )
    assert rows_600519 > 0
    assert (
        count_rows(
            manager,
            "SELECT COUNT(*) AS n FROM stock_price "
            "WHERE symbol = '600519' AND outstanding_share IS NOT NULL",
        )
        == rows_600519
    )


def test_init_database_is_idempotent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """容器每次启动都会跑 init_database()：重复执行不报错、不灌重复数据"""
    db_path = tmp_path / "finance.db"
    monkeypatch.setattr(settings, "database_path", db_path)

    init_database()
    first_run = count_rows(DatabaseManager(db_path), "SELECT COUNT(*) AS n FROM stock_price")

    init_database()
    second_run = count_rows(DatabaseManager(db_path), "SELECT COUNT(*) AS n FROM stock_price")

    assert first_run > 0
    assert second_run == first_run
