from finance_analysis.database.database_manager import DatabaseManager
from finance_analysis.utils.utils import get_database_path

db = DatabaseManager(
    get_database_path()
)

df =db.query_stock(
    symbol="600519",
    table_name = "stock_price"
)

print(df.head())
