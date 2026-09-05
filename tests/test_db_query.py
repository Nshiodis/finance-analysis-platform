from finance_analysis.database.manager import DatabaseManager
from finance_analysis.config import settings

db = DatabaseManager(
    settings.database_path
)

df =db.query_stock(
    symbol="600519",
    table_name = "stock_price"
)

print(df.head())
