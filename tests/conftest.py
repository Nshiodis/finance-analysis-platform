from collections.abc import Iterator

import pytest

from finance_analysis.config import settings
from finance_analysis.database.loader import DatabaseLoader
from finance_analysis.database.manager import DatabaseManager


@pytest.fixture(scope="session", autouse=True)
def isolated_database(tmp_path_factory: pytest.TempPathFactory) -> Iterator[None]:
    """每个 pytest 会话用独立临时数据库，绝不碰开发库 database/finance.db"""
    db_path = tmp_path_factory.mktemp("api_db") / "finance.db"

    # 用真实 CSV 把临时库灌成和开发库一样的内容（数据同源，断言不用改）
    db = DatabaseManager(db_path)
    loader = DatabaseLoader(db)
    for csv_name in ("600519.csv", "000858.csv"):
        loader.load_stock_csv(settings.data_path / csv_name, "stock_price")

    # 把配置指到临时库，测试结束后恢复
    original = settings.database_path
    settings.database_path = db_path
    yield
    settings.database_path = original   