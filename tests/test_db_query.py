from finance_analysis.database.manager import DatabaseManager
from finance_analysis.config import DATABASE_PATH

db = DatabaseManager(
    DATABASE_PATH
)

df =db.query_stock(
    symbol="600519",
    table_name = "stock_price"
)

print(df.head())
