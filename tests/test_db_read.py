from finance_analysis.database.manager import DatabaseManager
from finance_analysis.config import DATABASE_PATH

db = DatabaseManager(
    DATABASE_PATH
)

df = db.read_dataframe("stock_price")

print(df.head())
print()
print(df.shape)
