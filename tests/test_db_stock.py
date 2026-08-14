from finance_analysis.data.stock_data import StockData
from finance_analysis.data.stock_pool import StockPool


# stock = StockData.from_database("600519")

# # print(stock.df.head())

# stock.calculate_return()

# print(stock.df.head())


pool = StockPool.from_database(
    ["600519", "300750"]
)

print(len(pool.stocks))

pool.set_index()

pool.calculate_returns()

print(
    pool.compare_risk()
)