from finance_analysis.database.database_loader import DatabaseLoader
from finance_analysis.database.database_manager import DatabaseManager
from finance_analysis.utils.utils import get_data_path, get_database_path

db = DatabaseManager(
    get_database_path() / "finance.db"
)

loader = DatabaseLoader(db)

loader.load_stock_csv(
    file_path = get_data_path() / "300750.csv",
    table_name = "stock_price"
)

print("CSV导入成功")
