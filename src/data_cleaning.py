import pandas as pd
from pathlib import Path

# 读取数据
data_path = Path(__file__).resolve().parent.parent / "data"
file = data_path / "stock_data.csv"

df = pd.read_csv(file)

print("\n=== 查看数据 ===")
print(df.head())

# 查看数据基本情况
print("\n=== 查看数据基本情况 ===")
df.info()
print(df.describe(include="all"))
print(df.isnull().sum())

# 删除重复数据
print("\n=== 删除重复数据 ===")
df = df.drop_duplicates()
print(df.shape)     #查看数据有没有变少

# price 转为数字
print("\n=== price 转为数字 ===")
df["price"] = pd.to_numeric(df["price"], errors="coerce")
print(df.describe(include="all"))

# 处理缺失值
print("\n=== 处理缺失值 ===")
# df = df.dropna()
df["price"] = df["price"].fillna(df["price"].mean())
df["volume"] = df["volume"].fillna(df["volume"].median())
df["sector"] = df["sector"].fillna("Unknown")

# 修改数据类型
print("\n=== 修改数据类型 ===")
df["volume"] = df["volume"].astype(int)
print(df.dtypes)

# 清洗结果
print("\n=== 清洗后的数据 ===")
print(df.head())
print("\n=== 清洗后缺失值 ===")
print(df.isnull().sum())

# 保存清洗后的数据
output = data_path / "stock_data_cleaned.csv"
df.to_csv(output, index=False)
print("\n=== 数据清洗完成，已保存到 stock_data_cleaned.csv ===")