import logging
from datetime import date
import sqlite3
from pathlib import Path

import pandas as pd

from finance_analysis.database.manager import DatabaseManager
from finance_analysis.exceptions import DatabaseError


logger = logging.getLogger(__name__)


class StockRepository:
    """股票数据仓库"""

    def __init__(self, db_path: str | Path):

        self.db = DatabaseManager(
            db_path
        )


    def get_stock(
            self,
            symbol: str,
            start: date | None = None,
            end: date | None = None,
    ) -> pd.DataFrame:
        """
        根据股票代码获取股票数据
        """
        try:
            return self.db.query_stock(symbol, start, end)
        except (sqlite3.Error, pd.errors.DatabaseError) as exc:
            logger.error("查询股票 %s 失败：%s", symbol, exc)
            raise DatabaseError("数据库查询失败") from exc


    def get_all_symbols(self) -> list[str]:
        """
        获取所有股票代码
        """
        try:
            return self.db.query_symbols()
        except (sqlite3.Error, pd.errors.DatabaseError) as exc:
            logger.error("查询股票列表失败：%s", exc)
            raise DatabaseError("数据库查询失败") from exc
