import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

output_path = Path(__file__).resolve().parent.parent / "output"
output_path.mkdir(exist_ok=True)

# ========================
# 读取数据
# ========================

data_path = Path(__file__).resolve().parent.parent / "data"
file_path = data_path / "stock_data_cleaned.csv"

df = pd.read_csv(file_path)
print(df.head())

# ========================
# 数据统计
# ========================

print(df.describe())

print(f"平均价格: {df['price'].mean()}")
print(f"最高价格：{df['price'].max()}")
print(f"最低价格：{df['price'].min()}")
print(f"交易总量: {df['volume'].sum()}")

# ========================
# 统计分类数据
# ========================

print(df['sector'].value_counts())

# ========================
# 绘制折线图
# ========================

plt.figure(figsize=(10, 6))
plt.plot(df['date'], df['price'], marker='o', linestyle='-', color='b')
# 可以简写为 'bo-'，表示蓝色圆点实线
plt.title("Price Trend")
plt.xlabel("Date")
plt.ylabel("Price")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
# 保存图片
plt.savefig(
    output_path / "price_trend.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()
plt.close()

# ========================
# 绘制柱状图
# ========================

plt.figure(figsize=(10, 6))
sector_counts = df['sector'].value_counts()
plt.bar(sector_counts.index, sector_counts.values)
plt.title("Sector Distribution")
plt.xlabel("Sector")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
# 保存图片
plt.savefig(
    output_path / "sector_distribution.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()
plt.close()

# ========================
# 绘制直方图
# ========================

plt.figure(figsize=(10, 6))
plt.hist(df['price'], bins=8, color='skyblue', edgecolor='black')
plt.title("Price Distribution")
plt.xlabel("Price")
plt.ylabel("Frequency")
# 保存图片
plt.savefig(
    output_path / "price_distribution.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()
plt.close()