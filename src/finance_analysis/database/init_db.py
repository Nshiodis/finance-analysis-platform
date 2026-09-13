"""容器启动时确保数据库存在，并用 data/ 下的 CSV 灌库。"""
from pathlib import Path

from finance_analysis.config import settings
from finance_analysis.database.loader import DatabaseLoader
from finance_analysis.database.manager import DatabaseManager


def init_database() -> None:
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    manager = DatabaseManager(db_path)
    manager.create_stock_price_table()
    loader = DatabaseLoader(manager)

    for csv_file in sorted(Path(settings.data_path).glob("*.csv")):
        loader.load_stock_csv(csv_file, table_name="stock_price")


if __name__ == "__main__":
    init_database()