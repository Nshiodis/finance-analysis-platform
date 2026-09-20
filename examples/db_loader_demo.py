from finance_analysis.database.loader import DatabaseLoader
from finance_analysis.database.manager import DatabaseManager
from finance_analysis.config import settings

db = DatabaseManager(
    settings.database_path
)



loader = DatabaseLoader(db)

loader.load_stock_csv(
    file_path = settings.data_path / "300750.csv",
    table_name = "stock_price"
)

print("CSV导入成功")
