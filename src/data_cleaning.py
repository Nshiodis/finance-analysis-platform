import pandas as pd
from pathlib import Path

# =========================
# 读取数据
# =========================
data_path = Path(__file__).resolve().parent.parent / "data"
input_file = data_path / "stock_data.csv"

df = pd.read_csv(input_file)

print("\n========== 原始数据 ==========")
print(df.head())

# =========================
# 查看数据基本情况
# =========================
print("\n========== 数据基本信息 ==========")
df.info()

print("\n========== 描述性统计 ==========")
print(df.describe(include="all"))

print("\n========== 缺失值统计 ==========")
print(df.isnull().sum())

# =========================
# 删除重复数据
# =========================
print("\n========== 删除重复数据 ==========")

print(f"删除前数据行数：{df.shape[0]}")

df = df.drop_duplicates()

print(f"删除后数据行数：{df.shape[0]}")

# =========================
# 数据类型转换
# =========================
print("\n========== 数据类型转换 ==========")

# 转为数值类型，无法转换的数据变为 NaN
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

print(df.dtypes)

# =========================
# 处理缺失值
# =========================
print("\n========== 处理缺失值 ==========")

# price 使用平均值填充
df["price"] = df["price"].fillna(df["price"].mean())

# volume 使用中位数填充
df["volume"] = df["volume"].fillna(df["volume"].median())

# sector 缺失填 Unknown（虽然目前没有，但保留处理逻辑）
df["sector"] = df["sector"].fillna("Unknown")

# market 缺失填 Unknown
df["market"] = df["market"].fillna("Unknown")

# stock 缺失填 Unknown
df["stock"] = df["stock"].fillna("Unknown")

# =========================
# 修改数据类型
# =========================
print("\n========== 修改数据类型 ==========")

df["volume"] = df["volume"].astype(int)

# 日期转换为 datetime 类型
df["date"] = pd.to_datetime(df["date"])

print(df.dtypes)

# =========================
# 排序
# =========================
print("\n========== 按日期排序 ==========")

df = df.sort_values(by="date")

# =========================
# 清洗结果
# =========================
print("\n========== 清洗后的数据 ==========")

print(df.head())

print("\n========== 清洗后缺失值 ==========")

print(df.isnull().sum())

print("\n========== 最终数据规模 ==========")

print(df.shape)

# =========================
# 保存数据
# =========================
output_file = data_path / "stock_data_cleaned.csv"

df.to_csv(output_file, index=False)

print("\n========== 数据清洗完成 ==========")
print(f"文件已保存至：{output_file}")