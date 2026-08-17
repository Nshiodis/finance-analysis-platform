from finance_analysis.database.loader import DatabaseLoader
from finance_analysis.database.manager import DatabaseManager
from finance_analysis.config import DATA_PATH, DATABASE_PATH

db = DatabaseManager(
    DATABASE_PATH
)



loader = DatabaseLoader(db)

loader.load_stock_csv(
    file_path = DATA_PATH / "300750.csv",
    table_name = "stock_price"
)

print("CSV导入成功")
