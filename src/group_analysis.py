import pandas as pd
from pathlib import Path

data_path = Path(__file__).resolve().parent.parent / "data"
file_path = data_path / "stock_data_cleaned.csv"

df = pd.read_csv(file_path)

print(df.head())

# ========================
print("\n每个行业平均价格: ")
# ========================
print(df.groupby('sector')['price'].mean())

# ========================
print("\n每个行业总交易量: ")
# ========================
print(df.groupby('sector')['volume'].sum())

# ========================
print("\n一次统计多个指标: ")
# ========================
result = df.groupby("sector").agg(
    avg_price=("price", "mean"),
    max_price=("price", "max"),
    min_price=("price", "min"),
    total_volume=("volume", "sum")
).reset_index()
# result = df.groupby('sector').agg({
#     'price': ['mean', 'max', 'min'],
#     'volume': 'sum'
# }).reset_index()

print(result)

# ========================
print("\n按平均价格排序: ")
# ========================
result_sorted = result.sort_values(
    by='avg_price',
    ascending=False
)

# ========================
print("\n只显示前三列:")
# ========================
print(result_sorted[[
    "sector",
    "avg_price",
    "total_volume"
]])