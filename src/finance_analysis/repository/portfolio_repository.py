import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from finance_analysis.database.manager import DatabaseManager
from finance_analysis.exceptions import DatabaseError



class PortfolioRepository:
    def __init__(self, db_path: str | Path):
        self.db = DatabaseManager(db_path)
        self.db.create_portfolio_table()        # 确保表存在（IF NOT EXISTS，幂等）


    def create_portfolio(self, weights: dict[str, float]) -> int:
        """保存组合，返回自增 id"""
        try:
            weights_json = json.dumps(weights, ensure_ascii=False)
            created_at = datetime.now().isoformat()
            return self.db.insert_portfolio(weights_json, created_at)
        except sqlite3.Error as exc:
            raise DatabaseError("数据库插入失败") from exc

    def get_portfolio(self, portfolio_id: int) -> dict[str, Any] | None:
        """按 id 查询组合；不存在返回 None"""
        try:
            df = self.db.query_portfolio(portfolio_id)
        except sqlite3.Error as exc:
            raise DatabaseError("数据库查询失败") from exc

        if df.empty:
            return None

        row = df.iloc[0]
        return {
            "id": int(row["id"]),
            "weights": json.loads(row["weights"]),
        }
