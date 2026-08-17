import pandas as pd
from finance_analysis.config import DATABASE_PATH
from finance_analysis.database.manager import DatabaseManager


# 创建数据库对象

db = DatabaseManager(
    DATABASE_PATH
)

# 模拟股票数据

df = pd.DataFrame(
    {
        "symbol": [
            "600519",
            "600519"
        ],

        "date": [
            "2025-01-01",
            "2025-01-02"
        ],

        "open": [
            1500,
            1510
        ],

        "high": [
            1520,
            1530
        ],

        "low": [
            1490,
            1500
        ],

        "close": [
            1510,
            1520
        ],

        "volume": [
            10000,
            12000
        ]
    }
)

# 自动创建表

db.create_table_from_dataframe(
    df,
    "test_stock_price"
)


# 插入数据

db.insert_dataframe(
    df,
    "test_stock_price"
)


# 查询

result = db.execute_query(
    """
    SELECT *
    FROM test_stock_price
    """
)

print(result)


# 查看表字段

columns = db.check_table_columns(
    "test_stock_price"
)

print(columns)
