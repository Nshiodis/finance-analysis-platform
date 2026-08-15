import pandas as pd
from pathlib import Path
from finance_analysis.database.manager import DatabaseManager


class DatabaseLoader:
    """
    股票数据导入器
    """

    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager

    def load_stock_csv(
            self,
            file_path,
            table_name
    ):
        """
        CSV导入数据库

        Parameters
        ----------
        file_path:
            CSV文件路径

        table_name:
            数据库表名
        """

        file_path = Path(file_path)

        # 读取CSV
        df = pd.read_csv(file_path)

        # 自动获取股票代码
        symbol = file_path.stem

        # 增加symbol字段
        df["symbol"] = symbol

        # 第一次导入自动建表
        table = self.database_manager.execute_query(
            f"""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name='{table_name}'
            """
        )

        if table.empty:

            self.database_manager.create_table_from_dataframe(
                df,
                table_name
            )


        # 写入数据
        self.database_manager.insert_dataframe(
            df,
            table_name,
            ignore_duplicates=True,
        )
