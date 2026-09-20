import logging
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import pandas as pd


logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite 数据库管理器：负责连接、建表、查询、写入"""

    def __init__(self, db_path: str | Path):
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        """创建一个数据库连接（调用方负责关闭，日常请用 _connect()）"""
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as exc:
            logger.error("连接数据库失败：%s", exc)
            raise

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection]:
        """
        连接上下文管理器：离开 with 时必定关闭连接。

        sqlite3 自带的 `with conn:` 只管事务提交/回滚，不会关闭连接，
        所以这里自己包一层 finally，保证异常路径也不泄漏。
        """
        conn = self.connect()
        try:
            yield conn
        finally:
            conn.close()

    def create_table_from_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
    ) -> None:
        """
        根据 DataFrame 的列自动建表（列类型按粗略规则映射），并加 UNIQUE(symbol, date)

        Parameters
        ----------
        df:
            pandas DataFrame
        table_name:
            数据库表名
        """
        columns: list[str] = []

        for col in df.columns:
            if col in ["open", "high", "low", "close"]:
                dtype = "REAL"
            elif col == "volume":
                dtype = "INTEGER"
            else:
                dtype = "TEXT"

            columns.append(f"{col} {dtype}")

        columns.append("UNIQUE(symbol, date)")

        sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name}
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {",".join(columns)}
        )
        """

        with self._connect() as conn:
            conn.cursor().execute(sql)
            conn.commit()

    def insert_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        ignore_duplicates: bool = False,
    ) -> None:
        """
        把 DataFrame 写入数据库

        Parameters
        ----------
        df:
            pandas DataFrame
        table_name:
            数据库表名
        ignore_duplicates:
            是否忽略重复数据（True 时走 INSERT OR IGNORE，靠 UNIQUE 约束去重）
        """
        with self._connect() as conn:
            if not ignore_duplicates:
                df.to_sql(
                    table_name,
                    conn,
                    if_exists="append",
                    index=False,
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
                    df.itertuples(index=False, name=None),
                )

            conn.commit()

    def execute_query(self, sql: str) -> pd.DataFrame:
        """
        执行 SQL 查询并返回结果

        Parameters
        ----------
        sql:
            SQL 查询语句
        """
        with self._connect() as conn:
            return pd.read_sql(sql, conn)

    def query_stock(
        self,
        symbol: str,
        start: date | None = None,
        end: date | None = None,
        table_name: str = "stock_price",
    ) -> pd.DataFrame:
        """按股票代码查询行情（可选日期区间，按 date 升序）"""
        sql = f"SELECT * FROM {table_name} WHERE symbol = ?"
        params = [symbol]

        if start is not None:
            sql += " AND date >= ?"
            params.append(start.isoformat())

        if end is not None:
            sql += " AND date <= ?"
            params.append(end.isoformat())

        sql += " ORDER BY date"

        with self._connect() as conn:
            return pd.read_sql(sql, conn, params=params)

    def check_table_columns(self, table_name: str) -> list[str]:
        """查看表的字段名"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            return [row[1] for row in cursor.fetchall()]

    def drop_table(self, table_name: str) -> None:
        """删除数据表（不存在也不报错）"""
        with self._connect() as conn:
            conn.cursor().execute(f'DROP TABLE IF EXISTS "{table_name}"')
            conn.commit()

    def read_dataframe(self, table_name: str) -> pd.DataFrame:
        """读取整张表并转换为 DataFrame"""
        with self._connect() as conn:
            return pd.read_sql(f'SELECT * FROM "{table_name}"', conn)

    def query_symbols(self, table_name: str = "stock_price") -> list[str]:
        """查询所有股票代码（去重、升序）"""
        sql = f"SELECT DISTINCT symbol FROM {table_name} ORDER BY symbol"

        with self._connect() as conn:
            df = pd.read_sql(sql, conn)
            return df["symbol"].tolist()

    def create_portfolio_table(self, table_name: str = "portfolio") -> None:
        """创建组合表（weights 存 JSON 字符串）"""
        with self._connect() as conn:
            conn.cursor().execute(
                f"""
                CREATE TABLE IF NOT EXISTS "{table_name}"
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    weights TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def insert_portfolio(
        self,
        weights_json: str,
        created_at: str,
        table_name: str = "portfolio",
    ) -> int:
        """插入一条组合，返回自增 id"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f'INSERT INTO "{table_name}" (weights, created_at) VALUES (?, ?)',
                (weights_json, created_at),
            )
            conn.commit()
            portfolio_id = cursor.lastrowid
            assert portfolio_id is not None
            return portfolio_id

    def query_portfolio(
        self,
        portfolio_id: int,
        table_name: str = "portfolio",
    ) -> pd.DataFrame:
        """按 id 查询组合，返回 DataFrame（不存在则返回空表）"""
        with self._connect() as conn:
            return pd.read_sql(
                f'SELECT * FROM "{table_name}" WHERE id = ?',
                conn,
                params=(portfolio_id,),
            )

    def create_stock_price_table(self, table_name: str = "stock_price") -> None:
        """创建股票行情表（显式声明表结构，不依赖读到的第一个 CSV）"""
        with self._connect() as conn:
            conn.cursor().execute(
                f"""
                CREATE TABLE IF NOT EXISTS "{table_name}"
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    amount TEXT,
                    outstanding_share TEXT,
                    turnover TEXT,
                    UNIQUE(symbol, date)
                )
                """
            )
            conn.commit()
