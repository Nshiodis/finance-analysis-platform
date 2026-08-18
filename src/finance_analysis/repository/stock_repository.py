from datetime import date
import sqlite3

from finance_analysis.database.manager import DatabaseManager
from finance_analysis.exceptions import DatabaseError


class StockRepository:
    """股票数据仓库"""

    def __init__(self, db_path):

        self.db = DatabaseManager(
            db_path
        )


    def get_stock(
            self,
            symbol: str,
            start: date | None = None,
            end: date | None = None,
    ):
        """
        根据股票代码获取股票数据
        """
        try:
            return self.db.query_stock(symbol, start, end)
        except sqlite3.Error as exc:
            raise DatabaseError("数据库查询失败") from exc
        
