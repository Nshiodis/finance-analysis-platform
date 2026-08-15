from finance_analysis.database.manager import DatabaseManager


class StockRepository:
    """股票数据仓库"""

    def __init__(self, db_path):

        self.db = DatabaseManager(
            db_path
        )


    def get_stock(
            self,
            symbol: str
    ):
        """
        根据股票代码获取股票数据
        """

        return self.db.query_stock(symbol)
