import pandas as pd
from pathlib import Path

# 读取 CSV 文件
data_path = Path(__file__).resolve().parent.parent / "data"
file_path = data_path / "test.csv"
df = pd.read_csv(file_path)

# 查看数据
print("\n=== 查看数据 ===")
print("\n列名:")
print(df.columns)

print("\n数据形状:")
print(df.shape)

print("\n数据类型:")
print(df.dtypes)

# 选择列
print("\n=== 选择列 ===")
print("\n单列:")
print(df["price"])

print("\n多列:")
print(df[["price", "volume"]])

# 选择行
print("\n=== 选择行 ===")
print("\n单行:")
print(df.iloc[0])

print("\n多行:")
print(df.iloc[0:2])

print("\n通过标签选择行:")
print(df.loc[0])

print("\n条件筛选:")
high_price = df["price"] > 101
print(df.loc[high_price])

# 新增一列
print("\n=== 新增一列 ===")
df["amount"] = df["price"] * df["volume"]
df["high_price"] = df["price"] > 101

# 价格上涨了多少（与100相比）
df["price_change"] = df["price"] - 100

print(df)

# 查看缺失值
print("\n=== 查看缺失值 ===")
print("\n每列缺失值数量:")
print(df.isnull().sum())

print("\n筛选后的数据:")
print(df[
    ((df["price"] >= 101) & (df["volume"] >= 1000))
    | df["high_price"]
])