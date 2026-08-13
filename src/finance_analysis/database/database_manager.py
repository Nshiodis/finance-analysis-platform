import sqlite3
import pandas as pd


class DatabaseManager:
    """SQLite数据库管理器类"""

    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        """创建数据库连接"""
        return sqlite3.connect(self.db_path)

    def create_table_from_dataframe(
        self,
        df,
        table_name
    ):
        """
        根据DataFrame自动创建数据表，并根据symbol和date字段创建唯一索引

        Parameters
        ----------
        df:
            pandas DataFrame

        table_name:
            数据库表名
        """

        conn = self.connect()

        cursor = conn.cursor()

        columns = []

        for col in df.columns:

            if col in ["open", "high", "low", "close"]:
                dtype = "REAL"
            elif col == "volume":
                dtype = "INTEGER"
            else:
                dtype = "TEXT"
                
            columns.append(f"{col} {dtype}")

        columns.append(
            "UNIQUE(symbol, date)"
        )

        sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name}
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {",".join(columns)}
        )
        """

        cursor.execute(sql)

        conn.commit()

        conn.close()


    def insert_dataframe(
        self,
        df,
        table_name,
        ignore_duplicates=False
    ):
        """
        将 DataFrame 插入数据库

        Parameters
        ----------
        df:
            pandas DataFrame

        table_name:
            数据库表名

        ignore_duplicates:
            是否忽略重复数据
        """

        conn = self.connect()

        if not ignore_duplicates:

            df.to_sql(
                table_name,
                conn,
                if_exists="append",
                index=False
            )

        else:

            columns = ", ".join(
                f'"{column}"'
                for column in df.columns
            )

            placeholders = ", ".join(
                "?"
                for _ in df.columns
            )

            sql = f"""
            INSERT OR IGNORE INTO "{table_name}"
            ({columns})
            VALUES ({placeholders})
            """

            conn.executemany(
                sql,
                df.itertuples(
                    index=False,
                    name=None
                )
            )

        conn.commit()
        conn.close()


    def execute_query(
            self,
            sql
    ):
        """
        执行 SQL 查询并返回结果

        Parameters
        ----------
        sql : str
            SQL 查询语句

        Returns
        -------
        pandas.DataFrame
            查询结果
        """

        conn = self.connect()

        df = pd.read_sql(sql, conn)

        conn.close()

        return df
    

    def query_stock(
        self,
        symbol,
        table_name="stock_price"
):
        """
        根据股票代码查询股票数据

        Parameters
        ----------
        symbol:
            股票代码

        table_name:
            数据表名

        Returns
        -------
        DataFrame
        """

        conn = self.connect()


        sql = f"""
        SELECT *
        FROM {table_name}
        WHERE symbol = ?
        """


        df = pd.read_sql(
            sql,
            conn,
            params=(symbol,)
        )


        conn.close()


        return df
    
    def check_table_columns(
            self,
            table_name
    ):
        """
        查看表字段
        """

        conn =self.connect()

        cursor = conn.cursor()

        cursor.execute(
            f"PRAGMA table_info({table_name})"
        )

        columns = [
            row[1]
            for row in cursor.fetchall()
        ]

        conn.close()

        return columns

    def drop_table(self, table_name):
        """
        删除数据表
        """

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute(
            f'DROP TABLE IF EXISTS "{table_name}"'
        )

        conn.commit()

        conn.close()


    def create_unique_index(
            self,
            table_name,
            columns
    ):
        """
        创建唯一索引

        Parameters
        ----------
        table_name:
            数据表名

        columns:
            参与唯一约束的字段
        """

        conn = self.connect()

        cursor = conn.cursor()

        index_name = f"idx_{table_name}_{'_'.join(columns)}"

        column_sql = ", ".join(columns)

        sql = f"""
        CREATE UNIQUE INDEX IF NOT EXISTS "{index_name}"
        ON "{table_name}" ({column_sql})
        """

        cursor.execute(sql)

        conn.commit()

        conn.close()


    def read_dataframe(self, table_name):
        """
        从数据库读取数据并转换为 DataFrame

        Parameters
        ----------
        table_name:
            数据库表名

        Returns
        -------
        pandas.DataFrame
        """

        conn = self.connect()

        df = pd.read_sql(
            f'SELECT * FROM "{table_name}"',
            conn
        )

        conn.close()

        return df